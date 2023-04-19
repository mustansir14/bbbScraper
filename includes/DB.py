##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

from typing import List
from includes.models import *
import datetime, os, traceback
import mariadb
import logging
import time

class DB:

    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.db = os.getenv('DB_NAME')
        self.con = None
        
        if self.host is None or self.user is None or self.db is None:
            raise Exception("No .env, can not connect to db") 
        
        self.reconnect()
        
    def reconnect(self):
        if self.con:
            logging.info("Closing DB old connection")
            self.con.close()
        
        logging.info("DB Reconnect with:")
        logging.info("Host: " + self.host)
        logging.info("User: " + self.user)
        logging.info("Pass: ********")
        logging.info("Name: " + self.db)
        
        self.con = mariadb.connect(host=self.host, user=self.user, password=self.password, db=self.db, autocommit=True)
        
    def tryReconnect(self,times = 3):
        for i in range(times):
            logging.info(str(i) + ") Try reconnecting...")
            try:
                self.reconnect()
                return True
            except Exception:
                logging.error(traceback.format_exc())
                
            logging.info(str(i) + ") Reconnecting after 10 seconds")
            time.sleep(10)
        
        return False
        
    def removeCompanyByUrl(self, url):
        sql = 'delete from company where url = ?';
        self.execSQL(sql, (url,))
        
    def execSQL(self,sql,args):
        lastExceptionStr = None
        
        for i in range(3):
            cur = self.getDbCursor()
            
            try:
                cur.execute(sql, args)
                return True
            except Exception as e:
                lastExceptionStr = str(e)
                
                if "Duplicate entry" in str(e):
                    return True
                
                if "mysql server has gone away" not in str(e):
                    # on insert company sourceCode may be too large
                    #string = sql + "\n"
                    #if args:
                    #    string = string + "\n".join([str(v) for v in args]) + "\n"
                    #string = string + str(e)
                    raise Exception(e)
                
                if not self.tryReconnect():
                    raise Exception(e)
            finally:
                if not cur.closed:
                    cur.close()
                    
        raise Exception(lastExceptionStr)
        
    def getDbCursor(self):
        return self.con.cursor(dictionary=True)
    
    def queryArray(self,sql,args = ()):
        for i in range(3):
            cur = self.getDbCursor()
            
            try:
                cur.execute(sql, args)
                
                return cur.fetchall()
            except mariadb.InterfaceError as e:
                logging.info(e)
                if not self.tryReconnect():
                    raise Exception(e)
            except mariadb.ProgrammingError as e:
                logging.info(e)
                
                if not self.tryReconnect():
                    raise Exception(e)
            finally:
                if not cur.closed:
                    cur.close()

        raise Exception("Can not do queryArray")
        
    def queryRow(self,sql,args = ()):
        rows = self.queryArray(sql,args)
        if len(rows):
            return rows[0]
        
        return None
        
    def setSetting(self, name, value):
        self.execSQL('insert into `settings` set `name` = ?, `value` = ? ON DUPLICATE KEY UPDATE `value` = ?', (name, value, value, ))
        
    def getSetting(self, name, default):
        settingsRow = self.queryRow('select * from settings where name = ?',(name,))
        if settingsRow:
            return settingsRow['value']
            
        return default
        
    def getSettingInt(self, name, default):
        value = self.getSetting(name, default)
        return int(value)
        
    def getCompanyIdByUrl(self, company_url):
        companyRow = self.queryRow('select company_id from company where url = ?', (company_url,))
        if not companyRow:
            raise Exception("Can not find company with url: " + company_url)
            
        return companyRow['company_id']
        
    def move_company_to_other_company(self, from_company_url, to_company_url):
        try:
            fromCompanyId = self.getCompanyIdByUrl(from_company_url)
        except Exception as e:
            if str(e).find("Can not find company") == -1:
                raise e
                
            # may be company not in database
            fromCompanyId = 0
        
        try:
            toCompanyId = self.getCompanyIdByUrl(to_company_url)
        except Exception as e:
            if str(e).find("Can not find company") == -1:
                raise e
                
            # create company if not exists
            company = Company()
            company.url = to_company_url
            company.name = "no name, need scrape"
            company.status = "new"
        
            self.insert_or_update_company(company)
            
            toCompanyId = self.getCompanyIdByUrl(to_company_url)
        
        # company not in database, do not do anything
        if fromCompanyId:
            try:
                self.execSQL("update complaint set company_id = ? where company_id = ?",(toCompanyId, fromCompanyId,))
                logging.info("Complants moved to " + str(toCompanyId))
                
                self.execSQL("update review set company_id = ? where company_id = ?",(toCompanyId, fromCompanyId,))
                logging.info("Reviews moved to " + str(toCompanyId))
                
                self.execSQL("delete from company where company_id = ?", (fromCompanyId,))
                logging.info("Company removed: " + str(fromCompanyId))
            except Exception as e:
                logging.error(traceback.format_exc())
                raise e

    def insert_or_update_company(self, company : Company):
        try:
            company = self.trim_object(company)
            
            row = self.queryRow("SELECT company_id from company where url = ?", (company.url,))
            if row is not None:
                company_id = row['company_id']
                    
                if company.status == "success":
                    sql = """UPDATE company set 
                        version = 2, 
                        company_name = ?, 
                        alternate_business_name = ?, 
                        url = ?, 
                        logo = ?, 
                        categories = ?, 
                        phone = ?, 
                        address = ?, 
                        street_address = ?, 
                        address_locality = ?, 
                        address_region = ?, 
                        postal_code = ?,
                        website = ?, 
                        hq = ?, 
                        is_accredited = ?, 
                        bbb_file_opened = ?, 
                        years_in_business = ?, 
                        accredited_since = ?, 
                        rating = ?, 
                        original_working_hours = ?, 
                        working_hours = ?, 
                        number_of_stars = ?, 
                        number_of_reviews = ?, 
                        number_of_complaints = ?, 
                        overview = ?, 
                        products_and_services = ?, 
                        business_started = ?, 
                        business_incorporated = ?, 
                        type_of_entity = ?,
                        number_of_employees = ?, 
                        original_business_management = ?, 
                        business_management = ?, 
                        original_contact_information = ?, 
                        contact_information = ?, 
                        original_customer_contact = ?, 
                        customer_contact = ?, 
                        fax_numbers = ?, 
                        additional_phones = ?, 
                        additional_websites = ?, 
                        additional_faxes = ?, 
                        serving_area = ?, 
                        payment_methods = ?, 
                        referral_assistance = ?, 
                        refund_and_exchange_policy = ?, 
                        business_categories = ?, 
                        facebook = ?, 
                        instagram = ?, 
                        twitter = ?, 
                        pinterest = ?, 
                        linkedin = ?, 
                        date_updated = ?, 
                        status = ?, 
                        log = ?, 
                        half_scraped = ?, 
                        country = ?, 
                        source_code = ?, 
                        source_code_details = ? 
                        where company_id = ?"""
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
                sql = """INSERT INTO company SET 
                    version = 2, 
                    company_name = ?, 
                    alternate_business_name = ?, 
                    url = ?, 
                    logo = ?, 
                    categories = ?, 
                    phone = ?, 
                    address = ?, 
                    street_address = ?, 
                    address_locality = ?, 
                    address_region = ?, 
                    postal_code = ?, 
                    website = ?, 
                    hq = ?, 
                    is_accredited = ?, 
                    bbb_file_opened = ?, 
                    years_in_business = ?, 
                    accredited_since = ?,
                    rating = ?, 
                    original_working_hours = ?, 
                    working_hours = ?, 
                    number_of_stars = ?, 
                    number_of_reviews = ?, 
                    number_of_complaints = ?, 
                    overview = ?, 
                    products_and_services = ?, 
                    business_started = ?, 
                    business_incorporated = ?, 
                    type_of_entity = ?, 
                    number_of_employees = ?, 
                    original_business_management = ?, 
                    business_management = ?, 
                    original_contact_information = ?, 
                    contact_information = ?, 
                    original_customer_contact = ?,
                    customer_contact = ?, 
                    fax_numbers = ?, 
                    additional_phones = ?, 
                    additional_websites = ?, 
                    additional_faxes = ?, 
                    serving_area = ?, 
                    payment_methods = ?, 
                    referral_assistance = ?, 
                    refund_and_exchange_policy = ?, 
                    business_categories = ?, 
                    facebook = ?, 
                    instagram = ?, 
                    twitter = ?, 
                    pinterest = ?, 
                    linkedin = ?, 
                    source_code = ?, 
                    source_code_details = ?, 
                    date_created = ?, 
                    date_updated = ?, 
                    status = ?, 
                    log = ?, 
                    half_scraped = ?, 
                    country = ?"""
                args = (company.name, company.alternate_business_name, company.url, company.logo, company.categories, company.phone, company.address,
                company.street_address, company.address_locality, company.address_region, company.postal_code, 
                company.website, company.hq, company.is_accredited, company.bbb_file_opened, company.years_in_business, company.accredited_since, company.rating, 
                company.original_working_hours, company.working_hours, company.number_of_stars, 
                company.number_of_reviews, company.number_of_complaints, company.overview, company.products_and_services, company.business_started, 
                company.business_incorporated, company.type_of_entity, company.number_of_employees, company.original_business_management, company.business_management, company.original_contact_information,
                company.contact_information, company.original_customer_contact, company.customer_contact, company.fax_numbers, company.additional_phones, company.additional_websites, 
                company.additional_faxes, company.serving_area, company.payment_methods, company.referral_assistance, company.refund_and_exchange_policy, company.business_categories, 
                company.facebook, company.instagram, company.twitter, company.pinterest, company.linkedin, company.source_code, company.source_code_details,
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                company.status, company.log, company.half_scraped, company.country)
                
                success_statement = "Company " + company.url + " details added to DB successfully!"
                
            #logging.info(company)
            self.execSQL(sql,args)
            
            logging.info(success_statement)
            logging.info("Company id: " + self.getCompanyIdByUrl(company.url))
        except Exception as e:
            logging.error(traceback.format_exc())
            raise e

    def insert_or_update_reviews(self, reviews : List[Review]):
        counter = 0
        
        for review in reviews:
            try:
                review = self.trim_object(review)
                
                if review.status == None:
                    review.status = "success"
                    
                row = self.queryRow("SELECT review_id from review where company_id = ? and review_date = ? and username = ?;", (review.company_id, review.review_date, review.username))
                if row is not None:
                    review_id = row['review_id']
                    
                    sql = """UPDATE review SET 
                        review_text = ?, 
                        review_rating = ?, 
                        company_response_text = ?, 
                        company_response_date = ?, 
                        source_code = ?,
                        date_updated = ?, 
                        status = ?, 
                        log = ? 
                    where review_id = ?"""
                    args = (review.review_text, review.review_rating, review.company_response_text, review.company_response_date, review.source_code,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), review.status, review.log, review_id)
                else:    
                    sql = """INSERT INTO review set
                        company_id = ?,
                        review_date = ?,
                        username = ?,
                        review_text = ?,
                        review_rating = ?,
                        company_response_text = ?,
                        company_response_date = ?,
                        source_code = ?,
                        date_created = ?,
                        date_updated = ?,
                        status = ?,
                        log = ?
                    """
                    args = (review.company_id, review.review_date, review.username, review.review_text, review.review_rating, review.company_response_text, 
                    review.company_response_date, review.source_code, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    review.status, review.log)
                    
                #logging.info(review)
                #logging.info('\n')
                
                self.execSQL(sql,args)
                
                #logging.info("Review inserted to database")
                counter = counter + 1
            except Exception:
                logging.error(traceback.format_exc())
          
        if reviews:
            review = reviews[0]
            
            try:
                sql = 'update company set number_of_reviews = (select count(*) from review where company_id = ?) where company_id = ?'
                self.execSQL(sql,(review.company_id, review.company_id, ))
            except Exception:
                logging.error(traceback.format_exc())    
            
        logging.info(str(counter) + " reviews added/updated to DB successfully!")

    def insert_or_update_complaints(self, complaints : List[Complaint], page=None):
        counter = 0
        for complaint in complaints:
            try:
                complaint = self.trim_object(complaint)
                
                if complaint.status == None:
                    complaint.status = "success"
                    
                row = self.queryRow("SELECT complaint_id from complaint where company_id = ? and complaint_date = ? and complaint_type = ? and complaint_text = ?;", (complaint.company_id, complaint.complaint_date, complaint.complaint_type, complaint.complaint_text))
                if row is not None:
                    complaint_id = row['complaint_id']
                    
                    sql = """UPDATE complaint SET 
                        complaint_type = ?, 
                        complaint_date = ?,
                        complaint_text = ?, 
                        company_response_text = ?, 
                        company_response_date = ?, 
                        source_code = ?,
                        date_updated = ?, 
                        status = ?, 
                        log = ? 
                        where complaint_id = ?"""
                    args = (complaint.complaint_type, complaint.complaint_date, complaint.complaint_text, complaint.company_response_text, complaint.company_response_date, complaint.source_code,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), complaint.status, complaint.log, complaint_id)
                else:    
                    sql = """INSERT INTO complaint SET 
                        company_id = ?,
                        complaint_type = ?, 
                        complaint_date = ?,
                        complaint_text = ?, 
                        company_response_text = ?, 
                        company_response_date = ?, 
                        source_code = ?,
                        date_created = ?,
                        date_updated = ?, 
                        status = ?, 
                        log = ?"""
                    args = (complaint.company_id, complaint.complaint_type, complaint.complaint_date, complaint.complaint_text, complaint.company_response_text, 
                    complaint.company_response_date, complaint.source_code, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                    complaint.status, complaint.log)
                    
                #logging.info(complaint)
                #logging.info('\n')
                
                self.execSQL(sql,args)
                
                #logging.info("Complaint inserted to database")
                counter = counter + 1
            except Exception:
                logging.error(traceback.format_exc())
            
        if complaints:
            complaint = complaints[0]
            
            try:
                sql = 'update company set number_of_complaints = (select count(*) from complaint where company_id = ?) where company_id = ?'
                self.execSQL(sql,(complaint.company_id, complaint.company_id, ))
            except Exception:
                logging.error(traceback.format_exc())  
                
        logging.info(str(counter) + " complaints added/updated to DB successfully!")


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
        if self.con:
            self.con.close()