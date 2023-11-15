from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse
import logging, sys, time, re
from includes.DB import DB
def scraperUrlsFromQueueIgnoreExceptions(q, scrape_reviews_and_complaints=True, set_rescrape_setting=False):
    scraper = None
    try:
        proxy = getProxy()
        scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'],
                             proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])

        while q.qsize():
            company_url = q.get()

            logging.info("Scrape: " + company_url)

            if "/addressId/" in company_url:
                scraper.db.removeCompanyByUrl(company_url)
                continue

            try:
                scraper.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints,
                                   set_rescrape_setting=set_rescrape_setting)
            except Exception as e:
                logging.info(str(e))
    except:
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument('--logfile', nargs='?', type=str, default=None,
                        help='Path of the file where logs should be written')

    args = parser.parse_args()

    logging.basicConfig(handlers=[
        logging.FileHandler("logs/scrape_with_errors.py.log"),
        logging.StreamHandler()
    ], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

    db = DB()
    count = 0
    while count < 1:
        logging.info("Get companies...")

        companies = db.queryArray(
            f"SELECT company_id, url from company where status = 'error' limit 1000")
        if not companies:
            logging.info('No companies wait hour')
            time.sleep(3600)
            break

        logging.info("Scraping...")

        urls_to_scrape = Queue()

        for company in companies:
            urls_to_scrape.put(company['url'])

        if args.no_of_threads == 1:
            logging.info("Scrape with 1 treads")

            scraper = BBBScraper()

            while urls_to_scrape.qsize():
                company_url = urls_to_scrape.get()

                logging.info("Scrape: " + company_url)

                try:
                    scraper.scrape_url(company_url, scrape_reviews_and_complaints=True,
                                       set_rescrape_setting=False)
                except Exception as e:
                    logging.info(str(e))
        else:
            logging.info("Scrape with treads: " + str(args.no_of_threads))

            processes = []
            for i in range(args.no_of_threads):
                processes.append(Process(target=scraperUrlsFromQueueIgnoreExceptions, args=(urls_to_scrape, True,)))
                processes[i].start()

            try:
                for i in range(args.no_of_threads):
                    processes[i].join()
            except KeyboardInterrupt:
                logging.info("Close queue")
                urls_to_scrape.cancel_join_thread()

        count += 1
