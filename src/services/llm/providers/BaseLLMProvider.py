from abc import ABC, abstractmethod
from langchain_core.language_models.llms import BaseLLM
from typing import Optional
from src.services.BaseService import BaseService


class BaseLLMProvider(ABC):
    """Abstract class defines the interface for LLM providers."""
    def __init__(self, base_service: Optional[BaseService] = None, 
                 model: Optional[str] = None, 
                 temperature: Optional[float] = None):
        self.base_service = base_service or BaseService()
        self.logger = self.base_service.logger
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def get_llm(self) -> BaseLLM:
        """Returns an LLM instance"""
        pass