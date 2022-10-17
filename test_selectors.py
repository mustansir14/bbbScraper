from scrape import BBBScraper
from config import *
from includes.telegram_reporter import send_message
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS, proxy_type=PROXY_TYPE)
company = scraper.scrape_url("https://www.bbb.org/us/ca/mountain-view/profile/trademark-attorney/trademarkia-1216-1000005153", save_to_db=False)

if company.status == "error":
    send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\n" + company.log)

attributes = [a for a in dir(company) if not a.startswith('__') and not callable(getattr(company, a))]

for attribute in attributes:
    if attribute == "log":
        continue
    if getattr(company, attribute) is None:
        send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\nCompany Details: " + attribute + " not found!")

if company.reviews:
    attributes = [a for a in dir(company.reviews[0]) if not a.startswith('__') and not callable(getattr(company.reviews[0], a))]
    errors_done = []
    fields_not_in_all = ["company_response_text", "company_response_date"]
    fields_found = [False for _ in range(len(fields_not_in_all))]
    for review in company.reviews:

        if review.status == "error":
            send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\nReview: " + review.log)
            break

        for attribute in attributes:
            if attribute == "log":
                continue

            if attribute in fields_not_in_all:
                if getattr(review, attribute):
                    fields_found[fields_not_in_all.index(attribute)] = True
            elif getattr(review, attribute) is None:
                send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\nReview: " + attribute + " not found!")

    for i in range(len(fields_not_in_all)):
        if not fields_found[i]:
            send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\nReview: " + fields_not_in_all[i] + " not found in any of the reviews!")

if company.complaints:
    attributes = [a for a in dir(company.complaints[0]) if not a.startswith('__') and not callable(getattr(company.complaints[0], a))]
    errors_done = []
    fields_not_in_all = ["company_response_text", "company_response_date"]
    fields_found = [False for _ in range(len(fields_not_in_all))]
    for complaint in company.complaints:

        if complaint.status == "error":
            send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\nComplaint: " + complaint.log)
            break

        for attribute in attributes:
            if attribute == "log":
                continue

            if attribute in fields_not_in_all:
                if getattr(complaint, attribute):
                    fields_found[fields_not_in_all.index(attribute)] = True
            elif getattr(complaint, attribute) is None:
                send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\nComplaint: " + attribute + " not found!")

    for i in range(len(fields_not_in_all)):
        if not fields_found[i]:
            send_message("ERROR IN TESTING SELECTORS SCRIPT:\n\nComplaint: " + fields_not_in_all[i] + " not found in any of the complaints!")


scraper.kill_chrome()
        
            




