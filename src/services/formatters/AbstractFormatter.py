from abc import ABC, abstractmethod

class AbstractFormatter(ABC):

    @abstractmethod
    def format_summary(self, data: dict) -> str:
        pass