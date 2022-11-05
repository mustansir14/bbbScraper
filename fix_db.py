from includes.DB import DB
import json
from datetime import datetime
import re

db = DB()
cur = db.getDbCursor()

count = 0 
while True:
    cur.execute(f"SELECT * from company limit {count*5000}, 5000;")
    print(count*5000)
    records = cur.fetchall()
    if len(records) == 0:
        break
    for record in records:

        # working hours
        if record['working_hours'] and not record['original_working_hours']:
            
            working_hours_dict = {}
            days_mapping = {"M:": "monday",
            "T:": "tuesday", 
            "W:": "wednesday", 
            "Th:": "thursday", 
            "F:": "friday", 
            "Sa:": "saturday", 
            "Su:": "sunday",
            }
            record['working_hours'] = record['working_hours'].replace(":\n", ": ")
            for line in record['working_hours'].strip().split("\n"):
                if line.strip() == "":
                    continue
                first_word = line.split()[0]
                if first_word not in days_mapping:
                    continue
                time_data = "".join(line.split()[1:]).lower()
                if time_data == "open24hours":
                    time_data = "open24"
                elif "-" in time_data:
                    times = time_data.split("-")
                    if len(times) == 2:
                        for time_index in range(2):
                            if "pm" in times[time_index]:
                                colon_split = times[time_index].split(":")
                                if len(colon_split) >= 2:
                                    times[time_index] = str(int(colon_split[0].replace("am", "").replace("pm", ""))+12) + ":" + colon_split[1].replace("pm", "")
                                else:
                                    times[time_index] = str(int(colon_split[0].replace("am", "").replace("pm", ""))+12)
                            times[time_index] = times[time_index].replace("am", "")
                    time_data = "-".join(times)
                working_hours_dict[days_mapping[first_word]] = time_data.replace(".", "")
            record['original_working_hours'] = record['working_hours']
            record['working_hours'] = json.dumps(working_hours_dict)

        if record['products_and_services']:
            record['products_and_services'] = record['products_and_services'].strip().replace("\n\n", "")
        
        if record['serving_area']:
            pattern = r'<.*?>'
            record['serving_area'] = re.sub(pattern, '', record["serving_area"].replace("Read More", "").replace("Read Less", "").strip()[:65535])

        if record['website'] and not record['additional_websites']:
            record['additional_websites'] = ""
            for url in record['website'].replace("Read More", "").replace("Read Less", "").strip().split("\n")[1:]:
                if ("http" in url or "www" in url or ".com" in url) and " " not in url.strip():
                    record['additional_websites'] += url + "\n"
            record['additional_websites'] = record['additional_websites'].strip()
            if record['additional_websites'] == "":
                record['additional_websites'] = None
            record['website'] = record['website'].replace("Read More", "").replace("Read Less", "").strip().split("\n")[0]

        if record['phone'] and not record['additional_phones']:
            record['additional_phones'] = record['phone'].replace("Read More", "").replace("Read Less", "").replace("Primary Phone", "").replace("Other Phone", "").strip()
            record['additional_phones'] = "\n".join([line for line in record['additional_phones'].split("\n")[1:] if line[-3:].isnumeric()]).strip()
            record['phone'] = record['phone'].split("\n")[0]
            if record['additional_phones'] == "":
                record['additional_phones'] = None

        if record['fax_numbers'] and not record['additional_faxes']:
            fax_lines = record['fax_numbers'].replace("Primary Fax", "").replace("Other Fax", "").replace("Read More", "").replace("Read Less", "").replace("Phone Number: ", "").strip()
            fax_lines = [line for line in fax_lines.split("\n") if line[-3:].isnumeric()]
            if fax_lines:
                record['fax_numbers'] = fax_lines[0]
            else:
                record['fax_numbers'] = None
            if len(fax_lines) > 1:
                record['additional_faxes'] = "\n".join(fax_lines[1:])
        
        if record['contact_information'] and not record['original_contact_information']:
            record['original_contact_information'] = record['contact_information'].strip()
            record['contact_information'] = []
            current_type = None
            for line in record['original_contact_information'].split("\n"):
                if "," not in line:
                    current_type = line
                elif current_type:
                    person = {"name": line.split(",")[0].strip(), "designation": line.split(",")[1].strip()}
                    if record['contact_information'] and record['contact_information'][-1]["type"] == current_type:
                        record['contact_information'][-1]["persons"].append(person)
                    else:
                        record['contact_information'].append({"type": current_type, "persons": [person]})
            record['contact_information'] = json.dumps(record['contact_information'])

        if record['business_management'] and not record['original_business_management']:
            record['original_business_management'] = record['business_management'].strip()
            record['business_management'] = []
            for line in record['original_business_management'].split("\n"):
                if "," in line:
                    line_split = line.split(",")
                    record['business_management'].append({"type": line_split[1].strip(), "person": line_split[0].strip()})
            record['business_management'] = json.dumps(record['business_management'])

        if record['customer_contact'] and not record['original_customer_contact']:
            record['original_customer_contact'] = record['customer_contact'].strip()
            record['customer_contact'] = []
            for line in record['original_customer_contact'].split("\n"):
                if "," in line:
                    line_split = line.split(",")
                    record['customer_contact'].append({"type": line_split[1].strip(), "person": line_split[0].strip()})
            record['customer_contact'] = json.dumps(record['customer_contact'])

        cur.execute("UPDATE company set working_hours = %s, original_working_hours = %s, date_updated = %s, products_and_services = %s, serving_area = %s, website = %s, additional_websites = %s, phone = %s, additional_phones = %s, fax_numbers = %s, additional_faxes = %s, contact_information = %s, original_contact_information = %s, business_management = %s, original_business_management = %s, customer_contact = %s, original_customer_contact = %s where company_id = %s;", (record['working_hours'], record['original_working_hours'], datetime.now(), record['products_and_services'], record['serving_area'], record['website'], record['additional_websites'], record['phone'], record['additional_phones'], record['fax_numbers'], record['additional_faxes'], record['contact_information'], record['original_contact_information'], record['business_management'], record['original_business_management'], record['customer_contact'], record['original_customer_contact'], record['company_id']))
        db.con.commit()


    count += 1
