##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

class Company:

    def __init__(self) -> None:
        self.name = None
        self.url = None
        self.logo = None
        self.categories = None
        self.phone = None
        self.address = None
        self.website = None
        self.hq = None
        self.is_accredited = None
        self.rating = None
        self.working_hours = None
        self.number_of_stars = None
        self.number_of_reviews = None
        self.overview = None
        self.products_and_services = None
        self.business_started = None
        self.business_incorporated = None
        self.type_of_entity = None
        self.number_of_employees = None
        self.business_management = None
        self.contact_information = None
        self.customer_contact = None
        self.fax_numbers = None
        self.serving_area = None
        self.reviews = []
        self.complaints = []
        self.log = ""
        self.status = None

    def __str__(self) -> str:
        if self.name:
                return_string = 'Name: ' + self.name
        if self.url:
                return_string += '\nUrl: ' + self.url
        if self.logo:
                return_string += '\nLogo: ' + self.logo
        if self.categories:
                return_string += '\nCategories: ' + self.categories
        if self.phone:
                return_string += '\nPhone: ' + self.phone
        if self.address:
                return_string += '\nAddress: ' + self.address
        if self.website:
                return_string += '\nWebsite: ' + self.website
        if self.hq:
                return_string += '\HQ: ' + str(self.hq)
        if self.is_accredited:
                return_string += '\nIs Accredited: ' + str(self.is_accredited)
        if self.rating:
                return_string += '\nRating: ' + self.rating
        if self.working_hours:
                return_string += '\nWorking hours: ' + self.working_hours
        if self.number_of_stars:
                return_string += '\nNumber of stars: ' + str(self.number_of_stars)
        if self.number_of_reviews:
                return_string += '\nNumber of reviews: ' + str(self.number_of_reviews)
        if self.overview:
                return_string += '\nOverview: ' + self.overview
        if self.products_and_services:
                return_string += '\nProducts and services: ' + self.products_and_services
        if self.business_started:
                return_string += '\nBusiness started: ' + self.business_started
        if self.business_incorporated:
                return_string += '\nBusiness incorporated: ' + self.business_incorporated
        if self.type_of_entity:
                return_string += '\nType of entity: ' + self.type_of_entity
        if self.number_of_employees:
                return_string += '\nNumber of employees: ' + self.number_of_employees
        if self.business_management:
                return_string += '\nBusiness management: ' + self.business_management
        if self.contact_information:
                return_string += '\nContact information: ' + self.contact_information
        if self.customer_contact:
                return_string += '\nCustomer contact: ' + self.customer_contact
        if self.fax_numbers:
                return_string += '\nFax numbers: ' + self.fax_numbers
        if self.serving_area:
                return_string += '\nServing area: ' + self.serving_area

        return return_string 

class Review:

    def __init__(self) -> None:
        self.company_id = None
        self.review_date = None
        self.username = None
        self.review_text = None
        self.review_rating = None
        self.company_response_text = None
        self.company_response_date = None
        self.log = ""
        self.status = None

    def __str__(self) -> str:
        if self.company_id:
                return_string = 'Company id: ' + str(self.company_id)
        if self.review_date:
                return_string += '\nReview date: ' + self.review_date
        if self.username:
                return_string += '\nUsername: ' + self.username
        if self.review_text:
                return_string += '\nReview text: ' + self.review_text
        if self.review_rating:
                return_string += '\nReview rating: ' + str(self.review_rating)
        if self.company_response_text:
                return_string += '\nCompany response text: ' + self.company_response_text
        if self.company_response_date:
                return_string += '\nCompany response date: ' + self.company_response_date
        return return_string

class Complaint:

    def __init__(self) -> None:
        self.company_id = None
        self.complaint_type = None
        self.complaint_date = None
        self.complaint_text = None
        self.company_response_text = None
        self.company_response_date = None
        self.log = ""
        self.status = None

    def __str__(self) -> str:
        if self.company_id:
                return_string = 'Company id: ' + str(self.company_id)
        if self.complaint_type:
                return_string += '\nComplaint type: ' + self.complaint_type
        if self.complaint_date:
                return_string += '\nComplaint date: ' + self.complaint_date
        if self.complaint_text:
                return_string += '\nComplaint text: ' + self.complaint_text
        if self.company_response_text:
                return_string += '\nCompany response text: ' + self.company_response_text
        if self.company_response_date:
                return_string += '\nCompany response date: ' + self.company_response_date
        
        return return_string