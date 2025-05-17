from abc import ABC, abstractmethod
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

class BasePrompt(ABC):
    """Base class for all prompt strategies."""

    def __init__(self, output_parser: PydanticOutputParser):
        self.output_parser = output_parser

    @abstractmethod
    def get_prompt_template(self) -> PromptTemplate:
        """Get the prompt template."""
        pass