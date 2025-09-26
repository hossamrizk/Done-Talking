from langchain_ollama import OllamaLLM
from .BaseLLMProvider import BaseLLMProvider
from typing import Optional
from ...BaseService import BaseService

class OllamaProvider(BaseLLMProvider):
    """Implementation of LLMProvider Using Ollama."""
    def __init__(self, base_service: Optional[BaseService] = None, 
                 model: Optional[str] = "mistral:7b-instruct-q4_0", 
                 temperature: Optional[float] = 0.6):
        super().__init__(base_service, model=model, temperature=temperature)

    def get_llm(self) -> OllamaLLM:
        try:
            self.logger.info(f"Successfully load ollama model {self.model} with temperature {self.temperature}")
            return OllamaLLM(model=self.model, temperature=self.temperature)
        except Exception as e:
            self.logger.exception(f"Error during loading ollama model {e}")
            raise