import logging
import os
from typing import Any

from undetected_chromedriver import Chrome as ChromeDriver
from includes.browser.BrowserElement import BrowserElement


class Browser:
    proxy: str
    driver: ChromeDriver

    def __init__(self, driver: ChromeDriver):
        self.driver = driver
        self.proxy = ""

    def getId(self) -> str:
        return self.driver.session_id if self.driver else "[DriverRemoved]"

    def getCurrentUrl(self) -> str:
        return self.driver.current_url

    def setProxy(self, proxy: str) -> None:
        self.proxy = proxy

    def getProxy(self) -> str:
        return self.proxy

    def killDriver(self, driver):
        driver.quit()

        # Info: after quite() in `ps aux` | grep chrome will show [chrome] <defunct>
        # its not consume resources, but after 65k server cant create new processes
        # code below waits while child processes closed
        try:
            pid = True
            while pid:
                pid = os.waitpid(-1, os.WNOHANG)
                logging.info("Reaped child: %s" % str(pid))

                # Wonka's Solution to avoid infinite loop cause pid value -> (0, 0)
                try:
                    if pid[0] == 0:
                        pid = False
                except:
                    pass
        except ChildProcessError:
            pass

    def kill(self):
        try:
            if self.driver:
                logging.info("Killing browser #" + self.getId())

                self.killDriver(self.driver)
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

    def executeJS(self, javascriptCode: str, *args) -> Any:
        return self.driver.execute_script(javascriptCode, args)
