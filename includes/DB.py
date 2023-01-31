##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from typing import List
from includes.models import *
import datetime, os, traceback
if os.getenv('USE_MARIA_DB') is not None:
    import mariadb
else:
    import pymysql
import logging
import time

class DB:

    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.db = os.getenv('DB_NAME')
        self.con = None
        self.cur = None
        
        self.reconnect()
        
    def reconnect(self):
        if self.cur:
            self.cur.close()
            
        if self.con:
            self.con.close()
            
        if os.getenv('USE_MARIA_DB') is not None:
            self.con = mariadb.connect(host=self.host, user=self.user, password=self.password, db=self.db, autocommit=True)
        else:
            self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, cursorclass=pymysql.cursors.DictCursor)
            
        self.cur = self.con.cursor()
        
    def tryReconnect(self,times = 3):
        for i in range(times):
            logging.info(str(i) + ") Reconnecting after 10 seconds")
            time.sleep(10)
            
            try:
                self.reconnect()
                return True
            except Exception:
                logging.error(traceback.format_exc())
        
        return False
        
    def execSQL(self,sql,args):
        for i in range(3):
            try:
                self.cur.execute(sql, args)
                break
            except Exception as e:
                if "mysql server has gone away" not in str(e):
                    raise Exception(e)
                
                if not self.tryReconnect():
                    raise Exception(e)
        
    def getDbCursor(self):
        if os.getenv('USE_MARIA_DB') is not None:
            return self.con.cursor(dictionary=True)
            
        return self.con.cursor()
    
    def queryArray(self,sql,args):
        cur = self.getDbCursor()
        
        cur.execute( sql,args )
        rows = cur.fetchall()

        cur.close()

        return rows

    def insert_or_update_company(self, company : Company):
        try:
            company = self.trim_object(company)
                
            self.cur.execute("SELECT company_id from company where url = ?;", (company.url,))
            fetched_results = self.cur.fetchall()
            if len(fetched_results) == 1:
                if os.getenv('USE_MARIA_DB') is not None:
                    company_id = fetched_results[0][0]
                else:
                    company_id = fetched_results[0]["company_id"]
                    
                if company.status == "success":
                    sql = """UPDATE company set version = 2, company_name = ?, alternate_business_name = ?, url = ?, logo = ?, categories = ?, phone = ?, address = ?, 
                    street_address = ?, address_locality = ?, address_region = ?, postal_code = ?,
                    website = ?, hq = ?, is_accredited = ?, bbb_file_opened = ?, years_in_business = ?, accredited_since = ?, rating = ?, original_working_hours = ?, working_hours = ?, number_of_stars = ?, number_of_reviews = ?, number_of_complaints = ?, 
                    overview = ?, products_and_services = ?, business_started = ?, business_incorporated = ?, type_of_entity = ?,
                    number_of_employees = ?, original_business_management = ?, business_management = ?, original_contact_information = ?, contact_information = ?, original_customer_contact = ?, customer_contact = ?, 
                    fax_numbers = ?, additional_phones = ?, additional_websites = ?, additional_faxes = ?, serving_area = ?, payment_methods = ?, referral_assistance = ?, refund_and_exchange_policy = ?, business_categories = ?, facebook = ?, instagram = ?, twitter = ?, pinterest = ?, linkedin = ?, date_updated = ?, status = ?, log = ?, half_scraped = ?, country = ?, source_code = ?, source_code_details = ? where company_id = ?;"""
                    args = (company.name, company.alternate_business_name, company.url, company.logo, company.categories, company.phone, company.address,
                    company.street_address, company.address_locality, company.address_region, company.postal_code, 
                    company.website, company.hq, company.is_accredited, company.bbb_file_opened, company.years_in_business, company.accredited_since, company.rating, company.original_working_hours, company.working_hours, company.number_of_stars, 
                    company.number_of_reviews, company.number_of_complaints, company.overview, company.products_and_services, company.business_started, 
                    company.business_incorporated, company.type_of_entity, company.number_of_employees, company.original_business_management, company.business_management, company.original_contact_information,
                    company.contact_information, company.original_customer_contact, company.customer_contact, company.fax_numbers, company.additional_phones, company.additional_websites, company.additional_faxes, company.serving_area, company.payment_methods, company.referral_assistance, company.refund_and_exchange_policy, company.business_categories, company.facebook, company.instagram, company.twitter, company.pinterest, company.linkedin,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), company.status, company.log, company.half_scraped, company.country, company.source_code, company.source_code_details, company_id)
                else:
                    sql = """update company set source_code = ?, source_code_details = ?, status = ?, log = ?, half_scraped = ?, country = ?, date_updated = now() where company_id = ?;"""
                    args = (company.source_code, company.source_code_details, company.status, company.log, company.half_scraped, company.country, company_id)
                    
                success_statement = "Company " + company.url + " details updated successfully!"
            else:
                sql = """INSERT INTO company (version, company_name, alternate_business_name, url, logo, categories, phone, address, company.street_address, 
                company.address_locality, company.address_region, company.postal_code, website, hq, is_accredited, bbb_file_opened, years_in_business, accredited_since,
                rating, original_working_hours, working_hours, number_of_stars, number_of_reviews, number_of_complaints, overview, products_and_services, business_started, 
                business_incorporated, type_of_entity, number_of_employees, original_business_management, business_management, original_contact_information, contact_information, original_customer_contact,
                customer_contact, fax_numbers, additional_phones, additional_websites, additional_faxes, serving_area, payment_methods, referral_assistance, refund_and_exchange_policy, business_categories, facebook, instagram, twitter, pinterest, linkedin, source_code, source_code_details, date_created, date_updated, status, log, half_scraped, country) VALUES (2, """ + "?, " * 56 + "?);"
                args = (company.name, company.alternate_business_name, company.url, company.logo, company.categories, company.phone, company.address,
                company.street_address, company.address_locality, company.address_region, company.postal_code, 
                company.website, company.hq, company.is_accredited, company.bbb_file_opened, company.years_in_business, company.accredited_since, company.rating, company.original_working_hours, company.working_hours, company.number_of_stars, 
                company.number_of_reviews, company.number_of_complaints, company.overview, company.products_and_services, company.business_started, 
                company.business_incorporated, company.type_of_entity, company.number_of_employees, company.original_business_management, company.business_management, company.original_contact_information,
                company.contact_information, company.original_customer_contact, company.customer_contact, company.fax_numbers, company.additional_phones, company.additional_websites, company.additional_faxes, company.serving_area, company.payment_methods, company.referral_assistance, company.refund_and_exchange_policy, company.business_categories, company.facebook, company.instagram, company.twitter, company.pinterest, company.linkedin, company.source_code, company.source_code_details,
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                company.status, company.log, company.half_scraped, company.country)
                
                success_statement = "Company " + company.name + " details added to DB successfully!"
                
            logging.info(company)
            self.execSQL(sql,args)
            
            logging.info(success_statement)
        except Exception:
            logging.error(traceback.format_exc())
            


    def insert_or_update_reviews(self, reviews : List[Review]):
        for review in reviews:
            try:
                review = self.trim_object(review)
                
                if review.status == None:
                    review.status = "success"
                    
                self.cur.execute("SELECT review_id from review where company_id = ? and review_date = ? and username = ?;", (review.company_id, review.review_date, review.username))
                fetched_results = self.cur.fetchall()
                
                if len(fetched_results) >= 1:
                    if os.getenv('USE_MARIA_DB') is not None:
                        review_id = fetched_results[0][0]
                    else:
                        review_id = fetched_results[0]["review_id"]
                    sql = """UPDATE review SET review_text = ?, review_rating = ?, company_response_text = ?, company_response_date = ?, source_code = ?,
                    date_updated = ? , status = ?, log = ? where review_id = ?;"""
                    args = (review.review_text, review.review_rating, review.company_response_text, review.company_response_date, review.source_code,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), review.status, review.log, review_id)
                else:    
                    sql = "INSERT INTO review VALUES (DEFAULT, " + "?, " * 11 + "?);"
                    args = (review.company_id, review.review_date, review.username,review.review_text, review.review_rating, review.company_response_text, 
                    review.company_response_date, review.source_code, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    review.status, review.log)
                    
                logging.info(review)
                self.execSQL(sql,args)
                
                logging.info("Review inserted to database")
            except Exception:
                logging.error(traceback.format_exc())
            
                
        logging.info("Reviews added/updated to DB successfully!")

    def insert_or_update_complaints(self, complaints : List[Complaint], page=None):
        for complaint in complaints:
            try:
                complaint = self.trim_object(complaint)
                
                if complaint.status == None:
                    complaint.status = "success"
                    
                self.cur.execute("SELECT complaint_id from complaint where company_id = ? and complaint_date = ? and complaint_type = ? and complaint_text = ?;", (complaint.company_id, complaint.complaint_date, complaint.complaint_type, complaint.complaint_text))
                fetched_results = self.cur.fetchall()
                
                if len(fetched_results) >= 1:
                    if os.getenv('USE_MARIA_DB') is not None:
                        complaint_id = fetched_results[0][0]
                    else:
                        complaint_id = fetched_results[0]["complaint_id"]
                    sql = """UPDATE complaint SET complaint_type = ?, complaint_text = ?, company_response_text = ?, company_response_date = ?, source_code = ?,
                    date_updated = ? , status = ?, log = ? where complaint_id = ?;"""
                    args = (complaint.complaint_type, complaint.complaint_text, complaint.company_response_text, complaint.company_response_date, complaint.source_code,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), complaint.status, complaint.log, complaint_id)
                else:    
                    sql = "INSERT INTO complaint VALUES (DEFAULT, " + "?, " * 10 + "?);"
                    args = (complaint.company_id, complaint.complaint_type, complaint.complaint_date, complaint.complaint_text, complaint.company_response_text, 
                    complaint.company_response_date, complaint.source_code, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    complaint.status, complaint.log)
                    
                logging.info(complaint)
                self.execSQL(sql,args)
                
                logging.info("Complaint inserted to database")
            except Exception:
                logging.error(traceback.format_exc())
            
            
        logging.info("Complaints added/updated to DB successfully!")


    def trim_object(self, obj):

        for att in dir(obj):
            value = getattr(obj, att)
            if type(value) == str:
                value = value.strip()
                if value == '' or value == '{}':
                    value = None
                setattr(obj, att, value)
        return obj

    

    def __del__(self):
        self.con.close()