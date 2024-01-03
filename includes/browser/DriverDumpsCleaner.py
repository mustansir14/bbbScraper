import datetime
import logging
import glob
import os
import shutil
import time


class DriverDumpsCleaner:
    def clean(self):
        try:
            self.removeFiles("./core.*", 0)
            self.removeFiles("/tmp/.com.google.*", 60)
            self.removeFiles("/tmp/tmp*", 60)
        except Exception as e:
            logging.error("removeCoreDumps exception: " + str(e))

    def removeFiles(self, pattern: str, longerThanSeconds: int):
        logging.info("Remove files from: " + pattern)

        for file in glob.glob(pattern):
            try:
                ctime = os.stat(file).st_ctime

                logging.info("Remove: " + file + ", created: " + datetime.datetime.fromtimestamp(ctime).strftime(
                    '%Y-%m-%d %H:%M:%S'))

                if ctime < time.time() - longerThanSeconds:
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                    else:
                        os.remove(file)
            except Exception as e:
                logging.error(str(e))
                pass
