import datetime
import re


class DateHelper:
    @staticmethod
    def bbbDate2mariadb(text: str) -> str:
        # BBB have date problem:
        # https://www.bbb.org/us/ca/tracy/profile/mattress-supplies/zinus-inc-1156-90044368/customer-reviews
        # 02/28/2022
        # https://www.bbb.org/ca/ab/calgary/profile/insurance-agency/bayside-associates-0017-52776/customer-reviews
        # 15/09/2020
        # that's why %m/%d/%Y not work
        try:
            text = text.strip()
            text = re.sub(r'[^0-9/]', '', text)
            return datetime.datetime.strptime(text, "%m/%d/%Y").strftime('%Y-%m-%d')
        except Exception as e:
            pass

        return datetime.datetime.strptime(text, "%d/%m/%Y").strftime('%Y-%m-%d')
