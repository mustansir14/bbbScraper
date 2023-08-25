##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from dataclasses import field
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time, traceback
from typing import List
from includes.DB import DB
from includes.models import Company, Complaint, Review
from includes.proxies import getProxy
import xml.etree.ElementTree as ET
import datetime
import os, random, glob
import argparse
import sys
import logging, zipfile
from pyvirtualdisplay import Display
from sys import platform
from multiprocessing import Process, Queue
from includes.telegram_reporter import send_message
from slugify import slugify
import json
import re
import tempfile
import secrets
from urllib.request import urlretrieve
import shutil


class BBBScraper():

    def __init__(self, chromedriver_path=None, proxy=None, proxy_port=None, proxy_user=None, proxy_pass=None,
                 proxy_type="http") -> None:
        self.driver = None
        self.lastValidProxy = None
        self.rescrapeSettingKey = "rescrape_all_from_db.from_company_id";

        if not os.path.exists("file/logo/"):
            os.makedirs("file/logo")

        self.db = DB()

    def removeCoreDumps(self):
        try:
            logging.info("Remove core dumps, to free space...")

            for file in glob.glob("./core.*"):
                try:
                    os.remove(file)
                except:
                    pass
        except Exception as e:
            logging.error("removeCoreDumps exception: " + str(e))

    def createBrowser(self, chromedriver_path=None, proxy=None, proxy_port=None, proxy_user=None, proxy_pass=None,
                      proxy_type="http"):
        if self.driver:
            self.kill_chrome()

        # on long docker living too much coredumps create big storage usage
        self.removeCoreDumps()

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
        # headless does not support extensions
        # options.add_argument('--headless')
        options.add_argument("window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-gpu')
        options.add_argument("--mute-audio")
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--single-process'); # one process to take less memory
        options.add_argument('--renderer-process-limit=1')  # do not allow take more resources
        options.add_argument('--disable-crash-reporter')  # disable crash reporter process
        options.add_argument('--no-zygote')  # disable zygote process
        options.add_argument('--disable-crashpad')
        options.add_argument('--grabber-bbb-mustansir')
        #options.add_argument("--auto-open-devtools-for-tabs")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
        if proxy:
            if not proxy_port:
                raise Exception("Proxy Port missing.")

            self.session.proxies.update({proxy_type: proxy_type + "://" + proxy + ":" + proxy_port})
            options.add_argument("--proxy-server=%s" % proxy_type + "://" + proxy + ":" + proxy_port)

        self.usedProxy = proxy_type + "://" + proxy + ":" + proxy_port if proxy else ""

        if os.name != "nt":
            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()

        if chromedriver_path:
            self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
        else:
            self.driver = webdriver.Chrome(options=options, service=Service(self.getChromeDriver()))

        # Optimization: disable ads and analytics here
        self.driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": [
            "analytics.google.com",
            "www.google-analytics.com",
            "stats.g.doubleclick.net",
            "js-agent.newrelic.com",
            "analytics.tiktok.com",
            "adservice.google.com",
            "ad.doubleclick.net",
            "googletagmanager.com",
            "livechatinc.com",
            "gstatic.com",
            "facebook.net", # recaptcha
            "google.com", # recaptcha
            "assets.adobedtm.com",
            "mouseflow.com",
            "hubspot.com",
            "*.js",
            "*.png",
            "*.svg",
            "*.gif",
            "*.jpg",
            "*.jpeg",
            "*.bmp",
            "*.webp",
            "*.woff2",
            "*.woff",
        ]})

        self.driver.execute_cdp_cmd('Network.enable', {})

    def getChromeDriver(self):
        version = "116.0.5845.96"
        original = os.path.join(tempfile.gettempdir(), "chrome_" + str(version) + "_origin")

        if sys.platform.endswith("win32"):
            original += ".exe"

        if not os.path.exists(original):
            logging.info("Download last version of original: " + original)

            platform = "linux64"

            if sys.platform.endswith("win32"):
                platform = "win64"

            packageUrl = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/" + version + "/" + platform + "/chromedriver-" + platform + ".zip"
            logging.info(packageUrl)

            filename, headers = urlretrieve(packageUrl)

            logging.info(headers)
            logging.info("Unzip...")

            with zipfile.ZipFile(filename, mode="r") as z:
                chromeDriver = "chromedriver-" + platform + "/chromedriver"

                if sys.platform.endswith("win32"):
                    chromeDriver += ".exe"

                with z.open(chromeDriver) as zf, open(original, 'wb') as f:
                    shutil.copyfileobj(zf, f)

            logging.info("Remove zip...")
            os.remove(filename)

            logging.info("Set permissions to: " + original)
            os.chmod(original, 0o755)

            if not os.path.isfile(original):
                raise Exception("No origin executable")

        return original

        # Fix: i dont know but sometimes shutil.copy2 do not copy file
        for i in range(3):
            target = original.replace(".exe", "") + "_" + secrets.token_hex(16)
            if sys.platform.endswith("win32"):
                target += ".exe"

            shutil.copy2(original, target)

            # BugFix: may be situation then file not fully copied
            time.sleep(1);

            if os.path.isfile(target):
                break

        if not os.path.isfile(target):
            raise Exception("No target executable: " + target + ", origin exists: " + str(os.path.isfile(original)))

        os.chmod(original, 0o755)

        logging.info("Return target: " + target)

        return target

    def scrape_url(self, url, save_to_db=True, scrape_reviews_and_complaints=True,
                   set_rescrape_setting=False) -> Company:

        if "https://www.bbb.org/" not in url and "profile" not in url:
            raise Exception("Invalid URL")

        url_split = url.split("/")
        if url_split[-1] in ["details", "customer-reviews", "complaints"]:
            url = "/".join(url_split[:-1])

        self.reloadBrowser()
        self.driver.get("https://www.bbb.org/us/ct/berlin/profile/concrete-contractors/nadeau-brothers-0111-22004598")

        # must check this before, because url may be deleted in scrape_company_details
        company_id = self.db.getCompanyIdByUrl(url)

        company = self.scrape_company_details(company_url=url, save_to_db=save_to_db,
                                              half_scraped=not scrape_reviews_and_complaints)
        if company.status == "success":
            if scrape_reviews_and_complaints:
                company.reviews = self.scrape_company_reviews(company_url=company.url, save_to_db=save_to_db)
                company.complaints = self.scrape_company_complaints(company_url=company.url, save_to_db=save_to_db)

        self.kill_chrome()

        if set_rescrape_setting:
            sql = 'insert into `settings` set `name` = ?, `value` = ? ON DUPLICATE KEY UPDATE `value` = IF(`value` < ?, ?, `value`)'
            args = (self.rescrapeSettingKey, company_id, company_id, company_id,)

            logging.info(sql)
            logging.info(args)

            self.db.execSQL(sql, args)
        else:
            logging.info("Do not update rescrape settings")

        return company

    def getSchemaOrgByType(self, type):
        scriptTags = self.driver.find_elements(By.CSS_SELECTOR, 'script[type*="ld+json"]')
        for scriptTag in scriptTags:
            schemaOrgArray = json.loads(scriptTag.get_attribute('innerHTML').strip("\r\n\t ;"))
            for schemaOrg in schemaOrgArray:
                if schemaOrg['@type'] == type:
                    return schemaOrg

        return None

    def getCompanyLDJson(self):
        localBusiness = self.getSchemaOrgByType('LocalBusiness')
        if localBusiness is None:
            raise Exception("Can not get company ld json")

        return localBusiness

    def getCompanyPreloadState(self):
        code = self.driver.find_element(By.XPATH, '//script[contains(text(),"__PRELOADED_STATE__")]').get_attribute(
            'innerHTML').strip("\r\n\t ;")
        code = re.sub('^[^\{]+?{', '{', code)
        return json.loads(code)

    def reloadBrowser(self, useProxy=None):
        logging.info("Close old browser, creating new...")

        self.lastValidProxy = getProxy(useProxy)

        self.kill_chrome()
        self.createBrowser(
            None,
            self.lastValidProxy['proxy'],
            self.lastValidProxy['proxy_port'],
            self.lastValidProxy['proxy_user'],
            self.lastValidProxy['proxy_pass'],
            self.lastValidProxy['proxy_type']
        )

    def scrape_company_details(self, company_url=None, company_id=None, save_to_db=True, half_scraped=False) -> Company:

        if not company_url and not company_id:
            raise Exception("Please provide either company URL or company ID")
        elif company_id:
            row = self.db.queryRow("Select url from company where company_id = %s;", (company_id,))
            if row is not None:
                company_url = row['company_url']
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))

        logging.info("Scraping Company Details with proxy " + self.usedProxy + " for " + company_url)

        company = Company()
        company.url = company_url
        company.half_scraped = half_scraped
        company.country = company_url.replace("https://www.bbb.org/", "")[:2]
        if company.country not in ['us', 'ca']:
            # send_message("Company %s does not have valid country in url!!" % company.url)
            company.country = None

        counter = 0
        while True:
            logging.info("Driver get: " + company_url)
            self.driver.get(company_url)

            # BugFix: original url https://www.bbb.org/us/al/huntsville/profile/business-associations/the-catalyst-center-for-business-entrepreneurship-0513-900075144
            # redirect to: https://www.bbb.org/us/al/huntsville/charity-review/charity-community-development-civic-organizations/the-catalyst-center-for-business-entrepreneurship-0513-900075144
            if "/charity-review/" in self.driver.current_url:
                logging.info("Charity review detected, removing from database")
                self.db.removeCompanyByUrl(company_url)

                company.status = "error"
                company.log = "Charity review"

                return company

            if "403 Forbidden" in self.driver.title:
                logging.info("403 Forbidden error. Reload browser....")
                self.reloadBrowser()
                counter = counter + 1
            else:
                break

            if counter > 5:
                raise Exception("Company page, always 403 error")

        statusMustBeSuccess = False
        onlyMarkAsSuccess = False

        try:
            if os.getenv('GET_SOURCE_CODE', '0') == "1":
                company.source_code = self.driver.page_source

            if "<title>Page not found |" in self.driver.page_source:
                statusMustBeSuccess = True
                onlyMarkAsSuccess = True
                raise Exception("On url request returned: 404 - Whoops! Page not found!")

            if "Oops! We'll be right back." in self.driver.page_source:
                statusMustBeSuccess = True
                onlyMarkAsSuccess = True
                raise Exception("On url request returned: 500 - Whoops! We'll be right back!")

            companyLdJson = self.getCompanyLDJson()
            companyPreloadState = self.getCompanyPreloadState()

            company.name = companyLdJson['name']

            if company_url != self.driver.current_url:
                # old url: https://www.bbb.org/us/nd/fargo/profile/bank/bell-bank-0704-96381846
                # new url: https://www.bbb.org/us/mn/saint-louis-park/profile/real-estate-loans/bell-mortgage-0704-96148267

                newUrl = self.driver.current_url.split("?")[0]

                logging.info("Company url changed, move data to new url")
                logging.info("Old url: " + company_url)
                logging.info("New url: " + newUrl)

                self.db.move_company_to_other_company(company_url, newUrl)

                company.url = newUrl
                company_url = newUrl

            try:
                logo = self.driver.find_element(By.CSS_SELECTOR, ".dtm-logo").find_element(By.CSS_SELECTOR,
                                                                                           "img").get_attribute("src")
                if not "non-ab-icon__300w.png" in logo:
                    company.logo = "file/logo/" + slugify(company.name) + ".png"

                    self.driver.execute_script(f'''window.open("{logo}","_blank");''')
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    self.driver.save_screenshot(company.logo)
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as e:
                company.logo = ""

            company.categories = "\n".join(
                [x['title'] for x in companyPreloadState['businessProfile']['categories']['links']])
            company.phone = companyLdJson['telephone'] if 'telephone' in companyLdJson else None
            company.address = self.driver.find_element(By.CSS_SELECTOR, "address").text
            company.website = self._get_first_with_text(self.driver.find_elements(By.CSS_SELECTOR, ".dtm-url"))
            if company.website and company.website.lower().strip() == "visit website":
                company.website = self._get_first_with_text(self.driver.find_elements(By.CSS_SELECTOR, ".dtm-url"),
                                                            get_href=True)
            lines = company.address.split("\n")

            company.street_address = companyLdJson['address']['streetAddress']
            company.address_locality = companyLdJson['address']['addressLocality']
            company.address_region = companyLdJson['address']['addressRegion']
            company.postal_code = companyLdJson['address']['postalCode']
            company.street_address = companyLdJson['address']['streetAddress']

            icons = self.driver.find_elements(By.CSS_SELECTOR, ".find_elementwith-icon")
            company.hq = False
            for icon in icons:
                if "Headquarters" in icon.text:
                    company.hq = True
                    break

            try:
                self.driver.find_element(By.CSS_SELECTOR, ".dtm-accreditation-badge")
                company.is_accredited = True
            except:
                company.is_accredited = False

            try:
                company.rating = self.driver.find_elements(By.CSS_SELECTOR, ".dtm-rating")[-1].text.strip().split()[0][
                                 :2]
            except:
                company.rating = None

            try:
                element = self.driver.find_element(By.XPATH, '//*[contains(@class,"dtm-stars")]/following-sibling::*')
                company.number_of_stars = round(float(element.text.strip().split("/")[0]), 2)
            except:
                company.number_of_stars = None

            # these to fields updated in DB class, to write how much reviews/complaints scraped
            company.number_of_reviews = 0
            company.number_of_complaints = 0
            company.overview = companyPreloadState['businessProfile']['orgDetails']['organizationDescription']
            if company.overview:
                company.overview = re.sub('</?[^<]+?>', '', company.overview)
                company.overview = re.sub('(\r?\n){2,}', '\n\n', company.overview)

            try:
                company.products_and_services = self.driver.find_element(By.CSS_SELECTOR, ".dtm-products-services").text
            except:
                pass

            counter = 0
            while True:
                logging.info("Driver get: " + company.url + "/details")
                self.driver.get(company.url + "/details")

                if "403 Forbidden" in self.driver.title:
                    logging.info("403 Forbidden error. Sleeping for 60 seconds....")
                    time.sleep(60)

                    counter = counter + 1
                else:
                    break

                if counter > 2:
                    raise Exception("Details page, always 403 error")

            if os.getenv('GET_SOURCE_CODE', '0') == "1":
                company.source_code_details = self.driver.page_source

            # some proxies are from Mexico, and output not english, need more patterns
            patterns = [
                '//*[contains(normalize-space(text()),"BBB File Opened")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
                '//*[contains(normalize-space(text()),"Business Started")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
                '//*[contains(@class,"dtm-address")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
                '//*[contains(@class,"dtm-email")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
                '//*[contains(@class,"dtm-find-location")]/ancestor::*[contains(@class,"MuiCardContent-root")]',

                '//*[contains(normalize-space(text()),"BBB File Opened")]/ancestor::*[contains(@class,"card")]',
                '//*[contains(normalize-space(text()),"Business Started")]/ancestor::*[contains(@class,"card")]',
                '//*[contains(@class,"dtm-address")]/ancestor::*[contains(@class,"card")]',
                '//*[contains(@class,"dtm-email")]/ancestor::*[contains(@class,"card")]',
                '//*[contains(@class,"dtm-find-location")]/ancestor::*[contains(@class,"card")]',
            ]

            detailRoot = None

            for pattern in patterns:
                try:
                    detailRoot = self.driver.find_element(By.XPATH, pattern)
                    break
                except:
                    detailRoot = None

            if detailRoot is None:
                raise Exception("Can not find detailRoot")

            fields_headers = ["Date of New Ownership", "Location of This Business", "BBB File Opened",
                              "Licensing Information", "Service Type", "Menu Type",
                              "Number of Employees", "Years in Business", "Type of Entity", "Accredited Since",
                              "BBB File Opened", "Business Incorporated",
                              "Business Started", "Business Started Locally", "Headquarters",
                              "Location of This Business", "Hours of Operation",
                              "Business Management", "Contact Information", "Customer Contact",
                              "Additional Contact Information", "Fax Numbers",
                              "Serving Area", "Products and Services", "Business Categories", "Alternate Business Name",
                              "Related Businesses", "Email Addresses",
                              "Phone Numbers", "Social Media", "Website Addresses", "Payment Methods",
                              "Referral Assistance", "Refund and Exchange Policy", "Additional Business Information"]
            fields_headers = list(map(lambda x: x.lower(), fields_headers))
            fields_dict = {}

            elements = detailRoot.find_elements(By.CSS_SELECTOR, 'dt, dd')
            lastName = None
            for element in elements:
                # print(element.tag_name + ") " + element.text.strip())
                name = element.text.strip().lower().replace(':', '')
                if element.tag_name == "dt" and name in fields_headers:
                    lastName = name
                    # print("header: " + lastName)
                    if lastName:
                        if lastName not in fields_headers:
                            raise Exception("Unknown field: " + lastName)

                        fields_dict[lastName] = '';
                elif lastName:
                    # print("Append to " + lastName + ": " + element.text)
                    fields_dict[lastName] += element.text

            # print(fields_dict)
            # sys.exit(1)
            if "business started" in fields_dict:
                company.business_started = self.convertDateToOurFormat(fields_dict["business started"])

            if "business incorporated" in fields_dict:
                company.business_incorporated = self.convertDateToOurFormat(fields_dict["business incorporated"])

            if "bbb file opened" in fields_dict:
                company.bbb_file_opened = self.convertDateToOurFormat(fields_dict["bbb file opened"])

            if "accredited since" in fields_dict:
                company.accredited_since = self.convertDateToOurFormat(fields_dict["accredited since"])

            if "type of entity" in fields_dict:
                company.type_of_entity = fields_dict["type of entity"]

            if "years in business" in fields_dict:
                company.years_in_business = fields_dict["years in business"]

            if "number of employees" in fields_dict:
                company.number_of_employees = fields_dict["number of employees"]

            # print(fields_dict)
            if "hours of operation" in fields_dict:
                working_hours_dict = {}
                days_mapping = {"M:": "monday",
                                "T:": "tuesday",
                                "W:": "wednesday",
                                "Th:": "thursday",
                                "F:": "friday",
                                "Sa:": "saturday",
                                "Su:": "sunday",
                                }
                fields_dict["hours of operation"] = fields_dict["hours of operation"].replace(":\n", ": ")
                for line in fields_dict["hours of operation"].strip().split("\n"):
                    first_word = line.split()[0]
                    # print("Line: " + line + ", first_word: " + first_word)
                    if first_word not in days_mapping:
                        continue
                    time_data = "".join(line.split()[1:]).lower()
                    # print("time_data: " + time_data)
                    if time_data == "open24hours":
                        time_data = "open24"
                    elif "-" in time_data:
                        times = time_data.split("-")
                        if len(times) == 2:
                            for time_index in range(2):
                                if "pm" in times[time_index]:
                                    colon_split = times[time_index].split(":")
                                    if len(colon_split) >= 2:
                                        times[time_index] = str(int(colon_split[0]) + 12) + ":" + colon_split[
                                            1].replace("pm", "")
                                    else:
                                        times[time_index] = str(int(colon_split[0]) + 12)
                                times[time_index] = times[time_index].replace("am", "")
                        time_data = "-".join(times)

                    working_hours_dict[days_mapping[first_word]] = time_data.replace(".", "")

                    # may be many hours tables > 1, use only first
                    if len(working_hours_dict) >= 7:
                        break
                company.working_hours = json.dumps(working_hours_dict)
                company.original_working_hours = fields_dict['hours of operation']

            if "business management" in fields_dict:
                company.original_business_management = fields_dict["business management"].strip()
                company.business_management = []
                for line in company.original_business_management.split("\n"):
                    if "," in line:
                        line_split = line.split(",")
                        company.business_management.append(
                            {"type": line_split[1].strip(), "person": line_split[0].strip()})
                company.business_management = json.dumps(company.business_management)

            if "contact information" in fields_dict:
                company.original_contact_information = fields_dict["contact information"].strip()
                company.contact_information = []
                current_type = None
                for line in company.original_contact_information.split("\n"):
                    if "," not in line:
                        current_type = line
                    elif current_type:
                        person = {"name": line.split(",")[0].strip(), "designation": line.split(",")[1].strip()}
                        if company.contact_information and company.contact_information[-1]["type"] == current_type:
                            company.contact_information[-1]["persons"].append(person)
                        else:
                            company.contact_information.append({"type": current_type, "persons": [person]})
                company.contact_information = json.dumps(company.contact_information)

            if "customer contact" in fields_dict:
                company.original_customer_contact = fields_dict["customer contact"].strip()
                company.customer_contact = []
                for line in company.original_customer_contact.split("\n"):
                    if "," in line:
                        line_split = line.split(",")
                        company.customer_contact.append(
                            {"type": line_split[1].strip(), "person": line_split[0].strip()})
                company.customer_contact = json.dumps(company.customer_contact)

            if "fax numbers" in fields_dict:
                fax_lines = fields_dict["fax numbers"].replace("Primary Fax", "").replace("Other Fax", "").replace(
                    "Read More", "").replace("Read Less", "").strip()
                fax_lines = [line for line in fax_lines.split("\n") if line[-3:].isnumeric()]
                print(fax_lines)
                company.fax_numbers = fax_lines[0]
                if len(fax_lines) > 1:
                    company.additional_faxes = "\n".join(fax_lines[1:])

            if "serving area" in fields_dict:
                pattern = r'<.*?>'
                company.serving_area = re.sub(pattern, '',
                                              fields_dict["serving area"].replace("Read More", "").replace("Read Less",
                                                                                                           "").strip()[
                                              :65535])

            if "phone numbers" in fields_dict:
                company.additional_phones = fields_dict["phone numbers"].replace("Read More", "").replace("Read Less",
                                                                                                          "").replace(
                    "Primary Phone", "").replace("Other Phone", "").strip()
                company.additional_phones = "\n".join(
                    [line for line in company.additional_phones.split("\n") if line[-3:].isnumeric()])

            if "website addresses" in fields_dict:
                company.additional_websites = ""
                for url in fields_dict["website addresses"].replace("Read More", "").replace("Read Less",
                                                                                             "").strip().split("\n"):
                    if ("http" in url or "www" in url or ".com" in url) and " " not in url.strip():
                        company.additional_websites += url + "\n"

            if "alternate business name" in fields_dict:
                company.alternate_business_name = fields_dict["alternate business name"].replace("Read More",
                                                                                                 "").replace(
                    "Read Less", "").replace("\n\n", "\n")

            social_media_links = self.driver.find_elements(By.CSS_SELECTOR, ".with-icon.css-1csllio.e13hff4y0")
            for link in social_media_links:
                link_text = link.text.lower().strip()
                if link_text == "facebook":
                    company.facebook = link.get_attribute("href")
                elif link_text == "instagram":
                    company.instagram = link.get_attribute("href")
                elif link_text == "twitter":
                    company.twitter = link.get_attribute("href")
                elif link_text == "pinterest":
                    company.pinterest = link.get_attribute("href")
                elif link_text == "linkedin":
                    company.linkedin = link.get_attribute("href")

            if "payment methods" in fields_dict:
                company.payment_methods = fields_dict["payment methods"].replace("Read More", "").replace("Read Less",
                                                                                                          "").replace(
                    "\n\n", "\n")

            if "referral assistance" in fields_dict:
                company.referral_assistance = fields_dict["referral assistance"].replace("Read More", "").replace(
                    "Read Less", "").replace("\n\n", "\n")

            if "refund and exchange policy" in fields_dict:
                company.refund_and_exchange_policy = fields_dict["refund and exchange policy"].replace("Read More",
                                                                                                       "").replace(
                    "Read Less", "").replace("\n\n", "\n")

            if "business categories" in fields_dict:
                company.business_categories = fields_dict["business categories"].replace("Read More", "").replace(
                    "Read Less", "").replace("\n\n", "\n")

        except Exception as e:
            company.log = "Proxy: " + self.usedProxy + "\n" + traceback.format_exc()

            if not statusMustBeSuccess:
                company.status = "error"
                logging.error(company.log)

        if not company.status:
            company.status = "success"

        if save_to_db:
            if onlyMarkAsSuccess:
                # company 404 but must save old data
                self.db.mark_company_as_success(company.url)
            else:
                self.db.insert_or_update_company(company)

        return company

    def convertDateToOurFormat(self, text):
        # BBB have date problem:
        # https://www.bbb.org/us/ca/tracy/profile/mattress-supplies/zinus-inc-1156-90044368/customer-reviews
        # 02/28/2022
        # https://www.bbb.org/ca/ab/calgary/profile/insurance-agency/bayside-associates-0017-52776/customer-reviews
        # 15/09/2020
        # that's why %m/%d/%Y not work
        try:
            text = text.strip()
            text = re.sub(r'[^0-9/]', '', text)
            return datetime.datetime.strptime(text, "%m/%d/%Y").strftime('%Y-%m-%d')
        except Exception as e:
            pass

        return datetime.datetime.strptime(text, "%d/%m/%Y").strftime('%Y-%m-%d')

    def scrape_company_reviews(self, company_url=None, company_id=None, save_to_db=True, scrape_specific_review=None) -> \
            List[Review]:

        if company_url:
            row = self.db.queryRow("select company_id from company where url = ?", (company_url,))
            if row is None:
                self.scrape_company_details(company_url=company_url, save_to_db=True)
                row = self.db.queryRow("select company_id from company where url = ?", (company_url,))
            if row is None:
                return []

            company_id = row['company_id']

        elif company_id:
            row = self.db.queryRow("select url from company where company_id = ?", (company_id,))
            if row:
                company_url = row['company_url']
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
            review_results = self.db.queryArray("SELECT username, review_date from review where review_id = %s",
                                                (scrape_specific_review))

        page = 1
        while True:
            found = False
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, ".bds-button")
                for button in buttons:
                    if button.text.strip().lower() == "load more":
                        self.driver.execute_script("arguments[0].click();", button)
                        found = True
                        break
                if not found:
                    break
                page = page + 1
                logging.info("Reviews pages: " + str(page) + ", url: " + company_url)
                time.sleep(2)
            except Exception as e:
                break

        try:
            review_tags = self.driver.find_elements(By.XPATH,
                                                    '//*[contains(@class,"dtm-review")]/ancestor::*[contains(@class,"MuiCardContent-root")]')
        except:
            logging.info("No reviews for company: " + company_url)
            return []

        reviews = []

        for review_tag in review_tags:
            review = Review()

            try:
                username = review_tag.find_element(By.CSS_SELECTOR, "h3").text.strip().replace("Review from\n", "")
                if scrape_specific_review and username != review_results[0]["username"]:
                    continue

                if os.getenv('GET_SOURCE_CODE', '0') == "1":
                    review.source_code = review_tag.get_attribute('innerHTML')

                review.company_id = company_id
                review.username = username

                childs = review_tag.find_elements(By.CSS_SELECTOR, ".dtm-review > *")
                if len(childs) < 4:
                    raise Exception("Invalid child elements count")

                if not re.match('^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$', childs[3].text.strip()):
                    raise Exception("Child[3] not date element")

                review.review_date = self.convertDateToOurFormat(childs[3].text.strip())
                if scrape_specific_review and str(review.review_date) != str(review_results[0]["review_date"]):
                    continue

                review.review_rating = round(float(review_tag.find_element(By.XPATH,
                                                                           './/*[contains(@class,"dtm-review")]//*[contains(@class,"visually-hidden") and contains(text(),"star")]').text.split()[
                                                       0]), 1)

                if len(childs) > 4:
                    review.review_text = childs[4].text.strip()
                else:
                    texts = review_tag.find_elements(By.XPATH,
                                                     './/*[contains(@class,"dtm-review")]/following-sibling::*//*[contains(@class,"text-black")]')
                    dates = review_tag.find_elements(By.XPATH,
                                                     './/*[contains(@class,"dtm-review")]/following-sibling::*//*[contains(@class,"text-gray-70")]')

                    review.review_text = texts.pop(0).text.strip()

                    # Fix: https://www.bbb.org/us/ca/marina-del-rey/profile/razors/dollar-shave-club-1216-100113835/customer-reviews
                    # Review begins with in last page: Customer service SUCKS. You can't get in touch with anyone. 
                    # Structure like company response but without it
                    if len(texts):
                        review.company_response_text = texts[0].text.strip()
                        review.company_response_date = self.convertDateToOurFormat(dates[0].text.strip())

                # if review.status == "error":
                # send_message("Error scraping review for company on BBB: " + company_url + "\n" + review.log, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS)
            except Exception as e:
                review.status = "error"
                review.log = traceback.format_exc()

            if not review.status:
                review.status = "success"

            reviews.append(review)

            if scrape_specific_review:
                break

        if save_to_db and reviews:
            self.db.insert_or_update_reviews(reviews)

        return reviews

    def scrape_company_complaints(self, company_url=None, company_id=None, save_to_db=True,
                                  scrape_specific_complaint=None) -> List[Complaint]:

        if company_url:
            row = self.db.queryRow("Select company_id from company where url = %s;", (company_url,))
            if row is None:
                self.scrape_company_details(company_url=company_url, save_to_db=True)
                row = self.db.queryRow("Select company_id from company where url = %s;", (company_url,))
            if row is None:
                return []
            company_id = row["company_id"]

        elif company_id:
            row = self.db.queryRow("Select url from company where company_id = %s;", (company_id,))
            if row:
                company_url = row["company_url"]
            else:
                raise Exception("Company with ID %s does not exist" % str(company_id))
        else:
            raise Exception("Please provide either company URL or company ID")

        if scrape_specific_complaint:
            logging.info("Scraping Complaint with id %s for %s" % (scrape_specific_complaint, company_url))
        else:
            logging.info("Scraping Complaints for " + company_url)

        complaint_url = company_url + "/complaints"

        if scrape_specific_complaint:
            complaint_results = self.db.queryArray(
                "SELECT username, complaint_date from complaint where complaint_id = %s", (scrape_specific_complaint))

        page = 1
        while True:
            # Fix: for complaints?page=N has different url https://www.bbb.org/us/ca/marina-del-rey/profile/razors/dollar-shave-club-inc-1216-100113835/complaints
            # to find correct url, need only click on pagination
            if page == 1:
                logging.info("Scraping Page:  " + complaint_url)
                self.driver.get(complaint_url)
            else:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="/complaints?page=' + str(page) + '"]')
                    logging.info("Scraping Page:  " + element.get_attribute('href'))
                    self.driver.execute_script("arguments[0].click();", element)
                except Exception as e:
                    break

            complaints = []

            try:
                complaint_tags = self.driver.find_elements(By.XPATH, "//li[@id]")
            except:
                break

            if not complaint_tags:
                break

            for complaint_tag in complaint_tags:
                complaint = Complaint()

                try:
                    if os.getenv('GET_SOURCE_CODE', '0') == "1":
                        complaint.source_code = complaint_tag.get_attribute('innerHTML')

                    complaint.company_id = company_id
                    complaint.complaint_type = complaint_tag.find_element(By.XPATH,
                                                                          './/*[normalize-space(text())="Complaint Type:"]/following-sibling::*').text.strip()
                    complaint.complaint_date = self.convertDateToOurFormat(
                        complaint_tag.find_element(By.XPATH, './/h3/following-sibling::*').text.strip())
                    complaint.complaint_text = complaint_tag.find_element(By.XPATH,
                                                                          './/*[@data-body]/div[1]').text.strip()

                    if scrape_specific_complaint and (
                            complaint.complaint_type != complaint_results[0]["complaint_type"] or str(
                        complaint.complaint_date) != str(
                        complaint_results[0]["complaint_date"]) or complaint.complaint_text != complaint_results[0][
                                "complaint_text"]):
                        continue

                    try:
                        # Googd response hierarchy: https://www.bbb.org/us/ca/monrovia/profile/telecommunications/onesuite-corporation-1216-13050632/complaints
                        complaint.company_response_date = self.convertDateToOurFormat(
                            complaint_tag.find_element(By.XPATH, './/h4/following-sibling::*').text.strip())
                        complaint.company_response_text = complaint_tag.find_element(By.XPATH,
                                                                                     './/*[@data-body]/div[2]//*[@data-body]').text.strip()
                    except:
                        pass
                except Exception as e:
                    complaint.status = "error"
                    complaint.log = traceback.format_exc()

                if not complaint.status:
                    complaint.status = "success"

                complaints.append(complaint)

                if scrape_specific_complaint:
                    break

            if save_to_db and complaints:
                self.db.insert_or_update_complaints(complaints)

            page += 1

        return complaints

    def loadUrl(self, url):
        for i in range(3):
            if not self.lastValidProxy:
                logging.info("Find proxy...")
                self.lastValidProxy = getProxy()

            logging.info("Create browser")
            self.createBrowser(None, self.lastValidProxy['proxy'], self.lastValidProxy['proxy_port'],
                               self.lastValidProxy['proxy_user'], self.lastValidProxy['proxy_pass'],
                               self.lastValidProxy['proxy_type'])

            try:
                logging.info("Load: " + url)
                self.driver.get(url)
                logging.info("Loaded: SUCCESS")
                return self.driver.page_source
            except Exception as e:
                self.lastValidProxy = None
                logging.error(e)
            finally:
                self.kill_chrome()

        raise Exception("Can not create browser")

    def addNewUrls(self):
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

    def bulk_scrape(self, no_of_threads=1, scrape_reviews_and_complaints=True):

        sitemap_urls = ["https://www.bbb.org/sitemap-accredited-business-profiles-index.xml",
                        "https://www.bbb.org/sitemap-business-profiles-index.xml"]
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
                        processes.append(Process(target=self.scrape_urls_from_queue,
                                                 args=(urls_to_scrape, scrape_reviews_and_complaints,)))
                        processes[i].start()

                    for i in range(no_of_threads):
                        processes[i].join()
                else:
                    for company_url in urls_to_scrape:
                        self.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints)

    def scrape_urls_from_queue(self, q, scrape_reviews_and_complaints=True, set_rescrape_setting=False):

        try:
            proxy = getProxy()
            scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'],
                                 proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])

            while q.qsize():
                company_url = q.get()
                scraper.scrape_url(company_url, scrape_reviews_and_complaints=scrape_reviews_and_complaints,
                                   set_rescrape_setting=set_rescrape_setting)

        except:
            pass

        try:
            scraper.kill_chrome()
        except:
            pass

    def _get_first_with_text(self, elements, get_href=False):
        for element in elements:
            elem_text = element.text.strip()
            if elem_text != "":
                if get_href:
                    return element.get_attribute("href")
                return elem_text
        return None

    def kill_chrome(self):
        try:
            self.driver.quit()
            if os.name != "nt":
                self.display.stop()
        except:
            pass
        finally:
            self.driver = None


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="BBBScraper CLI to grab company and reviews from URL")
    parser.add_argument("--bulk_scrape", nargs='?', type=str, default="False",
                        help="Boolean variable to bulk scrape companies. Default False. If set to True, save_to_db will also be set to True")
    parser.add_argument("--urls", nargs='*', help="url(s) for scraping. Separate by spaces")
    parser.add_argument("--save_to_db", nargs='?', type=str, default="False",
                        help="Boolean variable to save to db. Default False")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument("--log_file", nargs='?', type=str, default=None,
                        help="Path for log file. If not given, output will be printed on stdout.")
    parser.add_argument("--urls_from_file", nargs='?', type=str, default=None, help="Load urls from file")
    parser.add_argument("--grabber-bbb-mustansir", nargs='?', type=bool, default=False, help="Only mark to kill all")
    parser.add_argument("--proxy", nargs='?', type=str, default=None, help="Set proxy for scan")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    # setup logging based on arguments
    logging.basicConfig(handlers=[
        logging.FileHandler("logs/scrape.py.log"),
        logging.StreamHandler()
    ], format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

    if args.proxy:
        logging.info("Try use proxy: " + args.proxy)

    scraper = BBBScraper()

    if str2bool(args.bulk_scrape):
        scraper.bulk_scrape(no_of_threads=args.no_of_threads)
    else:
        if args.urls_from_file is not None:
            lines = open(args.urls_from_file).readlines()
            lines = map(lambda x: x.strip(), lines)
            lines = list(filter(None, lines))

            if args.urls is None:
                args.urls = []

            for line in lines:
                args.urls.append(line)

        scraper.reloadBrowser(args.proxy)

        for url in args.urls:
            company = scraper.scrape_company_details(company_url=url, save_to_db=str2bool(args.save_to_db))
            logging.info("Company Details for %s scraped successfully.\n" % company.name)

            if company.status == "success":
                # need use company.url because url may be changed
                company.reviews = scraper.scrape_company_reviews(company_url=company.url,
                                                                 save_to_db=str2bool(args.save_to_db))
                company.complaints = scraper.scrape_company_complaints(company_url=company.url,
                                                                       save_to_db=str2bool(args.save_to_db))
                logging.info("Complaints and reviews scraped successfully.\n")

    scraper.kill_chrome()
