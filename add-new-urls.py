from scrape import BBBScraper
from sys import platform
from includes.proxies import getProxy
from multiprocessing import Queue, Process
import argparse, time
import logging

if __name__ == "__main__":
    
    logging.basicConfig(handlers=[
        logging.FileHandler("logs/add-new-urls.py.log"),
        logging.StreamHandler()
    ], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    
    sitemap_urls = ["https://www.bbb.org/sitemap-accredited-business-profiles-index.xml", "https://www.bbb.org/sitemap-business-profiles-index.xml"]
    
    proxy = getProxy()
    scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'], proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])
    
    start = time.time();
    scanAgain = 7200 # every 2 hours
    
    scraper.addNewUrls()
    
    while time.time() - start < scanAgain:
        break
        companies = scraper.db.queryArray(f"SELECT company_id, url from company where status = 'new' LIMIT 1000")
        if not companies:
            break
            
        for company in companies:
            if time.time() - start > scanAgain:
                break
                
            scraper.scrape_url(company['url'], scrape_reviews_and_complaints=True)
    
    if time.time() - start < scanAgain:
        left = scanAgain - (time.time() - start)
        if left < 0:
            left = 0
    
        logging.info("Sleep " + str(left) + " seconds, to get urls again")
        time.sleep(left)