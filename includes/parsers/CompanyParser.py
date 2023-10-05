from includes.parsers.ParserInterface import ParserInterface
from includes.parsers.ScriptTagParser import ScriptTagParser
from includes.models import Company
from bs4 import BeautifulSoup
import re


class CompanyParser(ParserInterface):
    def __init__(self):
        self.company = None

    def setCompany(self, company: Company):
        self.company = company

    def parse(self, html: str):
        if not html:
            raise Exception("No html")

        if not self.company:
            raise Exception("No company record")

        localBusiness = ScriptTagParser.getSchemaOrgByType(html, 'LocalBusiness')
        if not localBusiness:
            raise Exception("Can not find localBusiness in script[ld+json]")

        companyPreloadState = ScriptTagParser.getScriptVar(html, '__PRELOADED_STATE__')
        if not companyPreloadState:
            raise Exception("No preload state")

        soup = BeautifulSoup(html, 'html.parser')

        self.company.name = localBusiness['name']
        self.company.categories = "\n".join(
            [x['title'] for x in companyPreloadState['businessProfile']['categories']['links']])
        self.company.phone = localBusiness['telephone'] if 'telephone' in localBusiness else None

        if "primary" in companyPreloadState['businessProfile']['urls']:
            self.company.website = companyPreloadState['businessProfile']['urls']['primary']

        try:
            lines = [
                companyPreloadState['businessProfile']['location']['displayAddress']['addressLine1'],
                companyPreloadState['businessProfile']['location']['displayAddress']['addressLine2']
            ]
            lines = [i for i in lines if i is not None]

            self.company.address = ", ".join(lines)

            self.company.street_address = localBusiness['address']['streetAddress']
            self.company.address_locality = localBusiness['address']['addressLocality']
            self.company.address_region = localBusiness['address']['addressRegion']
            self.company.postal_code = localBusiness['address']['postalCode']
        except Exception as e:
            pass

        self.company.hq = companyPreloadState['businessProfile']['location']['isHq']
        self.company.is_accredited = companyPreloadState['businessProfile']['accreditationInformation']['isAccredited']
        self.company.rating = companyPreloadState['businessProfile']['rating']['bbbRating']
        self.company.number_of_stars = companyPreloadState['businessProfile']['reviewsComplaintsSummary'][
            'averageOfReviewStarRatings']
        self.company.number_of_reviews = companyPreloadState['businessProfile']['reviewsComplaintsSummary'][
            'reviewsTotal']
        self.company.number_of_complaints = companyPreloadState['businessProfile']['reviewsComplaintsSummary'][
            'complaintsTotal']

        self.company.overview = companyPreloadState['businessProfile']['orgDetails']['organizationDescription']
        if self.company.overview:
            self.company.overview = re.sub('</?[^<]+?>', '', self.company.overview)
            self.company.overview = re.sub('(\r?\n){2,}', '\n\n', self.company.overview)

        self.company.products_and_services = companyPreloadState['businessProfile']['display']['prodSrvcsSummary']
        self.company.source_code = html
