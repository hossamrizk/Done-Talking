from abc import ABC, abstractmethod
from ...BaseService import BaseService

class AbstractStopWords(ABC):
    """Abstract class for removing stopwords"""
    def __init__(self):
        self.base_service = BaseService()
        self.logger = self.base_service.logger

    @abstractmethod
    def get(self) -> set:
        pass