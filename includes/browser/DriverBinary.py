import logging
import tempfile
import os
import sys
import zipfile
import shutil
from urllib.request import urlretrieve


class DriverBinary:
    version: int

    def __init__(self):
        self.version = 119

    def getVersion(self) -> int:
        return self.version

    def getBinary(self):
        version = "119.0.6045.105"
        original = os.path.join(tempfile.gettempdir(), "chrome_" + str(version) + "_origin")

        if sys.platform.endswith("win32"):
            original += ".exe"

        if not os.path.exists(original):
            logging.info("Download last version of original: " + original)

            platform = "linux64"

            if sys.platform.endswith("win32"):
                platform = "win64"

            packageUrl = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/" + version + "/" + platform + "/chromedriver-" + platform + ".zip"
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
