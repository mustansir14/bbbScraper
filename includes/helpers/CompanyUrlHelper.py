import re


class CompanyUrlHelper:
    BusinessIdPart = 2
    BbbIdPart = 1

    @staticmethod
    def getBusinessId(companyUrl: str) -> str:
        return __class__.getUrlParts(companyUrl).group(__class__.BusinessIdPart)

    @staticmethod
    def getBbbId(companyUrl: str) -> str:
        return __class__.getUrlParts(companyUrl).group(__class__.BbbIdPart)

    @staticmethod
    def getUrlParts(companyUrl: str):
        result = re.search(r'([0-9]{1,8})\-([0-9]{1,20})$', companyUrl)
        if not result:
            raise Exception("Url not valid: " + companyUrl)

        return result
