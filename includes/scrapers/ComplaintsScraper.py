import traceback

from includes.browser.Browser import Browser
from includes.browser.BrowserElement import BrowserElement
from includes.models import Complaint
from includes.scrapers.AbstractScraper import AbstractScraper
import logging


class ComplaintsScraper(AbstractScraper):
    companyId: int

    def __init__(self):
        super().__init__()
        self.companyId = 0

    def setCompanyId(self, companyId: int) -> None:
        self.companyId = companyId

    def scrapeInternal(self, companyUrl: str) -> None:
        logging.info("Scraping Complaints for " + companyUrl)

        if not self.companyId:
            raise Exception("No company id")

        self.browserLoader.setFirstPage(companyUrl + "/complaints")

        for page in range(1, 1000):
            if page == 1:
                browser = self.browserLoader.loadFirstPage()
            else:
                browser = self.browserLoader.loadPage(companyUrl + "/complaints?page=" + str(page))

            if not browser:
                logging.info("No browser for url, break")
                return

            if self.scrapeComplaints(browser) == 0:
                break

    def scrapeComplaints(self, browser: Browser) -> int:
        tags = browser.getRootElement().findXpathAll("//li[@id]")
        if not tags:
            logging.info("No tags, skip")
            return 0

        complaintsList = []

        for tag in tags:
            complaint = self.scrapeCompaintTag(tag)
            complaintsList.append(complaint)

            self.printComplaint(complaint)

        self.db.insert_or_update_complaints(complaintsList)

        return len(complaintsList)

    def printComplaint(self, complaint: Complaint) -> None:
        if complaint.status == "success":
            logging.info(
                "[" + complaint.status + "] " + complaint.complaint_type + " (" + complaint.complaint_date + "): " +
                self.textExample(complaint.complaint_text)
            )

            if complaint.company_response_date:
                logging.info(
                    "    => Response " + complaint.company_response_date + ": " +
                    self.textExample(complaint.company_response_text)
                )
        else:
            logging.info("[" + complaint.status + "]: " + complaint.log)

    def scrapeCompaintTag(self, tag) -> Complaint | None:
        complaint = Complaint()

        try:
            complaint.status = "success"
            complaint.company_id = self.companyId
            complaint.source_code = tag.html()
            complaint.complaint_type = tag.findXpath(
                './/*[normalize-space(text())="Complaint Type:"]/following-sibling::*').textStriped()
            complaint.complaint_text = tag.findXpath('.//*[@data-body]/div[1]').textStriped()
            complaint.complaint_date = self.convertDateToOurFormat(
                tag.findXpath('.//h3/following-sibling::*').textStriped()
            )

            self.scrapeResponse(complaint, tag)
        except Exception:
            logging.error("Complaint exception: " + traceback.format_exc())

            complaint.status = "error"
            complaint.log = traceback.format_exc()

        return complaint

    def scrapeResponse(self, complaint: Complaint, tag: BrowserElement):
        try:
            # May be many responses how in chat
            # https://www.bbb.org/ca/ab/edmonton/profile/legal-forms/lawdepot-tm-0117-134065/complaints

            responses = tag.findXpathAll('.//h4/parent::*[@data-title]/parent::*')

            # need reverse because order is oldest -> newest, take latest
            for response in reversed(responses):
                type = response.findXpath('.//h4').textStriped()
                date = response.findXpath('.//h4/following-sibling::*').textStriped()
                text = response.findXpath('.//*[@data-body]').textStriped()

                if "business response" in type.lower():
                    complaint.company_response_text = text
                    complaint.company_response_date = self.convertDateToOurFormat(date)

                    break

        except Exception:
            logging.error("Complaint response exception: " + traceback.format_exc())
