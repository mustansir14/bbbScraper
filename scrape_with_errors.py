from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse
import logging, sys, time, re
from logging.handlers import RotatingFileHandler
from includes.DB import DB

rfh = RotatingFileHandler(
    filename="logs/scrape_with_errors.py.log", 
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

def scraperUrlsFromQueueIgnoreExceptions(q, scrape_reviews_and_complaints=True, set_rescrape_setting = False):
    scraper = None
    try:
        proxy = getProxy()
        scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'], proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])
        
        while q.qsize():
            company_url = q.get()
            
            logging.info("Scrape: " + company_url)
            
            if "/addressId/" in company_url:
                scraper.db.removeCompanyByUrl(company_url)
                continue
                
            try:
                scraper.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints, set_rescrape_setting = set_rescrape_setting)
            except Exception as e:
                logging.info(str(e))
    except:
        pass
    finally:
        if scraper:
            scraper.kill_chrome()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument('--logfile', nargs='?', type=str, default=None, help='Path of the file where logs should be written')

    args = parser.parse_args()
    
    db = DB()
    count = 0
    while count < 1:

        companies = db.queryArray(f"SELECT company_id, url from company where status = 'error' order by date_updated desc limit 5000")
        if not companies:
            logging.info('No companies wait hour')
            time.sleep(3600)
            break
        
        urls_to_scrape = Queue()
            
        for company in companies:
            urls_to_scrape.put(company['url'])

        processes = []
        for i in range(args.no_of_threads):
            processes.append(Process(target=scraperUrlsFromQueueIgnoreExceptions, args=(urls_to_scrape, True, )))
            processes[i].start()

        try:
            for i in range(args.no_of_threads):
                processes[i].join()
        except KeyboardInterrupt:
            logging.info("Close queue")
            urls_to_scrape.cancel_join_thread()
            
        count += 1