from includes.browser.Browser import Browser
from includes.browser.Driver import Driver
from includes.models import Company
from includes.parsers.CompanyParser import CompanyParser
from includes.parsers.Exceptions.PageNotFoundException import PageNotFoundException
from includes.parsers.Exceptions.PageNotLoadedException import PageNotLoadedException
from includes.parsers.Exceptions.PageWoopsException import PageWoopsException
import logging


class BrowserLoader:
    OptionRunCompanyParser = "run_company_parser"

    firstPage: None
    browser: Browser
    driver: Driver

    def __init__(self):
        self.browserCreator = Driver()
        self.browser = None
        self.firstPage = None

    def kill(self):
        if self.browser:
            logging.info("BrowserLoader: kill existing browser")
            self.browser.kill()
        else:
            logging.info("BrowserLoader: no browser, skip")

    def setFirstPage(self, firstPageUrl: str) -> None:
        self.firstPage = firstPageUrl

    def loadFirstPage(self):
        return self.loadPage(self.firstPage)

    def loadPage(self, pageUrl: str, options: dict = {}) -> Browser | int | None:
        if not self.browser:
            self.browser = self.browserCreator.createBrowserSingleton()

        for tryNbr in range(1, 5):
            logging.info(str(tryNbr) + ") Try load " + pageUrl)

            self.browser.loadPage(pageUrl)

            try:
                c = CompanyParser()
                c.checkErrorsPage(self.browser.getPageSource())

                logging.info(str(tryNbr) + ") No errors for return browser")

                if self.OptionRunCompanyParser in options:
                    c.setCompany(Company())
                    c.parse(self.browser.getPageSource())

                return self.browser
            except PageNotFoundException as e:
                logging.info(str(tryNbr) + ") Page not found (" + pageUrl + "), return None")
                return 404
            except (PageNotLoadedException, PageWoopsException) as e:
                logging.info(str(tryNbr) + ") Page error: " + str(e) + ", recreate browser")

                self.browser = self.browserCreator.createBrowserSingleton()

        return None
