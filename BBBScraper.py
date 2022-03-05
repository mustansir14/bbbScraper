from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
from typing import List
from DB import DB
from models import Company, Complaint, Review
from config import *
import xml.etree.ElementTree as ET
import datetime
import os
import argparse
import json
import sys
import logging, zipfile
from pyvirtualdisplay import Display
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)



class BBBScraper():

    def __init__(self, chromedriver_path=None, proxy=None, proxy_port=None, proxy_user=None, proxy_pass=None, proxy_type="https", headless=True) -> None:
        options = Options()
        options.add_argument("window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
        if proxy:
            if not proxy_port:
                raise Exception("Proxy Port missing.")
            if proxy_user and proxy_pass:
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
                pluginfile = 'proxy_auth_plugin.zip'
                with zipfile.ZipFile(pluginfile, 'w') as zp:
                    zp.writestr("manifest.json", manifest_json)
                    zp.writestr("background.js", background_js)
                options.add_extension(pluginfile)
            else:
                options.add_argument("--proxy-server=%s" % proxy_type + "://" + proxy + ":" + proxy_port)
        if headless:
            display = Display(visible=0, size=(1920, 1080))
            display.start()
        if chromedriver_path:
            self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)
        if not os.path.exists("file/logo/"):
            os.makedirs("file/logo")
        self.db = DB()


    def scrape_url(self, url, save_to_db=True) -> Company:
        
        if "https://www.bbb.org/" not in url and "profile" not in url:
            raise Exception("Invalid URL")
        url_split = url.split("/")
        if url_split[-1] in ["details", "customer-reviews", "complaints"]:
            url = "/".join(url_split[:-1]) 
        company = self.scrape_company_details(company_url=url, save_to_db=save_to_db)
        company.reviews = self.scrape_company_reviews(company_url=url, save_to_db=save_to_db)
        company.complaints = self.scrape_company_complaints(company_url=url, save_to_db=save_to_db)
        return company


    def scrape_company_details(self, company_url=None, company_id=None, save_to_db=True) -> Company:

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
        self.driver.get(company_url)
        company.name = self.driver.find_element_by_class_name("MuiTypography-root.MuiTypography-h3").text.strip()
        try:
            logo = self.driver.find_element_by_class_name("business-card__logo").find_element_by_tag_name("img").get_attribute("src")
            if logo != "https://www.bbb.org/TerminusContent/dist/img/non-ab-icon__300w.png":
                company.logo = "file/logo/" + company.name.replace(".", "").replace(",", "_").replace(" ", "_").replace("/", "_") + ".png"
                self.driver.execute_script(f'''window.open("{logo}","_blank");''')
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.save_screenshot(company.logo)
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            logging.error("Error in saving logo to disk. " + str(e))
            company.logo = ""
        try:
            company.categories = " > ".join([x.text for x in self.driver.find_elements_by_class_name("breadcrumbs__breadcrumb")[:4]])
            company.phone = self._get_first_with_text(self.driver.find_elements_by_class_name("dtm-phone"))
            company.address = self.driver.find_element_by_tag_name("address").text
            company.website = self._get_first_with_text(self.driver.find_elements_by_class_name("dtm-url"))
            try:
                review_box = self.driver.find_element_by_class_name("business-reviews-card__body")
                company.number_of_stars = round(float(review_box.find_element_by_tag_name("strong").text), 1)
                company.number_of_reviews = int(review_box.text.split("Average of ")[1].split(" Customer")[0].replace(",", ""))
            except:
                company.number_of_stars = None
                company.number_of_reviews = 0
            try:
                company.overview = self.driver.find_element_by_class_name("OverviewParagraph-sc-d81vb4-0").text
            except:
                pass
            try:
                company.products_and_services = self.driver.find_element_by_class_name("dtm-products-services").text
            except:
                pass
            self.driver.get(company_url + "/details")
            detail_lines = self.driver.find_element_by_class_name("business-details-card__content").text.split("\n")
            try:
                button = self.driver.find_element_by_class_name("business-details-card__content").find_element_by_class_name("styles__LinkStyled-sc-m9tecn-0.ixymiX")
                if "Read More" in button.text:
                    button.click()
                    time.sleep(0.5)
            except:
                pass
            fields_headers = ["Hours of Operation", "Business Management", "Contact Information", "Customer Contact", "Additional Contact Information", "Fax Numbers", "Serving Area", "Products and Services", "Business Categories", "Alternate Business Name", "Email Addresses", "Phone Numbers", "Social Media"]
            fields_dict = {}
            current_field = None
            for i, line in enumerate(detail_lines):
                if line == "Read Less":
                    continue
                if "Business Started:" in line:
                    try:
                        company.business_started = datetime.datetime.strptime(detail_lines[i+1].strip(), "%m/%d/%Y").strftime('%Y-%m-%d')
                    except:
                        company.business_started = datetime.datetime.strptime(detail_lines[i+1].strip(), "%d/%m/%Y").strftime('%Y-%m-%d')
                elif "Business Incorporated:" in line:
                    try:
                        company.business_incorporated = datetime.datetime.strptime(detail_lines[i+1].strip(), "%m/%d/%Y").strftime('%Y-%m-%d')
                    except:
                        company.business_incorporated = datetime.datetime.strptime(detail_lines[i+1].strip(), "%d/%m/%Y").strftime('%Y-%m-%d')
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
                company.fax_numbers = fields_dict["Fax Numbers"].replace("Primary Fax", "").replace("Other Fax", "").strip()
            if "Serving Area" in fields_dict:
                company.serving_area = fields_dict["Serving Area"].replace("Read More", "").strip()

        except Exception as e:
            logging.error(str(e))
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
                self.driver.find_element_by_class_name("MuiButtonBase-root.MuiButton-root.MuiButton-contained.styles__Button-sc-1jgsape-0.eevMuP.MuiButton-fullWidth").click()     
                time.sleep(1)
                WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "FullPageLoadingSpinner__Overlay-sc-1vxe47i-0")))
            except:
                break

        review_tags = self.driver.find_elements_by_class_name("styles__ReviewCard-sc-bfb5eq-0")
        for review_tag in review_tags:
            username = review_tag.find_element_by_class_name("styles__Name-sc-19fiob-2").text.strip()
            if scrape_specific_review and username != review_results[0]["username"]:
                continue
            review = Review()
            review.company_id = company_id
            review.username = username
            try:
                date = review_tag.find_element_by_class_name("styles__Date-sc-19fiob-4").text.strip()
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
            review_texts = review_tag.find_elements_by_class_name("MuiTypography-root.Text-sc-19d5fbu-0.imUbRu.text-black.MuiTypography-body2")
            if not review_texts:
                review_texts = review_tag.find_elements_by_class_name("styles__Review-sc-19fiob-5")
            try:
                review.review_text = review_texts[0].text
            except:
                review.review_text = ""
            try:
                review.review_rating = round(float(review_tag.find_element_by_class_name("visually-hidden").text.split()[0]), 1)
            except:
                review.status = "error"
                review.log += "error while scraping review stars\n"
            try:
                review.company_response_text = review_texts[1].text
                date = review_tag.find_element_by_class_name("Date-sc-sl1dca-0").text.strip()
                try:
                    review.company_response_date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime('%Y-%m-%d')
                except:
                    review.company_response_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
            except:
                pass
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
                self.driver.find_element_by_class_name("MuiButtonBase-root.MuiButton-root.MuiButton-contained.styles__Button-sc-1jgsape-0.eevMuP.MuiButton-fullWidth").click()     
                time.sleep(1)
                WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "FullPageLoadingSpinner__Overlay-sc-1vxe47i-0")))
            except:
                break

        complaint_tags = self.driver.find_elements_by_class_name("styles__Complaint-sc-1fdh5mu-0")
        for complaint_tag in complaint_tags:
            complaint = Complaint()
            complaint.company_id = company_id
            complaint.complaint_type = complaint_tag.find_element_by_class_name("Type-sc-e74mc1-0").text.replace("Complaint Type:", "").strip()
            try:
                date = complaint_tag.find_element_by_class_name("Content__Date-sc-30ryg1-1").text.strip()
                try:
                    complaint.complaint_date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime('%Y-%m-%d')
                except:
                    complaint.complaint_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
            except:
                complaint.complaint_date = None
                complaint.log += "Error while scraping/parsing date\n"
                complaint.status = "error"
            try:
                complaint.complaint_text = complaint_tag.find_element_by_class_name("Content__Text-sc-30ryg1-2").text
            except:
                complaint.complaint_text = None
                complaint.log += "Error while scraping complaint text\n"
                complaint.status = "error"
            if scrape_specific_complaint and (complaint.complaint_type != complaint_results[0]["complaint_type"] or str(complaint.complaint_date) != str(complaint_results[0]["complaint_date"]) or complaint.complaint_text != complaint_results[0]["complaint_text"]):
                continue
            try:
                complaint.company_response_text = complaint_tag.find_element_by_class_name("Text-sc-19d5fbu-0").text
                date = complaint_tag.find_element_by_class_name("Date-sc-sl1dca-0").text.strip()
                try:
                    complaint.company_response_date = datetime.datetime.strptime(date, "%m/%d/%Y").strftime('%Y-%m-%d')
                except:
                    complaint.company_response_date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime('%Y-%m-%d')
            except:
                pass
            complaints.append(complaint)
            if scrape_specific_complaint:
                break

        if save_to_db and complaints:
            self.db.insert_or_update_complaints(complaints)
        
        return complaints


    def bulk_scrape(self, continue_from_last_scrape=False):
 
        if continue_from_last_scrape:
            try:
                with open("last_scrape_info.json", "r") as f:
                    last_scrape = json.load(f)
                last_company_url = last_scrape["url"]
                last_sub_url = last_scrape["sub_url"]
                category_flag = False
            except:
                logging.info("No backup file found or invalid file. Scraping from beginning")
                category_flag = True
                last_scrape = {}
        else:
            category_flag = True
            last_scrape = {}
            
        url_flag = category_flag

        logging.info("Starting scrape (gathering sitemap urls...)")
        self.driver.get("https://www.bbb.org/sitemap-business-profiles-index.xml")
        self.driver.save_screenshot("first.png")
        root = ET.fromstring(self.driver.page_source)
        urls = []
        for child in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(child.text)
        for url in urls:
            if not category_flag and last_sub_url == url:
                category_flag = True
            if category_flag:
                self.driver.get(url)
                root = ET.fromstring(self.driver.page_source)
                company_urls = []
                for child in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                    child_text = child.text
                    if "profile" in child_text:
                        company_urls.append(child_text)
                for company_url in company_urls:
                    if not url_flag and company_url == last_company_url:
                        url_flag = True
                        continue
                    if url_flag:

                        self.scrape_url(company_url)
                        
                        last_scrape["url"] = company_url
                        last_scrape["sub_url"] = url
                        with open("last_scrape_info.json", "w") as f:
                            json.dump(last_scrape, f)

    def _get_first_with_text(self, elements):
        for element in elements:
            elem_text = element.text.strip()
            if elem_text != "":
                return elem_text
        return None

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--bulk_scrape", nargs='?', type=bool, default=False, help="Boolean variable to bulk scrape companies. Default False. If set to True, save_to_db will also be set to True")
    parser.add_argument("--urls", nargs='*', help="url(s) for scraping. Separate by spaces")
    parser.add_argument("--save_to_db", nargs='?', type=bool, default=False, help="Boolean variable to save to db. Default False")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS, proxy_type=PROXY_TYPE)
    if args.bulk_scrape:
        if os.path.isfile("last_scrape_info.json"):
            scraper.bulk_scrape(continue_from_last_scrape=True)
        else:
            scraper.bulk_scrape(continue_from_last_scrape=False)
    else:
        for url in args.urls:
            company = scraper.scrape_company_details(company_url=url, save_to_db=args.save_to_db)
            logging.info("Company Details for %s scraped successfully.\n" % company.id)
            print(company)
            print("\n")
            company.reviews = scraper.scrape_company_reviews(company_url=url, save_to_db=args.save_to_db)
            logging.info("Reviews for %s scraped successfully.\n" % company.id)
            for i, review in enumerate(company.reviews, start=1):
                print("Review# " + str(i))
                print(review)
                print("\n")
            company.complaints = scraper.scrape_company_complaints(company_url=url, save_to_db=args.save_to_db)
            logging.info("Complaints for %s scraped successfully.\n" % company.id)
            for i, complaint in enumerate(company.complaints, start=1):
                print("Complaint# " + str(i))
                print(complaint)
                print("\n")

        
    
    