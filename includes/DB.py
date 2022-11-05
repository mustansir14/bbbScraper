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
        
    def getDbCursor(self):
        if USE_MARIA_DB:
            return self.con.cursor(dictionary=True)
            
        return self.con.cursor()
    
    def queryArray(self,sql,args):
        cur = self.getDbCursor()
        
        cur.execute( sql,args )
        rows = cur.fetchall()

        cur.close()

        return rows

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
                    sql = """UPDATE company set version = 2, company_name = %s, alternate_business_name = %s, url = %s, logo = %s, categories = %s, phone = %s, address = %s, 
                    street_address = %s, address_locality = %s, address_region = %s, postal_code = %s,
                    website = %s, hq = %s, is_accredited = %s, bbb_file_opened = %s, years_in_business = %s, accredited_since = %s, rating = %s, original_working_hours = %s, working_hours = %s, number_of_stars = %s, number_of_reviews = %s, number_of_complaints = %s, 
                    overview = %s, products_and_services = %s, business_started = %s, business_incorporated = %s, type_of_entity = %s,
                    number_of_employees = %s, original_business_management = %s, business_management = %s, original_contact_information = %s, contact_information = %s, original_customer_contact = %s, customer_contact = %s, 
                    fax_numbers = %s, additional_phones = %s, additional_websites = %s, additional_faxes = %s, serving_area = %s, payment_methods = %s, referral_assistance = %s, refund_and_exchange_policy = %s, business_categories = %s, facebook = %s, instagram = %s, twitter = %s, pinterest = %s, linkedin = %s, date_updated = %s, status = %s, log = %s, half_scraped = %s, country = %s, source_code = %s, source_code_details = %s where company_id = %s;"""
                    args = (company.name, company.alternate_business_name, company.url, company.logo, company.categories, company.phone, company.address,
                    company.street_address, company.address_locality, company.address_region, company.postal_code, 
                    company.website, company.hq, company.is_accredited, company.bbb_file_opened, company.years_in_business, company.accredited_since, company.rating, company.original_working_hours, company.working_hours, company.number_of_stars, 
                    company.number_of_reviews, company.number_of_complaints, company.overview, company.products_and_services, company.business_started, 
                    company.business_incorporated, company.type_of_entity, company.number_of_employees, company.original_business_management, company.business_management, company.original_contact_information,
                    company.contact_information, company.original_customer_contact, company.customer_contact, company.fax_numbers, company.additional_phones, company.additional_websites, company.additional_faxes, company.serving_area, company.payment_methods, company.referral_assistance, company.refund_and_exchange_policy, company.business_categories, company.facebook, company.instagram, company.twitter, company.pinterest, company.linkedin,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), company.status, company.log, company.half_scraped, company.country, company.source_code, company.source_code_details, company_id)
                    success_statement = "Company " + company.name + " details updated successfully!"
                else:
                    sql = """INSERT INTO company (version, company_name, alternate_business_name, url, logo, categories, phone, address, company.street_address, 
                    company.address_locality, company.address_region, company.postal_code, website, hq, is_accredited, bbb_file_opened, years_in_business, accredited_since,
                    rating, original_working_hours, working_hours, number_of_stars, number_of_reviews, number_of_complaints, overview, products_and_services, business_started, 
                    business_incorporated, type_of_entity, number_of_employees, original_business_management, business_management, original_contact_information, contact_information, original_customer_contact,
                    customer_contact, fax_numbers, additional_phones, additional_websites, additional_faxes, serving_area, payment_methods, referral_assistance, refund_and_exchange_policy, business_categories, facebook, instagram, twitter, pinterest, linkedin, source_code, source_code_details, date_created, date_updated, status, log, half_scraped, country) VALUES (2, """ + "%s, " * 56 + "%s);"
                    args = (company.name, company.alternate_business_name, company.url, company.logo, company.categories, company.phone, company.address,
                    company.street_address, company.address_locality, company.address_region, company.postal_code, 
                    company.website, company.hq, company.is_accredited, company.bbb_file_opened, company.years_in_business, company.accredited_since, company.rating, company.original_working_hours, company.working_hours, company.number_of_stars, 
                    company.number_of_reviews, company.number_of_complaints, company.overview, company.products_and_services, company.business_started, 
                    company.business_incorporated, company.type_of_entity, company.number_of_employees, company.original_business_management, company.business_management, company.original_contact_information,
                    company.contact_information, company.original_customer_contact, company.customer_contact, company.fax_numbers, company.additional_phones, company.additional_websites, company.additional_faxes, company.serving_area, company.payment_methods, company.referral_assistance, company.refund_and_exchange_policy, company.business_categories, company.facebook, company.instagram, company.twitter, company.pinterest, company.linkedin, company.source_code, company.source_code_details,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    company.status, company.log, company.half_scraped, company.country)
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
                        sql = """UPDATE review SET review_text = %s, review_rating = %s, company_response_text = %s, company_response_date = %s, source_code = %s,
                        date_updated = %s , status = %s, log = %s where review_id = %s;"""
                        args = (review.review_text, review.review_rating, review.company_response_text, review.company_response_date, review.source_code,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), review.status, review.log, review_id)
                    else:    
                        sql = "INSERT INTO review VALUES (DEFAULT, " + "%s, " * 11 + "%s);"
                        args = (review.company_id, review.review_date, review.username,review.review_text, review.review_rating, review.company_response_text, 
                        review.company_response_date, review.source_code, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
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
                        sql = """UPDATE complaint SET complaint_type = %s, complaint_text = %s, company_response_text = %s, company_response_date = %s, source_code = %s,
                        date_updated = %s , status = %s, log = %s where complaint_id = %s;"""
                        args = (complaint.complaint_type, complaint.complaint_text, complaint.company_response_text, complaint.company_response_date, complaint.source_code,
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), complaint.status, complaint.log, complaint_id)
                    else:    
                        sql = "INSERT INTO complaint VALUES (DEFAULT, " + "%s, " * 10 + "%s);"
                        args = (complaint.company_id, complaint.complaint_type, complaint.complaint_date, complaint.complaint_text, complaint.company_response_text, 
                        complaint.company_response_date, complaint.source_code, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
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


    def trim_object(self, obj):

        for att in dir(obj):
            value = getattr(obj, att)
            if type(value) == str:
                setattr(obj, att, value.strip())
        return obj

    

    def __del__(self):
        self.con.close()