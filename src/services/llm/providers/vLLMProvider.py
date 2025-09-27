from ...BaseService import BaseService
from .BaseLLMProvider import BaseLLMProvider
from langchain_openai import ChatOpenAI
from typing import Optional

class vLLMProvider(BaseLLMProvider):
    """Implementation of LLMProvide using vLLM"""
    def __init__(self, base_service: Optional[BaseService] = None, 
                 model: Optional[str] = "Qwen/Qwen2.5-3B-Instruct", 
                 temperature: Optional[float] = 0.6):
        super().__init__(base_service, model=model, temperature=temperature)
    
    def get_llm(self):
        try:
            vllm_model = ChatOpenAI(
                model=self.model,
                openai_api_key="EMPTY",
                openai_api_base="http://localhost:8001/v1",
                temperature=self.temperature,
            )
            self.logger.info(f"Successfully loaded {self.model} model via vLLM with temperature {self.temperature}")
            return vllm_model
        except Exception as e:
            self.logger.exception(f"Error during loading vLLM model: {e}")
            raise