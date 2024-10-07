import json
import logging
import pprint
import re
import traceback
from typing import Any

from includes.browser.Browser import Browser
from includes.browser.BrowserElement import BrowserElement
from includes.helpers.DateHelper import DateHelper
from includes.models import Company
from includes.parsers.ScriptTagParser import ScriptTagParser
from includes.scrapers.AbstractScraper import AbstractScraper


class CompanyDetailsScraper(AbstractScraper):

    def __init__(self):
        super().__init__()

        self.company = None

    def setCompany(self, company: Company):
        self.company = company

    def scrapeInternal(self, companyUrl: str) -> Any:
        if not self.company:
            raise Exception("No company")

        browser = self.browserLoader.loadPage(companyUrl + "/details")
        if not browser:
            raise Exception("Can not load details page")

        self.company.source_code_details = browser.getPageSource()

        detailRoot = self.getDetailsRoot(browser)
        self.parseDetailRoot(browser, detailRoot)

        return True

    def parseDetailRoot(self, browser: Browser, detailRoot: BrowserElement):

        companyPreloadState = ScriptTagParser.getScriptVar(browser.getPageSource(), '__PRELOADED_STATE__')
        if not companyPreloadState:
            raise Exception("No preload state")

        businessProfile = companyPreloadState['businessProfile']

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

        elements = detailRoot.findAll('dt, dd')
        lastName = None
        for element in elements:
            try:
                name = element.textStriped().lower().replace(':', '')
                tag = element.getTag()
                text = element.text()
            except:
                continue

            if tag == "dt" and name in fields_headers:
                lastName = name
                # print("header: " + lastName)
                if lastName:
                    if lastName not in fields_headers:
                        raise Exception("Unknown field: " + lastName)

                    fields_dict[lastName] = ''
            elif lastName:
                # print("Append to " + lastName + ": " + element.text)
                fields_dict[lastName] += text

        if "business started" in fields_dict:
            self.company.business_started = DateHelper.bbbDate2mariadb(fields_dict["business started"])

        if "business incorporated" in fields_dict:
            self.company.business_incorporated = DateHelper.bbbDate2mariadb(fields_dict["business incorporated"])

        if "bbb file opened" in fields_dict:
            self.company.bbb_file_opened = DateHelper.bbbDate2mariadb(fields_dict["bbb file opened"])

        if "accredited since" in fields_dict:
            self.company.accredited_since = DateHelper.bbbDate2mariadb(fields_dict["accredited since"])

        if "type of entity" in fields_dict:
            self.company.type_of_entity = fields_dict["type of entity"]

        if "years in business" in fields_dict:
            self.company.years_in_business = fields_dict["years in business"]

        if "number of employees" in fields_dict:
            self.company.number_of_employees = fields_dict["number of employees"]

        # print(fields_dict)

        self.getWorkingHours(businessProfile)
        self.getBusinessManagement(fields_dict)
        self.getContactInformation(fields_dict)
        self.getCustomerContact(fields_dict)
        self.getFaxNumbers(fields_dict)
        self.getServingArea(fields_dict)
        self.getPhoneNumbers(fields_dict)
        self.getWebsiteAddress(fields_dict)
        self.getAltBusinessName(fields_dict)
        self.getSocials(browser)
        self.getPaymentMethods(fields_dict)
        self.getReferralAssistance(fields_dict)
        self.getRefundExchangePolicy(fields_dict)
        self.getBusinessCategories(businessProfile)

    def getWorkingHours(self, businessProfile):
        try:
            primary = self.getProfileItem(businessProfile, "location.operatingHours.byId.primary.days.byId")
            if primary:
                short2longName = {
                    "m": "monday",
                    "t": "tuesday",
                    "w": "wednesday",
                    "th": "thursday",
                    "f": "friday",
                    "sa": "saturday",
                    "su": "sunday",
                }

                # normal - https://www.bbb.org/us/nv/las-vegas/profile/electrician/pdq-electric-1086-90048215/details
                # open24 - https://www.bbb.org/us/nh/belmont/profile/rv-repair/kennett-equipment-services-llc-0051-92050352/details
                # multiple, all days, open24
                # https://www.bbb.org/us/la/west-monroe/profile/commercial-air-conditioning-contractors/g-lindsay-enterprises-llc-1015-150332319/details

                result = {}

                for shortDayOfWeek, data in primary.items():
                    dayName = short2longName[shortDayOfWeek]

                    if len(data['hours']) > 0:
                        open = re.search('T([0-9]{1,2}\\:[0-9]{1,2})', data['hours'][0]['openDate']).group(1)
                        close = re.search('T([0-9]{1,2}\\:[0-9]{1,2})', data['hours'][0]['closeDate']).group(1)

                        result[dayName] = open + "-" + close
                    else:
                        result[dayName] = "open24"

                self.company.working_hours = json.dumps(result)
                self.company.original_working_hours = str(primary)
        except Exception as e:
            logging.error(traceback.format_exc())

    def getBusinessManagement(self, fields_dict):
        try:
            if "business management" in fields_dict:
                self.company.original_business_management = fields_dict["business management"].strip()
                self.company.business_management = []
                for line in self.company.original_business_management.split("\n"):
                    if "," in line:
                        line_split = line.split(",")
                        self.company.business_management.append(
                            {"type": line_split[1].strip(), "person": line_split[0].strip()})
                self.company.business_management = json.dumps(self.company.business_management)
        except Exception as e:
            logging.error(traceback.format_exc())

    def getContactInformation(self, fields_dict):
        try:
            if "contact information" in fields_dict:
                self.company.original_contact_information = fields_dict["contact information"].strip()
                self.company.contact_information = []
                current_type = None
                for line in self.company.original_contact_information.split("\n"):
                    if "," not in line:
                        current_type = line
                    elif current_type:
                        person = {"name": line.split(",")[0].strip(), "designation": line.split(",")[1].strip()}
                        if self.company.contact_information and self.company.contact_information[-1][
                            "type"] == current_type:
                            self.company.contact_information[-1]["persons"].append(person)
                        else:
                            self.company.contact_information.append({"type": current_type, "persons": [person]})
                self.company.contact_information = json.dumps(self.company.contact_information)
        except Exception as e:
            logging.error(traceback.format_exc())

    def getCustomerContact(self, fields_dict):
        try:
            if "customer contact" in fields_dict:
                self.company.original_customer_contact = fields_dict["customer contact"].strip()
                self.company.customer_contact = []
                for line in self.company.original_customer_contact.split("\n"):
                    if "," in line:
                        line_split = line.split(",")
                        self.company.customer_contact.append(
                            {"type": line_split[1].strip(), "person": line_split[0].strip()})
                self.company.customer_contact = json.dumps(self.company.customer_contact)
        except Exception as e:
            logging.error(traceback.format_exc())

    def getFaxNumbers(self, fields_dict):
        try:
            if "fax numbers" in fields_dict:
                fax_lines = fields_dict["fax numbers"].replace("Primary Fax", "").replace("Other Fax", "").replace(
                    "Read More", "").replace("Read Less", "").strip()
                fax_lines = [line for line in fax_lines.split("\n") if line[-3:].isnumeric()]
                self.company.fax_numbers = fax_lines[0]
                if len(fax_lines) > 1:
                    self.company.additional_faxes = "\n".join(fax_lines[1:])
        except Exception as e:
            logging.error(traceback.format_exc())

    def getServingArea(self, fields_dict):
        try:
            if "serving area" in fields_dict:
                pattern = r'<.*?>'
                self.company.serving_area = re.sub(pattern, '', fields_dict["serving area"]
                                                   .replace("Read More", "")
                                                   .replace("Read Less", "").strip()[:65535])
        except Exception as e:
            logging.error(traceback.format_exc())

    def getPhoneNumbers(self, fields_dict):
        try:
            if "phone numbers" in fields_dict:
                self.company.additional_phones = (fields_dict["phone numbers"]
                                                  .replace("Read More", "")
                                                  .replace("Read Less", "")
                                                  .replace("Primary Phone", "")
                                                  .replace("Other Phone", "").strip())
                self.company.additional_phones = "\n".join(
                    [line for line in self.company.additional_phones.split("\n") if line[-3:].isnumeric()])
        except Exception as e:
            logging.error(traceback.format_exc())

    def getWebsiteAddress(self, fields_dict):
        try:
            if "website addresses" in fields_dict:
                self.company.additional_websites = ""
                for url in fields_dict["website addresses"].replace("Read More", "").replace("Read Less",
                                                                                             "").strip().split("\n"):
                    if ("http" in url or "www" in url or ".com" in url) and " " not in url.strip():
                        self.company.additional_websites += url + "\n"
        except Exception as e:
            logging.error(traceback.format_exc())

    def getAltBusinessName(self, fields_dict):
        try:
            if "alternate business name" in fields_dict:
                self.company.alternate_business_name = (fields_dict["alternate business name"]
                                                        .replace("Read More", "")
                                                        .replace("Read Less", "")
                                                        .replace("\n\n", "\n"))
        except Exception as e:
            logging.error(traceback.format_exc())

    def getSocials(self, browser):
        try:
            social_media_links = browser.getRootElement().findAll(".with-icon.css-1csllio.e13hff4y0")
            for link in social_media_links:
                link_text = link.text.lower().strip()
                if link_text == "facebook":
                    self.company.facebook = link.get_attribute("href")
                elif link_text == "instagram":
                    self.company.instagram = link.get_attribute("href")
                elif link_text == "twitter":
                    self.company.twitter = link.get_attribute("href")
                elif link_text == "pinterest":
                    self.company.pinterest = link.get_attribute("href")
                elif link_text == "linkedin":
                    self.company.linkedin = link.get_attribute("href")
        except Exception as e:
            logging.error(traceback.format_exc())

    def getPaymentMethods(self, fields_dict):
        try:
            if "payment methods" in fields_dict:
                self.company.payment_methods = (fields_dict["payment methods"]
                                                .replace("Read More", "")
                                                .replace("Read Less", "")
                                                .replace("\n\n", "\n"))
        except Exception as e:
            logging.error(traceback.format_exc())

    def getReferralAssistance(self, fields_dict):
        try:
            if "referral assistance" in fields_dict:
                self.company.referral_assistance = fields_dict["referral assistance"].replace("Read More", "").replace(
                    "Read Less", "").replace("\n\n", "\n")
        except Exception as e:
            logging.error(traceback.format_exc())

    def getRefundExchangePolicy(self, fields_dict):
        try:
            if "refund and exchange policy" in fields_dict:
                self.company.refund_and_exchange_policy = (fields_dict["refund and exchange policy"]
                                                           .replace("Read More", "")
                                                           .replace("Read Less", "")
                                                           .replace("\n\n", "\n"))
        except Exception as e:
            logging.error(traceback.format_exc())

    def getProfileItem(self, businessProfile, path):
        current = businessProfile
        for part in path.split("."):
            if type(current) is not dict:
                return None

            if part not in current:
                return None

            current = current[part]

        return current

    def getBusinessCategories(self, businessProfile):
        try:
            links = self.getProfileItem(businessProfile, "categories.links")
            if links:
                names = []

                for item in links:
                    names.append(item['title'])

                self.company.business_categories = "\n".join(names)
        except Exception as e:
            logging.error(traceback.format_exc())

    def getDetailsRoot(self, browser: Browser) -> BrowserElement:
        # some proxies are from Mexico, and output not english, need more patterns
        patterns = [
            '//*[contains(normalize-space(text()),"BBB File Opened")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
            '//*[contains(normalize-space(text()),"Business Started")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
            '//*[contains(@class,"dtm-address")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
            '//*[contains(@class,"dtm-email")]/ancestor::*[contains(@class,"MuiCardContent-root")]',
            '//*[contains(@class,"dtm-find-location")]/ancestor::*[contains(@class,"MuiCardContent-root")]',

            '//dt[contains(normalize-space(text()),"BBB File Opened")]/ancestor::dl',
            '//dt[contains(normalize-space(text()),"Business Started")]/ancestor::dl',
            '//*[contains(@class,"dtm-address")]/ancestor::dl',
            '//*[contains(@class,"dtm-email")]/ancestor::dl',
            '//*[contains(@class,"dtm-find-location")]/ancestor::dl',
        ]

        for pattern in patterns:
            logging.info("Try search details root with: " + pattern)
            detailRoot = browser.getRootElement().findXpath(pattern)
            if detailRoot:
                return detailRoot

        raise Exception("Can not find detailRoot")
