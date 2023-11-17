##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from flask import Flask, json, request, send_file
from multiprocessing import Process
import time, re
import requests, os

from includes.loaders.DisplayLoader import DisplayLoader
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
    display = DisplayLoader()

    try:
        display.start()

        api.run(host='0.0.0.0',port=3060)
    finally:
        display.stop()