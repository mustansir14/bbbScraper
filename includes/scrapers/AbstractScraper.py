from abc import ABC, abstractmethod
import datetime
import re

from includes.DB import DB
from includes.loaders.BrowserLoader import BrowserLoader
import logging


class AbstractScraper(ABC):
    browserLoader: BrowserLoader
    db: None

    def __init__(self):
        self.db = None
        self.browserLoader = BrowserLoader()

    def setDatabase(self, db: DB) -> None:
        self.db = db

    def textExample(self, text: str) -> str:
        text = text[0:60]
        text = text.replace("\r", "")
        text = text.replace("\n", " ")
        text = text.replace("\t", " ")

        return text + "..."

    def convertDateToDbFormat(self, text):
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

    def scrape(self, companyUrl: str) -> None:
        try:
            self.scrapeInternal(companyUrl)
        finally:
            self.browserLoader.kill()

    @classmethod
    @abstractmethod
    def scrapeInternal(self, companyUrl: str) -> None:
        pass
