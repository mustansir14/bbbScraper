from includes.browser.DriverBinary import DriverBinary
from includes.loaders.DisplayLoader import DisplayLoader
from scrape import BBBScraper
from includes.scrapers.SitemapScraper import SitemapScraper
from includes.DB import DB
import logging

logging.basicConfig(handlers=[
    logging.StreamHandler()
], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


def scrapeSitemaps():
    sc = SitemapScraper()
    sc.setDatabase(DB())
    sc.scrape("")


def scrapeNewUrls():
    scraper = BBBScraper()

    companies = scraper.db.queryArray(
        f"SELECT company_id, url from company where status = 'new' order by company_id LIMIT 1000")
    if companies:
        for company in companies:
            try:
                scraper.scrape_url(company['url'], scrape_reviews_and_complaints=True)
            except Exception as e:
                logging.error("scrape_url exception: " + str(e))


def main():
    DriverBinary().getBinary()
    #scrapeSitemaps()
    scrapeNewUrls()


if __name__ == "__main__":
    display = DisplayLoader()

    try:
        display.start()

        main()
    finally:
        display.stop()
