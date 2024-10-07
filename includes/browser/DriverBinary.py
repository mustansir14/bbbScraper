import logging
import random
import string
import tempfile
import os
import sys
import zipfile
import shutil
import re
from urllib.request import urlretrieve
from pathlib import Path

class DriverBinary:
    mainVersion: int
    fullVersion: str

    def __init__(self):
        versionData = self.detectInstalledChromeVersion()

        self.fullVersion = versionData['full']
        self.mainVersion = versionData['main']

        logging.info(
            "Detected chrome version in system: " + self.fullVersion + ", main version: " + str(self.mainVersion))

    def detectInstalledChromeVersion(self) -> dict:
        path = "/opt/google/chrome/chrome"
        if not os.path.isfile(path):
            raise Exception("Can not find chrome binary in: " + path)

        output = os.popen(f"{path} --version").read().strip()
        result = re.search("[0-9\\.]{4,}", output)
        if not result:
            raise Exception("Can not find version in: " + output)

        return {
            "full": result.group(0),
            "main": int(result.group(0).split(".")[0])
        }

    def getVersion(self) -> int:
        return self.mainVersion

    def getBinary(self):
        #rnd = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
        #dst = os.path.join(tempfile.gettempdir(), "chrome_" + self.fullVersion + "_" + str(rnd))
        #shutil.copyfile("/opt/google/chrome/chrome", dst)
        #return dst
        original = os.path.join(Path.home(), "chrome_" + self.fullVersion + "_origin")

        if sys.platform.endswith("win32"):
            original += ".exe"

        if not os.path.exists(original):
            logging.info("Download last version of original: " + original)

            platform = "linux64"

            if sys.platform.endswith("win32"):
                platform = "win64"

            # https://googlechromelabs.github.io/chrome-for-testing/
            packageUrl = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/" + self.fullVersion + "/" + platform + "/chromedriver-" + platform + ".zip"
            logging.info(packageUrl)

            filename, headers = urlretrieve(packageUrl)

            logging.info(headers)
            logging.info("Unzip...")

            with zipfile.ZipFile(filename, mode="r") as z:
                chromeDriver = "chromedriver-" + platform + "/chromedriver"

                if sys.platform.endswith("win32"):
                    chromeDriver += ".exe"

                with z.open(chromeDriver) as zf, open(original, 'wb') as f:
                    shutil.copyfileobj(zf, f)

            logging.info("Remove zip...")
            os.remove(filename)

            logging.info("Set permissions to: " + original)
            os.chmod(original, 0o777)

            if not os.path.isfile(original):
                raise Exception("No origin executable")

        return original
