from .BasePrompt import BasePrompt
from langchain.prompts import PromptTemplate

class EnglishPrompt(BasePrompt):
    """English prompt strategy implementation."""

    def get_prompt_template(self) -> PromptTemplate:
        """Return the english prompt template."""
        return PromptTemplate(
            template="""
                You are an expert meeting summarizer. 
                You are given transcription meeting data. Your job is :-
                Write a clear, structured summary of the meeting.
                Highlight their main contributions separately.\n{format_instructions}\n{text}\n""",
            input_variables = ["text"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )
    