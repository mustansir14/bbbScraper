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
url = "https://www.bbb.org/ca/ab/airdrie/profile/artificial-turf/perfect-turf-calgary-0017-51314"

while True:
    if url:
        sql = 'select company_id, url, source_code from company where url = "' + url + '"'
    else:
        sql = 'select company_id, url, source_code from company where company_id > ' + str(
            fromId) + ' and source_code is not null and length(source_code) > 0 order by company_id limit 100'

    print(sql)

    rows = db.queryArray(sql)
    if not rows:
        break

    for row in rows:
        fromId = row['company_id']

        print(row['url'])

        company = Company()

        try:
            c = CompanyParser()
            c.setCompany(company)
            c.parse(row['source_code'])
        except (PageNotFoundException, PageWoopsException):
            continue

        print(company)

    break
