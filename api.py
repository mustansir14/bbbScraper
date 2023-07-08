##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from flask import Flask, json, request, send_file
from multiprocessing import Process
import time, re
import requests, os
from scrape import BBBScraper
from includes.proxies import getProxy
from sys import platform
from os.path import exists
from includes.DB import DB
import logging
from logging.handlers import RotatingFileHandler

rfh = RotatingFileHandler(
    filename="logs/api.py.log", 
    mode='a',
    maxBytes=20*1024*1024,
    backupCount=1,
    delay=0,
    encoding=None
)
rfh.setFormatter(logging.Formatter('%(asctime)s Process ID %(process)d: %(message)s'))
rfh.setLevel(level=logging.DEBUG)

root = logging.getLogger('root')
root.setLevel(logging.INFO)
root.addHandler(rfh)

api = Flask(__name__)

def response( errors, data = None):
    isFail = True if isinstance(errors,list) and len(errors) > 0 else False
    errors = errors if isinstance(errors,list) else []
    return json.dumps( { 'success': ( not isFail ), 'errors': errors, 'data': ( None if isFail else data ) }, default=str )
    
@api.route('/api/v1/company/rating', methods = ['GET'])
def getCompanyRating():
    companyUrl = request.args["url"].strip() if "url" in request.args else ""
    if not companyUrl:
        return response(["Url parameter required"])
        
    db = DB()
    
    companyRow = db.queryRow("select company_id, status, rating from company where url = ?", (companyUrl, ))
    if not companyRow:
        return response(["No company in database"])
        
    if companyRow['status'] == 'error':
        return response(["Company not scraped successfully"])
        
    if not companyRow['rating']:
        return response(["No rating data"])
        
    return response([], companyRow['rating'])

@api.route('/api/v1/scrape/company', methods=['GET'])
def grab_company():

    def scrape_company(company_id, webhook_url, is_sync):

        try:
            proxy = getProxy()
            scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'], proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])
            if "http" in company_id:
                company = scraper.scrape_company_details(company_url=company_id)
                company.reviews = scraper.scrape_company_reviews(company_url=company_id)
                company.complaints = scraper.scrape_company_complaints(company_url=company_id)
            else:
                company = scraper.scrape_company_details(company_id=company_id)
                company.reviews = scraper.scrape_company_reviews(company_id=company_id)
                company.reviews = scraper.scrape_company_complaints(company_id=company_id)
            
            status = company.status
            log = company.log
            if company.status == "success":
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
                    return response( [], data= f"{company.name} with {len(company.reviews)} reviews and {len(company.complaints)} complaints." )
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
        proxy = getProxy()
        scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'], proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])
            
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
        proxy = getProxy()
        scraper = BBBScraper(proxy=proxy['proxy'], proxy_port=proxy['proxy_port'], proxy_user=proxy['proxy_user'], proxy_pass=proxy['proxy_pass'], proxy_type=proxy['proxy_type'])
        
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
    if "url" not in request.args or len( request.args["url"] ) == 0:
        return json.dumps({"error" : "missing url argument"})
        
    db = DB()
    errors = []
        
    sql = 'select * from company where url=%s limit 1'
    
    rows = db.queryArray( sql, (request.args["url"],))
    if rows is None:
        errors.append( "Internal error" )
        
    return response( errors, rows )
    
@api.route('/api/v1/file', methods=['GET'])
def flush_file():
    if "type" not in request.args or len( request.args["type"] ) == 0:
        return json.dumps({"error" : "missing type argument"})
        
    if not request.args["type"] in ['logo']:
        return json.dumps({"error" : "type invalid"})
        
    if "name" not in request.args or len( request.args["name"] ) == 0:
        return json.dumps({"error" : "missing name argument"})
        
    if not re.match( r'^[a-zA-Z0-9_\&\#\$\.]{1,}$', request.args["name"] ):
        return json.dumps({"error" : "name invalid"})
        
    path = os.path.dirname(os.path.realpath(__file__)) + "/file/logo/" + request.args["name"]
    
    if not exists(path):
        return json.dumps({"error" : "file not exists"})
        
    return send_file(path, as_attachment=True)
    
@api.route('/api/v1/stats', methods=['GET'])
def stats_for_day():
    if "date" not in request.args:
        return json.dumps({"error" : "missing date argument"})
        
    db = DB()
    errors = []
        
    sql = """select 
    d.dt as date, 
    (select count(*) from company where date_updated between concat(d.dt, " 00:00:00") and concat(d.dt, " 23:59:59") and status = 'success') as company_success, 
    (select count(*) from company where date_updated between concat(d.dt, " 00:00:00") and concat(d.dt, " 23:59:59") and status <> 'success') as company_error,
    (select count(*) from review where date_updated between concat(d.dt, " 00:00:00") and concat(d.dt, " 23:59:59") and status = 'success') as review_success, 
    (select count(*) from review where date_updated between concat(d.dt, " 00:00:00") and concat(d.dt, " 23:59:59") and status <> 'success') as review_error,
    (select count(*) from complaint where date_updated between concat(d.dt, " 00:00:00") and concat(d.dt, " 23:59:59") and status = 'success') as complaint_success, 
    (select count(*) from complaint where date_updated between concat(d.dt, " 00:00:00") and concat(d.dt, " 23:59:59") and status <> 'success') as complaint_error
from (
    select ? dt
) d"""
    
    row = db.queryRow( sql, (request.args["date"],))
    if row is None:
        errors.append( "Internal error" )
        
    return response( errors, row )
    
if __name__ == "__main__":
    api.run(host='0.0.0.0',port=5000)