##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from config import *
from typing import List
from includes.models import *
import datetime
if USE_MARIA_DB:
    import mariadb
else:
    import pymysql
import logging
import time

class DB:

    def __init__(self):
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.db = DB_NAME
        if USE_MARIA_DB:
            self.con = mariadb.connect(host=self.host, user=self.user, password=self.password, db=self.db)
        else:
            self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def insert_or_update_company(self, company : Company):
        while True:
            try:
                self.cur.execute("SELECT company_id from company where url = %s;", (company.url,))
                fetched_results = self.cur.fetchall()
                if len(fetched_results) == 1:
                    if USE_MARIA_DB:
                        company_id = fetched_results[0][0]
                    else:
                        company_id = fetched_results[0]["company_id"]
                    sql = """UPDATE company set company_name = %s, url = %s, logo = %s, categories = %s, phone = %s, address = %s, 
                    website = %s, is_accredited = %s, rating = %s, working_hours = %s, number_of_stars = %s, number_of_reviews = %s, 
                    overview = %s, products_and_services = %s, business_started = %s, business_incorporated = %s, type_of_entity = %s,
                    number_of_employees = %s, business_management = %s, contact_information = %s, customer_contact = %s, 
                    fax_numbers = %s, serving_area = %s, date_updated = %s, status = %s, log = %s where company_id = %s;"""
                    args = (company.name, company.url, company.logo, company.categories, company.phone, company.address, 
                    company.website, company.is_accredited, company.rating, company.working_hours, company.number_of_stars, 
                    company.number_of_reviews, company.overview, company.products_and_services, company.business_started, 
                    company.business_incorporated, company.type_of_entity, company.number_of_employees, company.business_management, 
                    company.contact_information, company.customer_contact, company.fax_numbers, company.serving_area, 
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), company.status, company.log, company_id)
                    success_statement = "Company " + company.name + " details updated successfully!"
                else:
                    sql = """INSERT INTO company (company_name, url, logo, categories, phone, address, website, is_accredited, 
                    rating, working_hours, number_of_stars, number_of_reviews, overview, products_and_services, business_started, 
                    business_incorporated, type_of_entity, number_of_employees, business_management, contact_information, 
                    customer_contact, fax_numbers, serving_area, date_created, date_updated, status, log) VALUES (""" + "%s, " * 26 + "%s);"
                    args = (company.name, company.url, company.logo, company.categories, company.phone, company.address, 
                    company.website, company.is_accredited, company.rating, company.working_hours, company.number_of_stars, 
                    company.number_of_reviews, company.overview, company.products_and_services, company.business_started, 
                    company.business_incorporated, company.type_of_entity, company.number_of_employees, company.business_management, 
                    company.contact_information, company.customer_contact, company.fax_numbers, company.serving_area, 
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    company.status, company.log)
                    success_statement = "Company " + company.name + " details added to DB successfully!"
                self.cur.execute(sql, args)
                self.con.commit()
                logging.info(success_statement)
                break
            except Exception as e:
                logging.error(e)
                for i in range(3):
                    logging.info("Reconnecting after 10 seconds")
                    time.sleep(10)
                    try:
                        if USE_MARIA_DB:
                            self.con = mariadb.connect(host=self.host, user=self.user, password=self.password, db=self.db)
                        else:
                            self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, cursorclass=pymysql.cursors.DictCursor)
                        success = True
                        self.cur = self.con.cursor()
                        break
                    except Exception as e:
                        logging.error(e)
                        success = False
                if not success:
                    raise Exception(e)


    def insert_or_update_reviews(self, reviews : List[Review]):
        
        while True:
            try:
                for review in reviews:
                    if review.status == None:
                        review.status = "success"
                    self.cur.execute("SELECT review_id from review where company_id = %s and review_date = %s and username = %s;", (review.company_id, review.review_date, review.username))
                    fetched_results = self.cur.fetchall()
                    if len(fetched_results) >= 1:
                        if USE_MARIA_DB:
                            review_id = fetched_results[0][0]
                        else:
                            review_id = fetched_results[0]["review_id"]
                        sql = """UPDATE review SET review_text = %s, review_rating = %s, company_response_text = %s, company_response_date = %s,
                        date_updated = %s , status = %s, log = %s where review_id = %s;"""
                        args = (review.review_text, review.review_rating, review.company_response_text, review.company_response_date,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), review.status, review.log, review_id)
                    else:    
                        sql = "INSERT INTO review VALUES (DEFAULT, " + "%s, " * 10 + "%s);"
                        args = (review.company_id, review.review_date, review.username,review.review_text, review.review_rating, review.company_response_text, 
                        review.company_response_date, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                        review.status, review.log)
                    self.cur.execute(sql, args)
                
                if reviews:
                    self.con.commit()
                    logging.info("Reviews added/updated to DB successfully!")
                break
            
            except Exception as error:
                logging.error(error)
                for i in range(3):
                    logging.info("Reconnecting after 10 seconds")
                    time.sleep(10)
                    try:
                        if USE_MARIA_DB:
                            self.con = mariadb.connect(host=self.host, user=self.user, password=self.password, db=self.db)
                        else:
                            self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, cursorclass=pymysql.cursors.DictCursor)
                        self.cur = self.con.cursor()
                        success = True
                        break
                    except Exception as e:
                        logging.error(e)
                        success = False
                if not success:
                    raise Exception(error)

    def insert_or_update_complaints(self, complaints : List[Complaint], page=None):
        
        while True:
            try:
                for complaint in complaints:
                    if complaint.status == None:
                        complaint.status = "success"
                    self.cur.execute("SELECT complaint_id from complaint where company_id = %s and complaint_date = %s and complaint_type = %s;", (complaint.company_id, complaint.complaint_date, complaint.complaint_type))
                    fetched_results = self.cur.fetchall()
                    if len(fetched_results) >= 1:
                        if USE_MARIA_DB:
                            complaint_id = fetched_results[0][0]
                        else:
                            complaint_id = fetched_results[0]["complaint_id"]
                        sql = """UPDATE complaint SET complaint_type = %s, complaint_text = %s, company_response_text = %s, company_response_date = %s,
                        date_updated = %s , status = %s, log = %s where complaint_id = %s;"""
                        args = (complaint.complaint_type, complaint.complaint_text, complaint.company_response_text, complaint.company_response_date,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), complaint.status, complaint.log, complaint_id)
                    else:    
                        sql = "INSERT INTO complaint VALUES (DEFAULT, " + "%s, " * 9 + "%s);"
                        args = (complaint.company_id, complaint.complaint_type, complaint.complaint_date, complaint.complaint_text, complaint.company_response_text, 
                        complaint.company_response_date, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                        complaint.status, complaint.log)
                    self.cur.execute(sql, args)
                
                if complaints:
                    self.con.commit()
                    logging.info("Complaints added/updated to DB successfully!")
                break
            
            except Exception as error:
                logging.error(error)
                for i in range(3):
                    logging.info("Reconnecting after 10 seconds")
                    time.sleep(10)
                    try:
                        if USE_MARIA_DB:
                            self.con = mariadb.connect(host=self.host, user=self.user, password=self.password, db=self.db)
                        else:
                            self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, cursorclass=pymysql.cursors.DictCursor)
                        self.cur = self.con.cursor()
                        success = True
                        break
                    except Exception as e:
                        logging.error(e)
                        success = False
                if not success:
                    raise Exception(error)

    

    def __del__(self):
        self.con.close()