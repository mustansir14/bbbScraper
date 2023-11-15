import logging
import os

from pyvirtualdisplay import Display


class DisplayLoader:
    display: None

    def __init__(self):
        self.display = None

    def start(self):
        if os.name != "nt":
            logging.info("Creating display...")

            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()

    def stop(self):
        if os.name != "nt" and self.display:
            logging.info("Removing display...")

            self.display.stop()
            self.display = None
