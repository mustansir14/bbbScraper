from scrape import BBBScraper
from config import *
from sys import platform
from multiprocessing import Queue, Process
import argparse
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")

    args = parser.parse_args()
    no_of_threads = args.no_of_threads

    sitemap_urls = ["https://www.bbb.org/sitemap-accredited-business-profiles-index.xml", "https://www.bbb.org/sitemap-business-profiles-index.xml"]
    scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS, proxy_type=PROXY_TYPE)
    count = 0
    while True:

        scraper.db.cur.execute(f"SELECT company_id, url from company LIMIT {count*5000}, 5000;")
        companies = scraper.db.cur.fetchall()
        if not companies:
            break
        
        if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
            urls_to_scrape = Queue()
        else:
            urls_to_scrape = []
        for company_id, company_url in companies:       
            if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
                urls_to_scrape.put(company_url)
            else:
                urls_to_scrape.append(company_url)

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