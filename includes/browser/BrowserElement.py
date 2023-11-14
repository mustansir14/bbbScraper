from typing import Self
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


class BrowserElement:
    element: object

    def __init__(self, driver, element):
        self.driver = driver
        self.element = element

    def click(self):
        self.driver.execute_script("arguments[0].click();", self.element)

    def html(self) -> str:
        return self.element.get_attribute('innerHTML')

    def text(self) -> str:
        # do not use self.element.text it may return empty string, don't know why
        return self.element.get_attribute("innerText")

    def textStriped(self) -> str:
        return self.text().strip()

    def getDriver(self) -> object:
        return self.driver

    def find(self, selector: str) -> Self | None:
        return self.__findSingle(By.CSS_SELECTOR, selector)

    def findXpath(self, selector: str) -> Self | None:
        return self.__findSingle(By.XPATH, selector)

    def findAll(self, selector: str) -> list:
        return self.__findAll(By.CSS_SELECTOR, selector)

    def findXpathAll(self, selector: str) -> list:
        return self.__findAll(By.XPATH, selector)

    def __findSingle(self, type: By, selector: str) -> Self | None:
        try:
            element = self.element.find_element(type, selector)
        except NoSuchElementException as e:
            return None

        return BrowserElement(self.getDriver(), element)

    def __findAll(self, type: By, selector: str) -> list:
        try:
            elements = self.element.find_elements(type, selector)
        except NoSuchElementException as e:
            return []

        elements = list(
            map(
                lambda element: BrowserElement(self.getDriver(), element),
                elements
            )
        )

        return elements

    def __str__(self) -> str:
        return self.html()
