from .BaseLLMProvider import BaseLLMProvider
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from core import get_settings
from typing import Optional
from ...BaseService import BaseService

class GoogleProvider(BaseLLMProvider):
    """Implementation of LLMProvider using Google Gemini"""
    def __init__(self, 
                 base_service: Optional[BaseService] = None,
                 model: str = "gemini-2.0-flash", 
                 temperature: float = 0.6):
        super().__init__(base_service=base_service, model=model, temperature=temperature)
        self.api_key = get_settings().GOOGLE_API_KEY

    def get_llm(self) -> BaseChatModel:
        try:
            self.logger.info(f"Successfully loading Google Gemini model {self.model} with temperature {self.temperature}")
            return ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                api_key=self.api_key
            )
        except Exception as e:
            self.logger.exception(f"Error during loading Google model: {e}")
            raise