from includes.browser.DriverBinary import DriverBinary
from includes.loaders.DisplayLoader import DisplayLoader
from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse
import logging
from logging.handlers import RotatingFileHandler

root = logging.getLogger('root')
root.setLevel(logging.INFO)
root.addHandler(logging.StreamHandler())


def main(args):
    no_of_threads = args.no_of_threads

    DriverBinary().getBinary()

    scraper = BBBScraper()

    while True:
        fromCompanyId = scraper.db.getSettingInt(scraper.rescrapeSettingKey, 0)

        sql = f"SELECT company_id, url from company where company_id > {fromCompanyId} and status <> 'removed' order by company_id LIMIT " + str(
            no_of_threads) + ";"
        logging.info(sql)

        companies = scraper.db.queryArray(sql)
        if not companies:
            logging.info("No more companies, set from to zero")
            scraper.db.setSetting(scraper.rescrapeSettingKey, 0)
            break

        if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
            urls_to_scrape = Queue()
        else:
            urls_to_scrape = []

        for company in companies:
            logging.info(str(company['company_id']) + ': ' + company['url'])
            if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
                urls_to_scrape.put(company['url'])
            else:
                urls_to_scrape.append(company['url'])

        if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
            processes = []
            for i in range(no_of_threads):
                processes.append(Process(target=scraper.scrape_urls_from_queue, args=(urls_to_scrape, True, True,)))
                processes[i].start()

            for i in range(no_of_threads):
                processes[i].join()
        else:
            for company_url in urls_to_scrape:
                scraper.scrape_url(company_url, scrape_reviews_and_complaints=True, set_rescrape_setting=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument('--logfile', nargs='?', type=str, default=None,
                        help='Path of the file where logs should be written')

    args = parser.parse_args()

    display = DisplayLoader()

    try:
        display.start()

        main(args)
    finally:
        display.stop()
