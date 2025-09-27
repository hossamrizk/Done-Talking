from abc import ABC, abstractmethod
from src.services.BaseService import BaseService
from src.schemas import MeetingSummary
from langchain_core.output_parsers import PydanticOutputParser

class AbstractSummary(ABC):

    def __init__(self):
        self.base_service = BaseService()
        self.logger = self.base_service.logger
        self.parser = PydanticOutputParser(pydantic_object=MeetingSummary)

    @abstractmethod
    def create_summary(self, text: str):
        pass