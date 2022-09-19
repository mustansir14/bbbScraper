##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
from typing import List
from includes.DB import DB
from includes.models import Company, Complaint, Review
from config import *
import xml.etree.ElementTree as ET
import datetime
import os
import argparse
import sys
import logging, zipfile
from pyvirtualdisplay import Display
from sys import platform
from multiprocessing import Process, Queue
from includes.telegram_reporter import send_message


class BBBScraper():

    def __init__(self, chromedriver_path=None, proxy=None, proxy_port=None, proxy_user=None, proxy_pass=None, proxy_type="http") -> None:
        
        self.session = requests.session()
        headers = {
            "authority": "www.bbb.org",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "sec-ch-ua": "^\^Google"
            }
        self.session.headers.update(headers)
        options = Options()
        options.add_argument("window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--single-process'); # one process to take less memory
        options.add_argument('--renderer-process-limit=1'); # do not allow take more resources
        options.add_argument('--disable-crash-reporter'); # disable crash reporter process
        options.add_argument('--no-zygote'); # disable zygote process
        options.add_argument('--disable-crashpad')
        options.add_argument('--grabber-bbb-mustansir')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
        if proxy:
            if not proxy_port:
                raise Exception("Proxy Port missing.")
            if proxy_user and proxy_pass:
                self.session.proxies.update({PROXY_TYPE: PROXY_TYPE + "://" + PROXY_USER + ":" + PROXY_PASS + "@" + PROXY + ":" + str(PROXY_PORT)})
                manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "<all_urls>",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    },
                    "minimum_chrome_version":"22.0.0"
                }
                """

                background_js = """
                var config = {
                        mode: "fixed_servers",
                        rules: {
                        singleProxy: {
                            scheme: "%s",
                            host: "%s",
                            port: parseInt(%s)
                        },
                        bypassList: ["localhost"]
                        }
                    };

                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "%s",
                            password: "%s"
                        }
                    };
                }

                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                """ % (proxy_type, proxy, proxy_port, proxy_user, proxy_pass)
                pluginfile = 'temp/proxy_auth_plugin.zip'
                if not os.path.isdir("temp"):
                    os.mkdir("temp")
                with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                options.add_extension(pluginfile)
            else:
                self.session.proxies.update({PROXY_TYPE: PROXY_TYPE + "://" + PROXY + ":" + PROXY_PORT})
                options.add_argument("--proxy-server=%s" % proxy_type + "://" + proxy + ":" + proxy_port)
        if os.name != "nt":
            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()
        if chromedriver_path:
            self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        else:
            self.driver = webdriver.Chrome(options=options, executable_path=ChromeDriverManager().install())
        if not os.path.exists("file/logo/"):
            os.makedirs("file/logo")
        self.db = DB()


    def scrape_url(self, url, save_to_db=True, scrape_reviews_and_complaints=True) -> Company:
        
        if "https://www.bbb.org/" not in url and "profile" not in url:
            raise Exception("Invalid URL")
        url_split = url.split("/")
        if url_split[-1] in ["details", "customer-reviews", "complaints"]:
            url = "/".join(url_split[:-1]) 
        company = self.scrape_company_details(company_url=url, save_to_db=save_to_db, half_scraped= not scrape_reviews_and_complaints)
        if scrape_reviews_and_complaints:
            company.reviews = self.scrape_company_reviews(company_url=url, save_to_db=save_to_db)
            company.complaints = self.scrape_company_complaints(company_url=url, save_to_db=save_to_db)
        return company


    def scrape_company_details(self, company_url=None, company_id=None, save_to_db=True, half_scraped=False) -> Company:

        if not company_url and not company_id:
            raise Exception("Please provide either company URL or company ID")
        elif company_id:
            self.db.cur.execute("Select url from company where company_id = %s;", (company_id, ))
            fetched_results = self.db.cur.fetchall()
            if len(fetched_results) == 1:
                if USE_MARIA_DB:
                    company_url = fetched_results[0][0]
                else:
                    company_url = fetched_results[0]["company_url"]
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))
            
        logging.info("Scraping Company Details for " + company_url)
        company = Company()
        company.url = company_url
        company.half_scraped = half_scraped
        self.driver.get(company_url)
        try:
            company.name = self.driver.find_element_by_class_name("MuiTypography-root.MuiTypography-h2").text.strip()
        except:
            logging.error("Error in scraping: " + company_url + " Page Broken (502)")
            company.name = company_url
            company.status = "error"
            company.log = "Page broken (502)"
            return company
        try:
            logo = self.driver.find_element_by_class_name("dtm-logo").find_element_by_tag_name("img").get_attribute("src")
            if logo != "https://www.bbb.org/TerminusContent/dist/img/non-ab-icon__300w.png":
                company.logo = "file/logo/" + company.name.replace(".", "").replace(",", "_").replace(" ", "_").replace("/", "_") + ".png"
                self.driver.execute_script(f'''window.open("{logo}","_blank");''')
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.save_screenshot(company.logo)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            company.logo = ""
        try:
            try:
                company.categories = " > ".join([x.text for x in self.driver.find_element_by_class_name("dtm-breadcrumbs").find_elements_by_tag_name("li")[:4]])
            except:
                pass
            company.phone = self._get_first_with_text(self.driver.find_elements_by_class_name("dtm-phone"))
            company.address = self.driver.find_element_by_tag_name("address").text
            company.website = self._get_first_with_text(self.driver.find_elements_by_class_name("dtm-url"))
            lines = company.address.split("\n")
            company.street_address = lines[0]
            if len(lines) > 1:
                comma_split = lines[1].split(",")
                company.address_locality = comma_split[0].strip()
                if len(comma_split) > 1:
                    company.address_region = comma_split[1].split()[0]
                    company.postal_code = " ".join(comma_split[1].split()[1:])
            icons = self.driver.find_elements_by_class_name("with-icon")
            company.hq = False
            for icon in icons:
                if "Headquarters" in icon.text:
                    company.hq = True
                    break
            try:
                self.driver.find_element_by_class_name("dtm-accreditation-badge")
                company.is_accredited = True
            except:
                company.is_accredited = False
            try:
                company.rating = self.driver.find_elements_by_class_name("dtm-rating")[-1].text.strip().split()[0][:2]
            except:
                company.rating = None
            try:
                review_box = self.driver.find_element_by_class_name("MuiCardContent-root.e1bq2n4p0.css-qo261a")
                company.number_of_stars = round(float(review_box.find_element_by_class_name("MuiTypography-root.MuiTypography-body2.text-size-70.css-8gocr").text.split("/")[0]), 2)
                company.number_of_reviews = int(review_box.text.split("Average of ")[1].split(" Customer")[0].replace(",", ""))
            except:
                company.number_of_stars = None
                company.number_of_reviews = 0
            try:
                company.overview = self.driver.find_element_by_id("overview").find_element_by_class_name("MuiTypography-paragraph").text
            except:
                pass
            try:
                company.products_and_services = self.driver.find_element_by_class_name("dtm-products-services").text
            except:
                pass
            self.driver.get(company_url.split("?")[0] + "/details")
            detail_lines = self.driver.find_element_by_class_name("MuiCardContent-root.e5hddx44.css-1hr2ai0").text.split("\n")
            try:
                buttons = self.driver.find_element_by_class_name("MuiCardContent-root.e5hddx44.css-1hr2ai0").find_elements_by_tag_name("button")
                for button in buttons:
                    if "Read More" in button.text:
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(0.5)
            except:
                pass
            fields_headers = ["Hours of Operation", "Business Management", "Contact Information", "Customer Contact", "Additional Contact Information", "Fax Numbers", "Serving Area", "Products and Services", "Business Categories", "Alternate Business Name", "Email Addresses", "Phone Numbers", "Social Media", "Website Addresses"]
            fields_dict = {}
            current_field = None
            for i, line in enumerate(detail_lines):
                if line == "Read Less":
                    continue
                if "Business Started:" in line:
                    try:
                        company.business_started = datetime.datetime.strptime(detail_lines[i+1].strip().split()[0], "%m/%d/%Y").strftime('%Y-%m-%d')
                    except:
                        company.business_started = datetime.datetime.strptime(detail_lines[i+1].strip().split()[0], "%d/%m/%Y").strftime('%Y-%m-%d')
                elif "Business Incorporated:" in line:
                    try:
                        company.business_incorporated = datetime.datetime.strptime(detail_lines[i+1].strip().split()[0], "%m/%d/%Y").strftime('%Y-%m-%d')
                    except:
                        company.business_incorporated = datetime.datetime.strptime(detail_lines[i+1].strip().split()[0], "%d/%m/%Y").strftime('%Y-%m-%d')
                elif "Type of Entity:" in line:
                    company.type_of_entity = detail_lines[i+1].strip()
                elif "Number of Employees:" in line:
                    company.number_of_employees = detail_lines[i+1].strip()
                elif line in fields_headers:
                    fields_dict[line] = ""
                    current_field = line
                    fields_headers.remove(line)
                elif current_field:
                    fields_dict[current_field] += line + "\n"
            
            if "Hours of Operation" in fields_dict:
                company.working_hours = fields_dict["Hours of Operation"].strip()
            if "Business Management" in fields_dict:
                company.business_management = fields_dict["Business Management"].strip()
            if "Contact Information" in fields_dict:
                company.contact_information = fields_dict["Contact Information"].strip()
            if "Customer Contact" in fields_dict:
                company.customer_contact = fields_dict["Customer Contact"].strip()
            if "Fax Numbers" in fields_dict:
                company.fax_numbers = fields_dict["Fax Numbers"].replace("Primary Fax", "").replace("Other Fax", "").replace("Read More", "").replace("Read Less", "").strip()
            if "Serving Area" in fields_dict:
                company.serving_area = fields_dict["Serving Area"].replace("Read More", "").replace("Read Less", "").strip()
            if "Phone Numbers" in fields_dict:
                if company.phone is None:
                    company.phone = ""
                else:
                    company.phone += "\n"
                company.phone += fields_dict["Phone Numbers"].replace("Read More", "").replace("Read Less", "").replace("Primary Phone", "").replace("Other Phone", "").strip()
            if "Website Addresses" in fields_dict:
                if company.website is None:
                    company.website = ""
                else:
                    company.website += "\n"
                company.website += fields_dict["Website Addresses"].replace("Read More", "").replace("Read Less", "").strip()

        except Exception as e:
            logging.error(str(e))
            send_message("Error scraping company on BBB: " + company.name + " " + company.url + "\n" + str(e), TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS)
            company.status = "error"
            company.log = "details page error: " + str(e)
        if not company.status:
            company.status = "success"
        if save_to_db:
            self.db.insert_or_update_company(company)
        return company


    def scrape_company_reviews(self, company_url=None, company_id = None, save_to_db=True, scrape_specific_review=None) -> List[Review]:

        if company_url:
            self.db.cur.execute("Select company_id from company where url = %s;", (company_url, ))
            fetched_results = self.db.cur.fetchall()
            if len(fetched_results) == 0:
                self.scrape_company_details(company_url=company_url, save_to_db=True)
                self.db.cur.execute("Select company_id from company where url = %s;", (company_url, ))
                fetched_results = self.db.cur.fetchall()
            if len(fetched_results) == 0:
                return []
            if USE_MARIA_DB:
                company_id = fetched_results[0][0]
            else:
                company_id = fetched_results[0]["company_id"]

        elif company_id:
            self.db.cur.execute("Select url from company where company_id = %s;", (company_id, ))
            fetched_results = self.db.cur.fetchall()
            if len(fetched_results) == 1:
                if USE_MARIA_DB:
                    company_url = fetched_results[0][0]
                else:
                    company_url = fetched_results[0]["company_url"]
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))
        else:
            raise Exception("Please provide either company URL or company ID")

        if scrape_specific_review:
            logging.info("Scraping Review with id %s for %s" % (scrape_specific_review, company_url))
        else:
            logging.info("Scraping Reviews for " + company_url)
        review_url = company_url + "/customer-reviews"
        self.driver.get(review_url)
        
        if scrape_specific_review:
            self.db.cur.execute("SELECT username, review_date from review where review_id = %s", (scrape_specific_review))
            review_results = self.db.cur.fetchall()

        reviews = []
        while True:
            try:
                load_more = self.driver.find_element_by_class_name("MuiButtonBase-root.MuiButton-root.MuiButton-contained.MuiButton-containedPrimary.MuiButton-sizeMedium.MuiButton-containedSizeMedium.MuiButton-fullWidth.ezpahdb0.css-1uz6nmt")
                self.driver.execute_script("arguments[0].click();", load_more)  
                time.sleep(2)
            except:
                break

        try:
            review_tags = self.driver.find_element_by_class_name("stack.css-zyn7di.e62xhj40").find_elements_by_tag_name("li")
        except:
            logging.info("No reviews for company: " + company_url)
            return []
        for review_tag in review_tags:
            username = review_tag.find_element_by_tag_name("h3").text.strip().replace("Review from\n", "")
            if scrape_specific_review and username != review_results[0]["username"]:
                continue
            review = Review()
            review.company_id = company_id
            review.username = username
            try:
                date = review_tag.find_element_by_class_name("MuiTypography-root.text-gray-70.MuiTypography-body2").text.strip()
                try:
                    review.review_date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime('%Y-%m-%d')
                except:
                    review.review_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
            except:
                review.review_date = None
                review.log += "Error while scraping/parsing date\n"
                review.status = "error"
            if scrape_specific_review and str(review.review_date) != str(review_results[0]["review_date"]):
                continue
            review_texts = review_tag.find_elements_by_class_name("MuiTypography-root.text-black.MuiTypography-body2")
            if not review_texts:
                review_texts = review_tag.find_elements_by_class_name("sc-3wcfn7-5")
            try:
                review.review_text = review_texts[0].text
            except:
                review.review_text = ""
            try:
                review.review_rating = round(float(review_tag.find_element_by_class_name("css-amhf5.ei2kcdu2").find_element_by_class_name("visually-hidden").text.split()[0]), 1)
            except:
                pass
            try:
                review.company_response_text = review_texts[1].text
                date = review_tag.find_element_by_class_name("MuiTypography-root.text-gray-70.MuiTypography-body1").text.strip()
                try:
                    review.company_response_date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime('%Y-%m-%d')
                except:
                    review.company_response_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
            except:
                pass
            if review.status == "error":
                send_message("Error scraping review for company on BBB: " + company_url + "\n" + review.log, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS)
            reviews.append(review)
            if scrape_specific_review:
                break

        if save_to_db and reviews:
            self.db.insert_or_update_reviews(reviews)
        
        return reviews

    
    def scrape_company_complaints(self, company_url=None, company_id = None, save_to_db=True, scrape_specific_complaint=None) -> List[Complaint]:

        if company_url:
            self.db.cur.execute("Select company_id from company where url = %s;", (company_url, ))
            fetched_results = self.db.cur.fetchall()
            if len(fetched_results) == 0:
                self.scrape_company_details(company_url=company_url, save_to_db=True)
                self.db.cur.execute("Select company_id from company where url = %s;", (company_url, ))
                fetched_results = self.db.cur.fetchall()
            if len(fetched_results) == 0:
                return []
            if USE_MARIA_DB:
                company_id = fetched_results[0][0]
            else:
                company_id = fetched_results[0]["company_id"]

        elif company_id:
            self.db.cur.execute("Select url from company where company_id = %s;", (company_id, ))
            fetched_results = self.db.cur.fetchall()
            if len(fetched_results) == 1:
                if USE_MARIA_DB:
                    company_url = fetched_results[0][0]
                else:
                    company_url = fetched_results[0]["company_url"]
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))
        else:
            raise Exception("Please provide either company URL or company ID")

        if scrape_specific_complaint:
            logging.info("Scraping Complaint with id %s for %s" % (scrape_specific_complaint, company_url))
        else:
            logging.info("Scraping Complaints for " + company_url)
        complaint_url = company_url + "/complaints"
        self.driver.get(complaint_url)
        
        if scrape_specific_complaint:
            self.db.cur.execute("SELECT username, complaint_date from complaint where complaint_id = %s", (scrape_specific_complaint))
            complaint_results = self.db.cur.fetchall()

        complaints = []
        while True:
            try:
                load_more = self.driver.find_element_by_class_name("MuiButtonBase-root.MuiButton-root.MuiButton-contained.MuiButton-containedPrimary.MuiButton-sizeMedium.MuiButton-containedSizeMedium.MuiButton-fullWidth.ezpahdb0.css-1uz6nmt")
                self.driver.execute_script("arguments[0].click();", load_more)  
                time.sleep(2)
            except:
                break
        try:
            complaint_tags = self.driver.find_element_by_class_name("stack.css-zyn7di.e62xhj40").find_elements_by_tag_name("li")
        except:
            logging.info("No Complaints for company: " + company_url)
            return []
        for complaint_tag in complaint_tags:
            complaint = Complaint()
            complaint.company_id = company_id
            try:
                complaint.complaint_type = complaint_tag.find_element_by_class_name("MuiTypography-root.MuiTypography-body2").text.replace("Complaint Type:", "").replace("Anonymous complaint:", "").strip()
            except:
                continue
            try:
                date = complaint_tag.find_element_by_class_name("MuiTypography-root.MuiTypography-body2.text-gray-70.css-8gocr").text.strip()
                try:
                    complaint.complaint_date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime('%Y-%m-%d')
                except:
                    complaint.complaint_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
            except:
                complaint.complaint_date = None
                complaint.log += "Error while scraping/parsing date\n"
                complaint.status = "error"
            try:
                complaint.complaint_text = complaint_tag.find_elements_by_class_name("MuiTypography-root.MuiTypography-body2.css-8gocr")[-1].text
            except:
                complaint.complaint_text = None
                complaint.log += "Error while scraping complaint text\n"
                complaint.status = "error"
            if scrape_specific_complaint and (complaint.complaint_type != complaint_results[0]["complaint_type"] or str(complaint.complaint_date) != str(complaint_results[0]["complaint_date"]) or complaint.complaint_text != complaint_results[0]["complaint_text"]):
                continue
            try:
                complaint.company_response_text = complaint_tag.find_element_by_class_name("MuiTypography-root.MuiTypography-body2.text-black.eeijlg00.css-jzmzv").text.replace("Business Response", "").strip()
                date = complaint_tag.find_element_by_class_name("MuiTypography-root.MuiTypography-body1.text-gray-70.css-a4lmh5").text.strip()
                try:
                    complaint.company_response_date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime('%Y-%m-%d')
                except:
                    complaint.company_response_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
            except:
                pass
            if complaint.status == "error":
                send_message("Error scraping complaint for company on BBB: " + company_url + "\n" + complaint.log, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS)
            complaints.append(complaint)
            if scrape_specific_complaint:
                break

        if save_to_db and complaints:
            self.db.insert_or_update_complaints(complaints)
        
        return complaints


    def bulk_scrape(self, no_of_threads=1, scrape_reviews_and_complaints=True):

            
        sitemap_urls = ["https://www.bbb.org/sitemap-accredited-business-profiles-index.xml", "https://www.bbb.org/sitemap-business-profiles-index.xml"]
        logging.info("Starting scrape (gathering sitemap urls...)")
        for sitemap_url in sitemap_urls:
        
            self.driver.get(sitemap_url)
            root = ET.fromstring(self.driver.page_source)
            urls = []
            for child in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                urls.append(child.text)
            for url in urls:
                self.driver.get(url)
                root = ET.fromstring(self.driver.page_source)
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
                    self.db.cur.execute("SELECT date_updated from company where url = %s", (company_url, ))
                    data = self.db.cur.fetchall()
                    if len(data) > 0:
                        if USE_MARIA_DB:
                            date_updated = data[0][0]
                        else:
                            date_updated = data[0]["date_updated"]
                        if (date_updated - datetime.datetime.now()).days < 7:
                            continue

                    found_url = True
                    if platform == "linux" or platform == "linux2":
                        urls_to_scrape.put(company_url)
                    else:
                        urls_to_scrape.append(company_url)
                if not found_url:
                    continue

                if platform == "linux" or platform == "linux2":
                    processes = []
                    for i in range(no_of_threads):
                        processes.append(Process(target=self.scrape_urls_from_queue, args=(urls_to_scrape, scrape_reviews_and_complaints, )))
                        processes[i].start()

                    for i in range(no_of_threads):
                        processes[i].join()
                else:
                    for company_url in urls_to_scrape:
                        self.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints)


    def scrape_urls_from_queue(self, q, scrape_reviews_and_complaints=True):

        try:
            scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS, proxy_type=PROXY_TYPE)
            
            while q.qsize():
                company_url = q.get()
                scraper.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints)
            
        except:
            pass
        scraper.kill_chrome()
                    
    def _get_first_with_text(self, elements):
        for element in elements:
            elem_text = element.text.strip()
            if elem_text != "":
                return elem_text
        return None

    def kill_chrome(self):
        try:
            self.driver.quit()
            if os.name != "nt":
                self.display.stop()
        except:
            pass


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--bulk_scrape", nargs='?', type=str, default="False", help="Boolean variable to bulk scrape companies. Default False. If set to True, save_to_db will also be set to True")
    parser.add_argument("--urls", nargs='*', help="url(s) for scraping. Separate by spaces")
    parser.add_argument("--save_to_db", nargs='?', type=str, default="False", help="Boolean variable to save to db. Default False")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument("--log_file", nargs='?', type=str, default=None, help="Path for log file. If not given, output will be printed on stdout.")
    parser.add_argument("--scrape_reviews_and_complaints", nargs='?', type=str, default="False", help="Boolean variable to get company reviews and complaints as well. Default True")
    parser.add_argument("--grabber-bbb-mustansir", nargs='?', type=bool, default=False, help="Only mark to kill all")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    # setup logging based on arguments
    if args.log_file and platform == "linux" or platform == "linux2":
        logging.basicConfig(filename=args.log_file, filemode='a',format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    elif platform == "linux" or platform == "linux2":
        logging.basicConfig(format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    elif args.log_file:
        logging.basicConfig(filename=args.log_file, filemode='a',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS, proxy_type=PROXY_TYPE)
    if str2bool(args.bulk_scrape):
        scraper.bulk_scrape(no_of_threads=args.no_of_threads, scrape_reviews_and_complaints=str2bool(args.scrape_reviews_and_complaints))
    else:
        for url in args.urls:
            company = scraper.scrape_company_details(company_url=url, save_to_db=str2bool(args.save_to_db))
            logging.info("Company Details for %s scraped successfully.\n" % company.name)
            try:
                print(company)
            except Exception as e:
                print(e)
            print("\n")
            company.reviews = scraper.scrape_company_reviews(company_url=url, save_to_db=str2bool(args.save_to_db))
            logging.info("Reviews for %s scraped successfully.\n" % company.name)
            for i, review in enumerate(company.reviews, start=1):
                print("Review# " + str(i))
                try:
                    print(review)
                except Exception as e:
                    print(e)
                print("\n")
            company.complaints = scraper.scrape_company_complaints(company_url=url, save_to_db=str2bool(args.save_to_db))
            logging.info("Complaints for %s scraped successfully.\n" % company.name)
            for i, complaint in enumerate(company.complaints, start=1):
                print("Complaint# " + str(i))
                try:
                    print(complaint)
                except Exception as e:
                    print(e)
                print("\n")


    scraper.kill_chrome()

        
    
    