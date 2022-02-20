class Company:

    def __init__(self) -> None:
        self.name = None
        self.url = None
        self.logo = None
        self.categories = None
        self.phone = None
        self.address = None
        self.website = None
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
        return_string = 'Name: ' + self.name
        return_string += '\nUrl: ' + self.url
        return_string += '\nLogo: ' + self.logo
        return_string += '\nCategories: ' + self.categories
        return_string += '\nPhone: ' + self.phone
        return_string += '\nAddress: ' + self.address
        return_string += '\nWebsite: ' + self.website
        return_string += '\nWorking hours: ' + self.working_hours
        return_string += '\nNumber of stars: ' + self.number_of_stars
        return_string += '\nNumber of reviews: ' + self.number_of_reviews
        return_string += '\nOverview: ' + self.overview
        return_string += '\nProducts and services: ' + self.products_and_services
        return_string += '\nBusiness started: ' + self.business_started
        return_string += '\nBusiness incorporated: ' + self.business_incorporated
        return_string += '\nType of entity: ' + self.type_of_entity
        return_string += '\nNumber of employees: ' + self.number_of_employees
        return_string += '\nBusiness management: ' + self.business_management
        return_string += '\nContact information: ' + self.contact_information
        return_string += '\nCustomer contact: ' + self.customer_contact
        return_string += '\nFax numbers: ' + self.fax_numbers
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
        return_string = 'Company id: ' + self.company_id
        return_string += '\nReview date: ' + self.review_date
        return_string += '\nUsername: ' + self.username
        return_string += '\nReview text: ' + self.review_text
        return_string += '\nReview rating: ' + self.review_rating
        return_string += '\nCompany response text: ' + self.company_response_text
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
        return_string = 'Company id: ' + self.company_id
        return_string += '\nComplaint type: ' + self.complaint_type
        return_string += '\nComplaint date: ' + self.complaint_date
        return_string += '\nComplaint text: ' + self.complaint_text
        return_string += '\nCompany response text: ' + self.company_response_text
        return_string += '\nCompany response date: ' + self.company_response_date
        
        return return_string