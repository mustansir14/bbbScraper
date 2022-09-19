from scrape import BBBScraper
from config import *
import xml.etree.ElementTree as ET
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
    logging.info("Starting scrape (gathering sitemap urls...)")
    for sitemap_url in sitemap_urls:

        scraper.driver.get(sitemap_url)
        root = ET.fromstring(scraper.driver.page_source)
        urls = []
        for child in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(child.text)
        for url in urls:
            logging.info("Scraping from sitemap " + url + "...")
            scraper.driver.get(url)
            root = ET.fromstring(scraper.driver.page_source)
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
                scraper.db.cur.execute("SELECT company_id from company where url = %s", (company_url, ))
                data = scraper.db.cur.fetchall()
                if len(data) > 0:
                    logging.info("Company " + company_url + " exits. Skipping")
                    continue
                found_url = True
                if platform == "linux" or platform == "linux2":
                    urls_to_scrape.put(company_url)
                else:
                    urls_to_scrape.append(company_url)
            if not found_url:
                continue

            if no_of_threads > 1 and (platform == "linux" or platform == "linux2"):
                processes = []
                for i in range(no_of_threads):
                    processes.append(Process(target=scraper.scrape_urls_from_queue, args=(urls_to_scrape, False, )))
                    processes[i].start()

                for i in range(no_of_threads):
                    processes[i].join()
            else:
                for company_url in urls_to_scrape:
                    scraper.scrape_url(company_url, scrape_reviews_and_complaints=False)