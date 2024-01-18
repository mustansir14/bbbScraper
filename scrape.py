##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

import time
from includes.DB import DB
from includes.helpers.CLIArgumentsParserHelper import CLIArgumentsParserHelper
from includes.loaders.DisplayLoader import DisplayLoader
from includes.models import Company
from includes.scrapers.CompanyScraper import CompanyScraper
from includes.scrapers.ComplaintsScraper import ComplaintsScraper
from includes.proxies import getProxy
import xml.etree.ElementTree as ET
import random
import logging
from sys import platform
from multiprocessing import Process, Queue
from includes.scrapers.ReviewsScraper import ReviewsScraper


class BBBScraper:
    db: DB
    rescrapeSettingKey: str

    def __init__(self) -> None:
        self.rescrapeSettingKey = "rescrape_all_from_db.last_company_id";
        self.db = DB()

    def normalizeCompanyUrl(self, companyUrl: str) -> str:
        if "https://www.bbb.org/" not in companyUrl and "profile" not in companyUrl:
            raise Exception("Invalid URL")

        url_split = companyUrl.split("/")
        if url_split[-1] in ["details", "customer-reviews", "complaints"]:
            companyUrl = "/".join(url_split[:-1])

        return companyUrl

    def scrape_url(self, companyUrl, save_to_db=True, scrape_reviews_and_complaints=True,
                   set_rescrape_setting=False) -> Company:

        companyUrl = self.normalizeCompanyUrl(companyUrl)

        # must check this before, because url may be deleted in scrape_company_details
        company_id = self.db.getCompanyIdByUrl(companyUrl)

        company = self.scrape_company_details(
            company_url=companyUrl,
            save_to_db=save_to_db,
            half_scraped=not scrape_reviews_and_complaints
        )

        if company.status == "success":
            if scrape_reviews_and_complaints:
                self.scrape_company_reviews(company_url=company.url, save_to_db=save_to_db)
                self.scrape_company_complaints(company_url=company.url, save_to_db=save_to_db)

        if set_rescrape_setting:
            sql = 'insert into `settings` set `name` = ?, `value` = ? ON DUPLICATE KEY UPDATE `value` = IF(`value` < ?, ?, `value`)'
            args = (self.rescrapeSettingKey, company_id, company_id, company_id,)

            logging.info(sql)
            logging.info(args)

            self.db.execSQL(sql, args)
        else:
            logging.info("Do not update rescrape settings")

        return company

    def scrape_company_details(self, company_url=None, company_id=None, save_to_db=True, half_scraped=False) -> Company:

        if not company_url and not company_id:
            raise Exception("Please provide either company URL or company ID")
        elif company_id:
            row = self.db.queryRow("Select url from company where company_id = %s;", (company_id,))
            if row is not None:
                company_url = row['company_url']
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))

        sc = CompanyScraper()
        sc.setDatabase(self.db)
        company = sc.scrape(company_url)

        return company

    def scrape_company_reviews(self, company_url=None, company_id=None, save_to_db=True,
                               scrape_specific_review=None) -> None:

        if company_url:
            row = self.db.queryRow("select company_id from company where url = ?", (company_url,))
            if row is None:
                self.scrape_company_details(company_url=company_url, save_to_db=True)
                row = self.db.queryRow("select company_id from company where url = ?", (company_url,))
            if row is None:
                return

            company_id = row['company_id']

        elif company_id:
            row = self.db.queryRow("select url from company where company_id = ?", (company_id,))
            if row:
                company_url = row['company_url']
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))
        else:
            raise Exception("Please provide either company URL or company ID")

        sc = ReviewsScraper()
        sc.setDatabase(self.db)
        sc.setCompanyId(company_id)
        sc.scrape(company_url)

    def scrape_company_complaints(self, company_url=None, company_id=None, save_to_db=True,
                                  scrape_specific_complaint=None) -> None:

        if company_url:
            row = self.db.queryRow("Select company_id from company where url = %s;", (company_url,))
            if row is None:
                self.scrape_company_details(company_url=company_url, save_to_db=True)
                row = self.db.queryRow("Select company_id from company where url = %s;", (company_url,))
            if row is None:
                return
            company_id = row["company_id"]

        elif company_id:
            row = self.db.queryRow("Select url from company where company_id = %s;", (company_id,))
            if row:
                company_url = row["company_url"]
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))
        else:
            raise Exception("Please provide either company URL or company ID")

        sc = ComplaintsScraper()
        sc.setDatabase(self.db)
        sc.setCompanyId(company_id)
        sc.scrape(company_url)

    def scrape_urls_from_queue(self, q, scrape_reviews_and_complaints=True, set_rescrape_setting=False):

        try:
            scraper = BBBScraper()

            while q.qsize():
                company_url = q.get()
                scraper.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints,
                                   set_rescrape_setting=set_rescrape_setting)

        except:
            pass

    def _get_first_with_text(self, elements, get_href=False):
        for element in elements:
            elem_text = element.text.strip()
            if elem_text != "":
                if get_href:
                    return element.get_attribute("href")
                return elem_text
        return None


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


def main(args):
    # setup logging based on arguments

    if args.proxy:
        logging.info("Try use proxy: " + args.proxy)

    scraper = BBBScraper()

    if args.urls_from_file is not None:
        lines = open(args.urls_from_file).readlines()
        lines = map(lambda x: x.strip(), lines)
        lines = list(filter(None, lines))

        if args.urls is None:
            args.urls = []

        for line in lines:
            args.urls.append(line)

    for url in args.urls:
        logging.info("Scraping url: " + url)

        company = scraper.scrape_company_details(company_url=url, save_to_db=str2bool(args.save_to_db))

        if company.status == "success":
            scraper.scrape_company_reviews(company_url=company.url, save_to_db=str2bool(args.save_to_db))
            scraper.scrape_company_complaints(company_url=company.url, save_to_db=str2bool(args.save_to_db))

            logging.info("Complaints and reviews scraped successfully.\n")


if __name__ == '__main__':
    logging.basicConfig(handlers=[
        logging.FileHandler("logs/scrape.py.log"),
        logging.StreamHandler()
    ], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

    args = CLIArgumentsParserHelper.get()
    display = DisplayLoader()

    try:
        display.start()

        main(args)
    finally:
        display.stop()
