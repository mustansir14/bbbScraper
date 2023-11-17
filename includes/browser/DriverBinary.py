import logging
import tempfile
import os
import sys
import zipfile
import shutil
from urllib.request import urlretrieve


class DriverBinary:
    versions: dict[int, str]
    version: int

    def __init__(self):
        self.version = 119
        self.versions = {
            116: "116.0.5845.96",
            119: "119.0.6045.105",
        }

    def getVersion(self) -> int:
        return self.version

    def getBinary(self):
        original = os.path.join(tempfile.gettempdir(), "chrome_" + self.versions[self.getVersion()] + "_origin")

        if sys.platform.endswith("win32"):
            original += ".exe"

        if not os.path.exists(original):
            logging.info("Download last version of original: " + original)

            platform = "linux64"

            if sys.platform.endswith("win32"):
                platform = "win64"

            # https://googlechromelabs.github.io/chrome-for-testing/
            packageUrl = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/" + self.versions[
                self.getVersion()] + "/" + platform + "/chromedriver-" + platform + ".zip"
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
            os.chmod(original, 0o755)

            if not os.path.isfile(original):
                raise Exception("No origin executable")

        return original
