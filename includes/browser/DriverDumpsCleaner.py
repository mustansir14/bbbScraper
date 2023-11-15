import logging
import glob
import os


class DriverDumpsCleaner:
    def clean(self):
        try:
            logging.info("Remove core dumps, to free space...")

            for file in glob.glob("./core.*"):
                try:
                    os.remove(file)
                except:
                    pass
        except Exception as e:
            logging.error("removeCoreDumps exception: " + str(e))