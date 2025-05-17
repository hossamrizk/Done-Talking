from .BasePrompt import BasePrompt
from langchain.prompts import PromptTemplate

class ArabicPrompt(BasePrompt):
    """Arabic prompt strategy implementation."""

    def get_prompt_template(self) -> PromptTemplate:
        """Return the arabic prompt template."""
        return PromptTemplate(
            template="""
                You are a helpful assistant specialized in summarizing meetings in Arabic.
                Your task is to analyze the conversation and summarize it in a specific data structure format.
                Please output the result strictly in the following format:
                {{
                    "meeting_topic": "A brief description of the meeting's topic",
                    "summary": "A comprehensive summary of the meeting, including key points and decisions made"
                }}
                Write in formal Arabic, focusing on the essential points and avoiding unnecessary details. 
                Keep any technical terms or names as they are.
                \n{format_instructions}\n{text}\n""",
            input_variables = ["text"],
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )