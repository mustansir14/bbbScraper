##########################################
# Coded by Mustansir Muzaffar
# mustansir2001@gmail.com
# +923333487952
##########################################

class Company:

    def __init__(self) -> None:
        self.name = None
        self.alternate_business_name = None
        self.url = None
        self.logo = None
        self.categories = None
        self.phone = None
        self.address = None
        self.street_address = None
        self.address_locality = None
        self.address_region = None
        self.postal_code = None
        self.country = None
        self.website = None
        self.hq = None
        self.is_accredited = None
        self.bbb_file_opened = None
        self.years_in_business = None
        self.accredited_since = None
        self.rating = None
        self.original_working_hours = None
        self.working_hours = None
        self.number_of_stars = None
        self.number_of_reviews = None
        self.number_of_complaints = None
        self.overview = None
        self.products_and_services = None
        self.business_started = None
        self.business_incorporated = None
        self.type_of_entity = None
        self.number_of_employees = None
        self.original_business_management = None
        self.business_management = None
        self.original_contact_information = None
        self.contact_information = None
        self.original_customer_contact = None
        self.customer_contact = None
        self.fax_numbers = None
        self.additional_phones = None
        self.additional_websites = None
        self.additional_faxes = None
        self.serving_area = None
        self.payment_methods = None
        self.referral_assistance = None
        self.refund_and_exchange_policy = None
        self.business_categories = None
        self.facebook = None
        self.instagram = None
        self.twitter = None
        self.pinterest = None
        self.linkedin = None
        self.source_code = None
        self.source_code_details = None
        self.reviews = []
        self.complaints = []
        self.log = ""
        self.status = None
        self.half_scraped = None

    def __str__(self) -> str:
        if self.name:
                return_string = 'Name: ' + self.name
        if self.alternate_business_name:
                return_string = 'Alternate name: ' + self.alternate_business_name
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
        if self.street_address:
                return_string += '\nStreet Address: ' + self.street_address
        if self.address_locality:
                return_string += '\nAddress Locality: ' + self.address_locality
        if self.address_region:
                return_string += '\nAddress Region: ' + self.address_region
        if self.postal_code:
                return_string += '\nPostal Code: ' + self.postal_code
        if self.website:
                return_string += '\nWebsite: ' + self.website
        if self.hq:
                return_string += '\nHQ: ' + str(self.hq)
        if self.is_accredited:
                return_string += '\nIs Accredited: ' + str(self.is_accredited)
        if self.rating:
                return_string += '\nRating: ' + self.rating
        if self.working_hours:
                return_string += '\nWorking hours: ' + self.working_hours
        if self.number_of_stars:
                return_string += '\nNumber of stars: ' + str(self.number_of_stars)
        if self.number_of_complaints:
                return_string += '\nNumber of complaints: ' + str(self.number_of_complaints)
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
        self.source_code = None
        self.log = ""
        self.status = None

    def __str__(self) -> str:
        if self.company_id:
                return_string = 'Company id: ' + str(self.company_id)
        if self.review_date:
                return_string += '\nReview date: ' + self.review_date
        if self.username:
                return_string += '\nUsername: ' + self.username
        if self.review_rating:
                return_string += '\nReview rating: ' + str(self.review_rating)
        if self.review_text:
                return_string += '\nReview text: ' + self.review_text
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
        self.source_code = None
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