import traceback
from typing import Any

from includes.models import Company
from includes.parsers.CompanyParser import CompanyParser
from includes.scrapers.AbstractScraper import AbstractScraper
from includes.scrapers.CompanyDetailsScraper import CompanyDetailsScraper
import logging


class CompanyScraper(AbstractScraper):
    def scrapeInternal(self, companyUrl: str) -> Any:
        logging.info("Scraping company: " + companyUrl)

        browser = self.getBrowserLoader().loadPage(companyUrl, {
            self.getBrowserLoader().OptionRunCompanyParser: True
        })

        company = self.createCompany(companyUrl)

        if not browser:
            return self.failReturn(company, "No browser, may be banned. Return fail", True)

        if isinstance(browser, int):
            self.db.removeCompanyIfEmpty(companyUrl)
            return self.failReturn(company, "Url not exists anymore, http code " + str(browser))

        # BugFix: original url https://www.bbb.org/us/al/huntsville/profile/business-associations/the-catalyst-center-for-business-entrepreneurship-0513-900075144
        # redirect to: https://www.bbb.org/us/al/huntsville/charity-review/charity-community-development-civic-organizations/the-catalyst-center-for-business-entrepreneurship-0513-900075144
        if "/charity-review/" in browser.getCurrentUrl():
            self.db.removeCompanyByUrl(companyUrl)
            return self.failReturn(company, "Charity review")

        if companyUrl != browser.getCurrentUrl():
            # old url: https://www.bbb.org/us/nd/fargo/profile/bank/bell-bank-0704-96381846
            # new url: https://www.bbb.org/us/mn/saint-louis-park/profile/real-estate-loans/bell-mortgage-0704-96148267

            newUrl = browser.getCurrentUrl().split("?")[0]

            logging.info("Company url changed, move data to new url")
            logging.info("Old url: " + companyUrl)
            logging.info("New url: " + newUrl)

            self.db.move_company_to_other_company(companyUrl, newUrl)

            company.url = newUrl

        try:
            cp = CompanyParser()
            cp.setCompany(company)
            cp.parse(browser.getPageSource())

            # attention company url may be incorrect
            # https://www.bbb.org/us/tx/houston/profile/restaurants/landrys-seafood-1296-90225256/addressId/697351 - addressId
            # https://www.bbb.org/us/co/windsor/profile/electrician/conduct-all-electric-0805-46101614/ - last /
            # that's why company.url may be changed
            if companyUrl != company.url:
                self.db.execSQL("update company set url = ? where url = ?", (company.url, companyUrl,))

            detailsScraper = CompanyDetailsScraper()
            detailsScraper.setBrowserLoader(self.getBrowserLoader())
            detailsScraper.setCompany(company)
            detailsScraper.scrape(company.url)
        except Exception:
            return self.failReturn(company, traceback.format_exc(), True)

        self.db.insert_or_update_company(company)

        return company

    def failReturn(self, company: Company, errorText: str, saveInDb: bool = False) -> Company:
        company.status = "error"
        company.log = errorText

        logging.info("Fail return: " + errorText)

        if saveInDb:
            self.db.insert_or_update_company(company)

        return company

    def createCompany(self, companyUrl: str) -> Company:
        company = Company()
        company.status = "success"
        company.url = companyUrl
        company.half_scraped = None
        company.country = companyUrl.replace("https://www.bbb.org/", "")[:2]

        if company.country not in ['us', 'ca']:
            company.country = None

        return company
