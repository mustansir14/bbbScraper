import logging
import time
import traceback

import undetected_chromedriver as uc

from includes.browser.Browser import Browser
from includes.browser.DriverBinary import DriverBinary
from includes.browser.DriverOptions import DriverOptions
from includes.proxies import getProxy
from includes.browser.DriverDumpsCleaner import DriverDumpsCleaner

from includes.browser.DriverUrlsBlocker import DriverUrlsBlocker


class Driver:
    binary: DriverBinary
    urlsBlocker: DriverUrlsBlocker
    options: DriverOptions
    dumpsCleaner: DriverDumpsCleaner
    chromeVersion: int
    browser: None

    def __init__(self):
        self.browser = None
        self.dumpsCleaner = DriverDumpsCleaner()
        self.options = DriverOptions()
        self.urlsBlocker = DriverUrlsBlocker()
        self.binary = DriverBinary()

    def createDriver(self, proxy: str):
        driver = uc.Chrome(
            options=self.options.create(proxy),
            version_main=self.binary.getVersion(),
            driver_executable_path=self.binary.getBinary()
        )

        self.urlsBlocker.set(driver)

        return driver

    def createBrowser(self) -> Browser:
        self.dumpsCleaner.clean()

        proxy = getProxy()
        proxy = proxy['proxy'] + ":" + proxy['proxy_port']

        try:
            driver = self.createDriver(proxy)
        except Exception:
            logging.error("Create driver exception: " + traceback.format_exc())

            time.sleep(3)

            driver = self.createDriver(proxy)

        browser = Browser(driver)
        browser.setProxy(proxy)

        logging.info("Browser #" + browser.getId() + " created with proxy: " + proxy)

        return browser

    def createBrowserSingleton(self) -> Browser:
        if self.browser:
            self.browser.kill()
            self.browser = None

        self.browser = self.createBrowser()

        return self.browser
