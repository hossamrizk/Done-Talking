from abc import ABC, abstractmethod
from src.services.BaseService import BaseService

class AbstractAudioHandler(ABC):
    def __init__(self):
        self.base_service = BaseService()
        self.logger = self.base_service.logger

    @abstractmethod
    def handle(self, *args, **kwargs):
        pass