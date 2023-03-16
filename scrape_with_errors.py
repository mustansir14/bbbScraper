from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse
import logging, sys, time, re




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument('--logfile', nargs='?', type=str, default=None, help='Path of the file where logs should be written')

    args = parser.parse_args()
    no_of_threads = args.no_of_threads
    if args.logfile:
        logging.basicConfig(filename=args.logfile, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    else:
        logging.basicConfig(handlers=[
            logging.FileHandler("logs/scrape_with_errors.py.log"),
            logging.StreamHandler()
        ], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
        
    proxy = getProxy()
    scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'], proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])
    count = 0
    while True:

        companies = scraper.db.queryArray(f"SELECT company_id, url from company where status = 'error' limit 5000")
        if not companies:
            logging.info('No companies wait hour')
            time.sleep(3600)
            break
        
        if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
            urls_to_scrape = Queue()
        else:
            urls_to_scrape = []
            
        for company in companies:
            if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
                urls_to_scrape.put(company['url'])
            else:
                urls_to_scrape.append(company['url'])

        if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
            processes = []
            for i in range(no_of_threads):
                processes.append(Process(target=scraper.scrape_urls_from_queue, args=(urls_to_scrape, True, )))
                processes[i].start()

            for i in range(no_of_threads):
                processes[i].join()
        else:
            for company_url in urls_to_scrape:
                company = scraper.scrape_url(company_url, scrape_reviews_and_complaints=True)
                if company.status != "success":
                    logging.info("Not success exit")
                    sys.exit(1);

        count += 1

    scraper.kill_chrome()