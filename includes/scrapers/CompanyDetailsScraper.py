import json
import logging
import re
from typing import Any

from includes.browser.Browser import Browser
from includes.browser.BrowserElement import BrowserElement
from includes.helpers.DateHelper import DateHelper
from includes.models import Company
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

        with open('details.htm', 'w') as fd:
            fd.write(browser.getPageSource())

        detailRoot = self.getDetailsRoot(browser)
        self.parseDetailRoot(browser, detailRoot)

        return True

    def parseDetailRoot(self, browser: Browser, detailRoot: BrowserElement):
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

        # print(fields_dict)
        # sys.exit(1)
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
            self.company.working_hours = json.dumps(working_hours_dict)
            self.company.original_working_hours = fields_dict['hours of operation']

        if "business management" in fields_dict:
            self.company.original_business_management = fields_dict["business management"].strip()
            self.company.business_management = []
            for line in self.company.original_business_management.split("\n"):
                if "," in line:
                    line_split = line.split(",")
                    self.company.business_management.append(
                        {"type": line_split[1].strip(), "person": line_split[0].strip()})
            self.company.business_management = json.dumps(self.company.business_management)

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

        if "customer contact" in fields_dict:
            self.company.original_customer_contact = fields_dict["customer contact"].strip()
            self.company.customer_contact = []
            for line in self.company.original_customer_contact.split("\n"):
                if "," in line:
                    line_split = line.split(",")
                    self.company.customer_contact.append(
                        {"type": line_split[1].strip(), "person": line_split[0].strip()})
            self.company.customer_contact = json.dumps(self.company.customer_contact)

        if "fax numbers" in fields_dict:
            fax_lines = fields_dict["fax numbers"].replace("Primary Fax", "").replace("Other Fax", "").replace(
                "Read More", "").replace("Read Less", "").strip()
            fax_lines = [line for line in fax_lines.split("\n") if line[-3:].isnumeric()]
            print(fax_lines)
            self.company.fax_numbers = fax_lines[0]
            if len(fax_lines) > 1:
                self.company.additional_faxes = "\n".join(fax_lines[1:])

        if "serving area" in fields_dict:
            pattern = r'<.*?>'
            self.company.serving_area = re.sub(pattern, '',
                                               fields_dict["serving area"].replace("Read More", "").replace("Read Less",
                                                                                                            "").strip()[
                                               :65535])

        if "phone numbers" in fields_dict:
            self.company.additional_phones = fields_dict["phone numbers"].replace("Read More", "").replace("Read Less",
                                                                                                           "").replace(
                "Primary Phone", "").replace("Other Phone", "").strip()
            self.company.additional_phones = "\n".join(
                [line for line in self.company.additional_phones.split("\n") if line[-3:].isnumeric()])

        if "website addresses" in fields_dict:
            self.company.additional_websites = ""
            for url in fields_dict["website addresses"].replace("Read More", "").replace("Read Less",
                                                                                         "").strip().split("\n"):
                if ("http" in url or "www" in url or ".com" in url) and " " not in url.strip():
                    self.company.additional_websites += url + "\n"

        if "alternate business name" in fields_dict:
            self.company.alternate_business_name = fields_dict["alternate business name"].replace("Read More",
                                                                                                  "").replace(
                "Read Less", "").replace("\n\n", "\n")

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

        if "payment methods" in fields_dict:
            self.company.payment_methods = fields_dict["payment methods"].replace("Read More", "").replace("Read Less",
                                                                                                           "").replace(
                "\n\n", "\n")

        if "referral assistance" in fields_dict:
            self.company.referral_assistance = fields_dict["referral assistance"].replace("Read More", "").replace(
                "Read Less", "").replace("\n\n", "\n")

        if "refund and exchange policy" in fields_dict:
            self.company.refund_and_exchange_policy = fields_dict["refund and exchange policy"].replace("Read More",
                                                                                                        "").replace(
                "Read Less", "").replace("\n\n", "\n")

        if "business categories" in fields_dict:
            self.company.business_categories = fields_dict["business categories"].replace("Read More", "").replace(
                "Read Less", "").replace("\n\n", "\n")

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
