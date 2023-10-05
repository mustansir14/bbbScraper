from bs4 import BeautifulSoup
import json
import re


class ScriptTagParser:
    @staticmethod
    def getSchemaOrgByType(html: str, type: str):
        if not html:
            raise Exception("No html")

        if not type:
            raise Exception("No type")

        soup = BeautifulSoup(html, 'html.parser')

        for scriptTag in soup.find_all("script", type="application/ld+json"):
            schemaOrgArray = json.loads(scriptTag.string)
            for schemaOrg in schemaOrgArray:
                if schemaOrg['@type'] == type:
                    return schemaOrg

        return None

    @staticmethod
    def getScriptVar(html: str, name: str):
        if not html:
            raise Exception("No html")

        if not name:
            raise Exception("No name")

        data = re.search(r"<script>window\." + name + "\s*?=(.*?);</script>", html)

        if not data:
            raise Exception("Can not get window." + name)

        data = data.group(1)
        return json.loads(data)
