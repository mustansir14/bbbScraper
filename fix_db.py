from includes.DB import DB
import json
from datetime import datetime
import re, sys
from includes.parsers.CompanyParser import CompanyParser
from includes.models import Company
from includes.parsers.Exceptions.PageNotFoundException import PageNotFoundException
from includes.parsers.Exceptions.PageWoopsException import PageWoopsException

db = DB()
fromId = 0
url = None #"https://www.bbb.org/ca/ab/airdrie/profile/artificial-turf/perfect-turf-calgary-0017-51314"

while True:
    if url:
        sql = 'select company_id, url, source_code from company where url = "' + url + '"'
    elif "--cb" in sys.argv:
        sql = 'select company_id, url, source_code from company where exists_on_cb  > 0 and company_id > ' + str(
            fromId) + ' and source_code is not null and length(source_code) > 0 order by company_id limit 100'
    else:
        sql = 'select company_id, url, source_code from company where company_id > ' + str(
            fromId) + ' and source_code is not null and length(source_code) > 0 order by company_id limit 100'

    print(sql)

    rows = db.queryArray(sql)
    if not rows:
        break

    for row in rows:
        fromId = row['company_id']

        #print(row['url'])

        company = Company()

        try:
            c = CompanyParser()
            c.setCompany(company)
            c.parse(row['source_code'])
        except (PageNotFoundException, PageWoopsException):
            continue

        fields = {
            'company_name': company.name,
            'categories': company.categories,
            'phone': company.phone,
            'website': company.website,
            'address': company.address,
            'street_address': company.street_address,
            'address_locality': company.address_locality,
            'address_region': company.address_region,
            'postal_code': company.postal_code,
            'hq': company.hq,
            'is_accredited': company.is_accredited,
            'rating': company.rating,
            'number_of_stars': company.number_of_stars,
            'number_of_reviews': company.number_of_reviews,
            'number_of_complaints': company.number_of_complaints,
            'overview': company.overview,
            'products_and_services': company.products_and_services,
        }

        db.update('company', fields, "company_id = '" + str(row['company_id']) + "'")
