##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from flask import Flask, json, request
from multiprocessing import Process
import time
import requests
from scrape import BBBScraper
from sys import platform
from includes.DB import DB
from config import *
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

api = Flask(__name__)

def response( errors, data = None):
    isFail = True if isinstance(errors,list) and len(errors) > 0 else False
    errors = errors if isinstance(errors,list) else []
    return json.dumps( { 'success': ( not isFail ), 'errors': errors, 'data': ( None if isFail else data ) }, default=str )

@api.route('/api/v1/scrape/company', methods=['GET'])
def grab_company():

    def scrape_company(company_id, webhook_url, is_sync):

        try:
            scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS, proxy_type=PROXY_TYPE)
            if "http" in company_id:
                company = scraper.scrape_company_details(company_url=company_id)
                company.reviews = scraper.scrape_company_reviews(company_url=company_id)
                company.complaints = scraper.scrape_company_complaints(company_url=company_id)
            else:
                company = scraper.scrape_company_details(company_id=company_id)
                company.reviews = scraper.scrape_company_reviews(company_id=company_id)
                company.reviews = scraper.scrape_company_complaints(company_id=company_id)
            
            status = "success"
            if company.status == "error":
                status = "error"
                log = "Error in scraping company details"
            else:
                for review in company.reviews:
                    if review.status == "error":
                        status = "error"
                        log = "Error in scraping some of the reviews"
                for complaint in company.complaints:
                    if complaint.status == "error":
                        status = "error"
                        log = "Error in scraping some of the complaints"
            
            scraper.kill_chrome()
                        
            if is_sync == False:
                if status == "success":
                    requests.post(webhook_url, json={"company_id": company_id, "status" : "success"})
                else:
                    requests.post(webhook_url, json={"company_id": company_id, "status" : status, "log": log})
            else:
                if status == "success":
                    return response( [] )
                else:
                    return response( [ log ] )

            
            
        except Exception as e:
            try:
                scraper.kill_chrome()
            except:
                pass
            return response( [ str(e) ] )
        
    if "id" not in request.args:
        return response( [ "missing id argument" ] )
        
    if "sync" not in request.args and "webhookUrl" not in request.args:
        return response( [ "missing webhookUrl argument" ] )
    
    if "webhookUrl" not in request.args:
        webhook = None
    else:
        webhook = request.args["webhookUrl"]
    try:
        
        if "sync" not in request.args and ( platform == "linux" or platform == "linux2" ):
            p = Process(target=scrape_company, args=(request.args["id"], webhook, False, ))
            p.start()
        else:
            return scrape_company(request.args["id"], webhook, "sync" in request.args )
            
    except Exception as e:
        return response( [ str(e) ] )
        
    return response( [], 'pending' )

@api.route('/api/v1/scrape/review', methods=['GET'])
def grab_review():

    def scrape_review(review_id, webhook_url):
        scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS)
        scraper.db.cur.execute("SELECT company_id from review where review_id = %s;", (review_id,))
        company_id = scraper.db.cur.fetchall()[0]["company_id"]
        if "http" in company_id:
            reviews = scraper.scrape_company_reviews(company_url=company_id, scrape_specific_review=review_id)
        else:
            reviews = reviews = scraper.scrape_company_reviews(company_id=company_id, scrape_specific_review=review_id)
        status = "success"
        if reviews:
            if reviews[0].status == "error":
                status = "error"
                log = "Error in scraping review"
        else:
            status = "error"
            log = "No review found with given review_id"
        if status == "success":
            requests.post(webhook_url, json={"review_id": review_id, "status" : "success"})
        else:
            requests.post(webhook_url, json={"review_id": review_id, "status" : status, "log": log})
        
    if "id" not in request.args:
        return json.dumps({"error" : "missing id argument"})
    if "webhookUrl" not in request.args:
        return json.dumps({"error" : "missing webhookUrl argument"})
    if platform == "linux" or platform == "linux2":
        p = Process(target=scrape_review, args=(request.args["id"], request.args["webhookUrl"],))
        p.start()
    else:
        scrape_review(request.args["id"], request.args["webhookUrl"])
    return json.dumps(request.args)

@api.route('/api/v1/scrape/complaint', methods=['GET'])
def grab_complaint():

    def scrape_complaint(complaint_id, webhook_url):
        scraper = BBBScraper(proxy=PROXY, proxy_port=PROXY_PORT, proxy_user=PROXY_USER, proxy_pass=PROXY_PASS)
        scraper.db.cur.execute("SELECT company_id from complaint where complaint_id = %s;", (complaint_id,))
        company_id = scraper.db.cur.fetchall()[0]["company_id"]
        if "http" in company_id:
            complaints = scraper.scrape_company_complaints(company_url=company_id, scrape_specific_complaint=complaint_id)
        else:
            complaints = complaints = scraper.scrape_company_complaints(company_id=company_id, scrape_specific_complaint=complaint_id)
        status = "success"
        if complaints:
            if complaints[0].status == "error":
                status = "error"
                log = "Error in scraping complaint"
        else:
            status = "error"
            log = "No complaint found with given complaint_id"
        if status == "success":
            requests.post(webhook_url, json={"complaint_id": complaint_id, "status" : "success"})
        else:
            requests.post(webhook_url, json={"complaint_id": complaint_id, "status" : status, "log": log})
        
    if "id" not in request.args:
        return json.dumps({"error" : "missing id argument"})
    if "webhookUrl" not in request.args:
        return json.dumps({"error" : "missing webhookUrl argument"})
    if platform == "linux" or platform == "linux2":
        p = Process(target=scrape_complaint, args=(request.args["id"], request.args["webhookUrl"],))
        p.start()
    else:
        scrape_complaint(request.args["id"], request.args["webhookUrl"])
    return json.dumps(request.args)

@api.route('/api/v1/company', methods=['GET'])
def flush_company_data():
    if "name" not in request.args:
        return json.dumps({"error" : "missing name argument"})
        
    db = DB()
    errors = []
        
    sql = 'select * from company where company_name=%s'
    
    rows = db.queryArray( sql, (request.args["name"],))
    if rows is None:
        errors.append( "Internal error" )
        
    return response( errors, rows )

if __name__ == "__main__":
    api.run(host='0.0.0.0',port=5000)