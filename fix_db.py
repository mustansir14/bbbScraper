from includes.DB import DB
import json
from datetime import datetime
import re, sys
from includes.parsers.CompanyParser import CompanyParser
from includes.models import Company

db = DB()
companyRow = db.queryRow('select * from company where url = ?', [
    'https://www.bbb.org/us/fl/saint-petersburg/profile/social-security-services/quikaid-inc-0653-90159326',
    #'https://www.bbb.org/ca/ab/edmonton/profile/legal-forms/lawdepot-tm-0117-134065',
])

#print(companyRow['source_code'])

c = CompanyParser()
c.setCompany(Company())
c.parse(companyRow['source_code'])
