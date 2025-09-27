from .AbstractSummary import AbstractSummary
from ..llm import ArabicPrompt, GoogleProvider, vLLMProvider
from langchain_core.output_parsers import StrOutputParser
from .JSONOutputHandler import JSONOutputHandler

class ArabicSummary(AbstractSummary):
    def __init__(self):
        super().__init__()
        arabic_prompt = ArabicPrompt(output_parser=self.parser)
        google_provider = GoogleProvider()
        #vllm_provider = vLLMProvider()

        self.prompt = arabic_prompt.get_prompt_template()
        self.llm = google_provider.get_llm()
        #self.llm = vllm_provider.get_llm()
        self.json_handler = JSONOutputHandler(base_service=self.base_service)


    def create_summary(self, text: str):
        try:    
            chain = self.prompt | self.llm | StrOutputParser()
            output = chain.invoke(input=text)
            parsed_result = self.parser.parse(output)
            file_path = self.json_handler.save_output(data = parsed_result.dict())
            self.logger.info(f"Successfully parsed arabic summary result and file saved at {file_path}")
            return file_path
        except Exception as e:
            self.logger.exception(f"Error while generating Arabic summary {e}")