from abc import ABC, abstractmethod


class ParserInterface(ABC):
    @classmethod
    @abstractmethod
    def parse(self, html: str):
        pass
