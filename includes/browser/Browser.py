import logging
from undetected_chromedriver import Chrome as ChromeDriver
from includes.browser.BrowserElement import BrowserElement


class Browser:
    proxy: str
    driver: ChromeDriver

    def __init__(self, driver: ChromeDriver):
        self.driver = driver
        self.proxy = ""

    def getId(self) -> str:
        return self.driver.session_id

    def setProxy(self, proxy: str) -> None:
        self.proxy = proxy

    def getProxy(self) -> str:
        return self.proxy

    def kill(self):
        try:
            logging.info("Killing browser #" + self.getId())
            self.driver.quit()
        except Exception as e:
            logging.error("Kill browser exception: " + str(e))
        finally:
            self.driver = None

    def getPageSource(self) -> str:
        return self.driver.page_source

    def loadPage(self, pageUrl: str):
        return self.driver.get(pageUrl)

    def getDriver(self) -> object:
        return self.driver

    def getRootElement(self) -> BrowserElement:
        return BrowserElement(self.driver, self.driver)
