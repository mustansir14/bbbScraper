import time
from typing import Any
from includes.models import Company
from includes.scrapers.AbstractScraper import AbstractScraper
import logging
import xml.etree.ElementTree as ET
import traceback
import random


class SitemapScraper(AbstractScraper):
    def scrapeInternal(self, companyUrl: str) -> Any:
        logging.info("Scrape sitemap")

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

    def loadUrl(self, childUrl) -> str:
        browser = self.getBrowserLoader().loadPage(childUrl)
        return browser.getPageSource() if browser else "";
