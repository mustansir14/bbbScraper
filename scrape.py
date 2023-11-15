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

    def loadUrl(self, url):
        for i in range(3):
            if not self.lastValidProxy:
                logging.info("Find proxy...")
                self.lastValidProxy = getProxy()

            logging.info("Create browser")
            self.createBrowser(None, self.lastValidProxy['proxy'], self.lastValidProxy['proxy_port'],
                               self.lastValidProxy['proxy_user'], self.lastValidProxy['proxy_pass'],
                               self.lastValidProxy['proxy_type'])

            try:
                logging.info("Load: " + url)
                self.driver.get(url)
                logging.info("Loaded: SUCCESS")
                return self.driver.page_source
            except Exception as e:
                self.lastValidProxy = None
                logging.error(e)

        raise Exception("Can not create browser")

    def addNewUrls(self):
        sitemap_urls = [
            "https://www.bbb.org/sitemap-accredited-business-profiles-index.xml",
            "https://www.bbb.org/sitemap-business-profiles-index.xml"
        ]

        for sitemap_url in sitemap_urls:
            logging.info("Download root url: " + sitemap_url)
            pageSourceCode = self.loadUrl(sitemap_url)

            childUrls = []
            rootXml = ET.fromstring(pageSourceCode)
            for rootChild in rootXml.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                try:
                    childUrls.append(rootChild.text.strip())
                except Exception as e:
                    logging.error(str(e))

            # need shuffle pages, because may be constant crash on some url, to scrape others do some trick
            random.shuffle(childUrls)

            counter = 0
            for childUrl in childUrls:
                logging.info(str(counter) + "/" + str(len(childUrls)) + ") Download child url: " + childUrl)
                pageSourceCode = self.loadUrl(childUrl)

                childXml = ET.fromstring(pageSourceCode)
                locs = childXml.findall(
                    './/{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')

                stats = {'new': 0, 'passed': 0, 'total': len(locs)}
                statsTime = time.time() + 10

                for child in locs:
                    try:
                        url = child.text.strip()
                    except Exception as e:
                        logging.error(e)
                        logging.info(child)

                        continue

                    if "/profile/" in url:
                        row = self.db.queryRow('select company_id from company where url = ?', (url,))
                        if row is None:
                            company = Company()
                            company.url = url
                            company.name = "no name, need scrape"
                            company.status = "new"

                            self.db.insert_or_update_company(company)

                            stats['new'] = stats['new'] + 1

                    stats['passed'] = stats['passed'] + 1

                    if statsTime < time.time():
                        statsTime = time.time() + 10

                        logging.info(stats)

                logging.info(stats)
                counter = counter + 1

    def bulk_scrape(self, no_of_threads=1, scrape_reviews_and_complaints=True):

        sitemap_urls = ["https://www.bbb.org/sitemap-accredited-business-profiles-index.xml",
                        "https://www.bbb.org/sitemap-business-profiles-index.xml"]
        logging.info("Starting scrape (gathering sitemap urls...)")
        for sitemap_url in sitemap_urls:

            self.driver.get(sitemap_url)
            root = ET.fromstring(self.driver.page_source)
            urls = []
            for child in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                urls.append(child.text)
            for url in urls:
                self.driver.get(url)
                root = ET.fromstring(self.driver.page_source)
                company_urls = []
                for child in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                    child_text = child.text
                    if "profile" in child_text:
                        company_urls.append(child_text)
                if platform == "linux" or platform == "linux2":
                    urls_to_scrape = Queue()
                else:
                    urls_to_scrape = []
                found_url = False
                for company_url in company_urls:
                    found_url = True
                    if platform == "linux" or platform == "linux2":
                        urls_to_scrape.put(company_url)
                    else:
                        urls_to_scrape.append(company_url)
                if not found_url:
                    continue

                if platform == "linux" or platform == "linux2":
                    processes = []
                    for i in range(no_of_threads):
                        processes.append(Process(target=self.scrape_urls_from_queue,
                                                 args=(urls_to_scrape, scrape_reviews_and_complaints,)))
                        processes[i].start()

                    for i in range(no_of_threads):
                        processes[i].join()
                else:
                    for company_url in urls_to_scrape:
                        self.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints)

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
