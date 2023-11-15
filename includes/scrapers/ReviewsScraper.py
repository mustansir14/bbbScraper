import traceback
import time
from typing import Any

from includes.browser.Browser import Browser
from includes.browser.BrowserElement import BrowserElement
from includes.helpers.CompanyUrlHelper import CompanyUrlHelper
from includes.helpers.TextFormatHelper import TextFormatHelper
from includes.models import Review
from includes.scrapers.AbstractScraper import AbstractScraper
import logging


class ReviewsScraper(AbstractScraper):
    companyId: int

    def __init__(self):
        super().__init__()
        self.companyId = 0

    def setCompanyId(self, companyId: int) -> None:
        self.companyId = companyId

    def scrapeInternal(self, companyUrl: str) -> Any:
        logging.info("Scraping reviews for " + companyUrl)

        if not self.companyId:
            raise Exception("No company id")

        browser = self.getBrowserLoader().loadPage(companyUrl + "/customer-reviews")
        totalPages = 1

        page = 0
        while page < totalPages:
            page += 1

            if not browser:
                logging.info("No browser for url, break")
                return

            apiUrl = ('https://www.bbb.org/api/businessprofile/customerreviews?page=' + str(page)
                      + '&pageSize=10'
                      + '&businessId=' + CompanyUrlHelper.getBusinessId(companyUrl)
                      + '&bbbId=' + CompanyUrlHelper.getBbbId(companyUrl)
                      + '&sort=reviewDate%20desc,%20id%20desc'
                      )

            logging.info(str(page) + "/" + str(totalPages) + ") Call api: " + apiUrl + ", wait response...")

            data = self.getReviewsApiRequest(browser, apiUrl)
            if not data:
                logging.info("No data from api, skip")
                continue

            totalPages = data['totalPages']

            if self.scrapeReviews(data['items']) == 0:
                break

        return None

    def getReviewsApiRequest(self, browser, apiUrl: str) -> dict | None:
        jsCode = '''
                    (function () {
                        window.reviewsResponse = null;

                        fetch('{url}')
                            .then(function(response) { 
                                return response.json();
                            })
                            .then(function (json) {
                                window.reviewsResponse = json;
                            });
                    })();
                    '''.strip()

        jsCode = jsCode.replace('{url}', apiUrl)
        browser.executeJS(jsCode)

        for i in range(15):
            response = browser.executeJS('return window.reviewsResponse')
            if response is not None:
                if "items" not in response:
                    raise Exception("Unknown response from api")

                return response

            time.sleep(1)

        return None

    def scrapeReviews(self, items: list) -> int:
        if len(items) == 0:
            logging.info("No items, skip")
            return 0

        reviewsList = []

        for item in items:
            review = self.createReviewFromItem(item)
            reviewsList.append(review)

            self.printReview(review)

        self.db.insert_or_update_reviews(reviewsList)

        return len(reviewsList)

    def printReview(self, review: Review) -> None:
        if review.status == "success":
            logging.info(
                "[" + review.status + "] " + review.username + " (" + review.review_date + ") with " + review.review_rating + " star: " +
                self.textExample(review.review_text)
            )

            if review.company_response_date:
                logging.info(
                    "    => Response " + review.company_response_date + ": " +
                    self.textExample(review.company_response_text)
                )
        else:
            logging.info("[" + review.status + "]: " + review.log)

    def createReviewFromItem(self, item) -> Review | None:
        review = Review()

        try:
            review.status = "success"
            review.company_id = self.companyId
            review.source_code = str(item)
            review.review_rating = str(item['reviewStarRating'])
            review.username = item['displayName']
            review.review_text = TextFormatHelper.html2text(item['text'])
            review.review_date = self.formateDateFromArray(item["date"])

            if item["hasExtendedText"]:
                # sometimes used item.text or item.text = null and item.extendedText[0].text = 'value'
                if not review.review_text:
                    review.review_text = TextFormatHelper.html2text(item["extendedText"][0]['text'])

                for extItem in item['extendedText']:
                    if extItem["isBusiness"]:
                        review.company_response_date = self.formateDateFromArray(extItem["date"])
                        review.company_response_text = TextFormatHelper.html2text(extItem['text'])
                        break
        except Exception:
            logging.error("Review exception: " + traceback.format_exc())

            review.status = "error"
            review.log = traceback.format_exc()

        return review

    def formateDateFromArray(self, item: dict):
        return str(item["year"]) + "-" + str(item["month"]) + "-" + str(item["day"])
