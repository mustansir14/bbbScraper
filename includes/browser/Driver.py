import os
import logging
from pyvirtualdisplay import Display
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
    display: None
    browser: None

    def __init__(self):
        self.browser = None
        self.display = None
        self.dumpsCleaner = DriverDumpsCleaner()
        self.options = DriverOptions()
        self.urlsBlocker = DriverUrlsBlocker()
        self.binary = DriverBinary()

    def createBrowser(self) -> Browser:
        self.dumpsCleaner.clean()

        proxy = getProxy()
        proxy = proxy['proxy'] + ":" + proxy['proxy_port']

        driver = uc.Chrome(
            options=self.options.create(proxy),
            version_main=self.binary.getVersion(),
            driver_executable_path=self.binary.getBinary()
        )

        self.urlsBlocker.set(driver)

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
