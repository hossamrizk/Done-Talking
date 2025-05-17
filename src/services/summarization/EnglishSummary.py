from .AbstractSummary import AbstractSummary
from ..llm import EnglishPrompt, OllamaProvider
from langchain_core.output_parsers import StrOutputParser
from .JSONOutputHandler import JSONOutputHandler

class EnglishSummary(AbstractSummary):
    def __init__(self):
        super().__init__()
        english_prompt = EnglishPrompt(output_parser=self.parser)
        ollama_provider = OllamaProvider()

        self.prompt = english_prompt.get_prompt_template()
        self.llm = ollama_provider.get_llm()
        self.json_handler = JSONOutputHandler(base_service=self.base_service)

    def create_summary(self, text: str):
        try:    
            chain = self.prompt | self.llm | StrOutputParser()
            output = chain.invoke(input=text)
            parsed_result = self.parser.parse(output)
            file_path = self.json_handler.save_output(data = parsed_result.dict())
            self.logger.info(f"Successfully parsed english summary result and file saved at {file_path}")
            return file_path
        except Exception as e:
            self.logger.exception(f"Error while generating English summary {e}")