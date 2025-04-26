from langchain_ollama import ChatOllama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from models import MeetingSummary
from datetime import datetime
import os

class AudioSummarization:
    def __init__(self, report_output_path: str = "assets/generated_reports"):
        self.output_path = report_output_path
        self.llm = ChatOllama(
            model="gemma2:9b",  
            temperature=0.5
        )

    def format_transcript_for_prompt(self, transcript):
        """Simplified transcript formatting"""
        if isinstance(transcript, list):
            return "\n".join([f"{seg.get('speaker', 'Unknown')}: {seg.get('text', '')}" 
                            if isinstance(seg, dict)
                            else f"{seg[0]}: {seg[1]}" if len(seg) >= 2 
                            else str(seg)
                            for seg in transcript])
        return str(transcript)

    def summarization(self, transcript):
        """Generate summary from transcript"""
        parser = PydanticOutputParser(pydantic_object=MeetingSummary)
        formatted_transcript = self.format_transcript_for_prompt(transcript)
        prompt_template = PromptTemplate(
            template="""You are an expert meeting analyst. Create a comprehensive summary from this transcript:

        1. First identify the main topic and participants
        2. Extract decisions with clear outcomes
        3. List action items with assignees when mentioned
        4. Capture important discussion points
        5. Flag unresolved matters

        Format exactly as specified below:

        {format_instructions}

        Transcript:
        {formatted_transcript}

        Summary Output:""",
            input_variables=["formatted_transcript"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        formatted_prompt = prompt_template.format(formatted_transcript=formatted_transcript)

        return self.llm.invoke(formatted_prompt)

    def generate_report(self, summary, filename=None):
        """Simply save summary to text file and return path"""
        os.makedirs(self.output_path, exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.txt"
        
        report_path = os.path.join(self.output_path, filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(summary)
        
        return report_path