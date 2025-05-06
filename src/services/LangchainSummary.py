from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from .BaseService import BaseService
from models import MeetingSummary
import json
import os

class LangchainSummary(BaseService):
    def __init__(self, model: str = "gemma2:9b", temperature: float = 0.6):
        super().__init__()
        self.llm = OllamaLLM(model=model, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=MeetingSummary)
        self.output_path = self.generated_reports_path
        self.output_filename = os.path.join(self.output_path, "summarized_report.json")

    def get_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""
                You are an expert meeting summarizer. 
                You are given transcription meeting data. Your job is :-
                Write a clear, structured summary of the meeting.
                Highlight their main contributions separately.\n{format_instructions}\n{text}\n""",
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
    
    def summarize(self, text):
        prompt = self.get_prompt_template()
        prompt_and_model =  prompt | self.llm
        output = prompt_and_model.invoke(input=text)
        parsed_result = self.parser.invoke(output)
        print(parsed_result)
        try:   
            with open(self.output_filename, "w", encoding="utf-8") as f:
                json.dump(parsed_result.dict(), f, indent=4, ensure_ascii=False)
            return self.output_filename
        except Exception as e:
            self.logger.error(f"Failed to write to file {self.output_filename}: {str(e)}")
            raise FileNotFoundError(f"Failed to write to file {self.output_filename}: {str(e)}")
        