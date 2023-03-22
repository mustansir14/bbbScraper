from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse
import logging
from logging.handlers import RotatingFileHandler

rfh = RotatingFileHandler(
    filename="logs/rescrape_all_from_db.py.log", 
    mode='a',
    maxBytes=20*1024*1024,
    backupCount=1,
    delay=0,
    encoding=None
)
rfh.setFormatter(logging.Formatter('%(asctime)s Process ID %(process)d: %(message)s'))
rfh.setLevel(level=logging.DEBUG)

root = logging.getLogger('root')
root.setLevel(logging.INFO)
root.addHandler(rfh)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument('--logfile', nargs='?', type=str, default=None, help='Path of the file where logs should be written')

    args = parser.parse_args()
    no_of_threads = args.no_of_threads
        
    proxy = getProxy()
    scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'], proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])
    count = 0
    while True:

        companies = scraper.db.queryArray(f"SELECT company_id, url from company order by date_updated LIMIT {count*5000}, 5000;")
        if not companies:
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
                scraper.scrape_url(company_url, scrape_reviews_and_complaints=True)

        count += 1

    scraper.kill_chrome()