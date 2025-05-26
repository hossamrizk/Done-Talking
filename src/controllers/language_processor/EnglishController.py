from .AbstractLanguage import AbstractLanguage
from services import EnglishSummary, EnglishFormatter, EnglishConverter, BaseService
from typing import Tuple, Dict, Any
from helpers import load_csv, load_json
from fastapi import HTTPException
import os

class EnglishController(AbstractLanguage):
    def __init__(self):
        self.summary_service = EnglishSummary()
        self.formatter = EnglishFormatter()
        self.tts = EnglishConverter()
        
        base_service = BaseService()
        self.logger = base_service.logger
        
    def process_text(self, csv_path: str, analysis_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Process the text from the CSV file and return the summary and TTS file paths.
        
        :param csv_path: Path to the CSV file containing the text data.
        :param analysis_data: Dictionary containing analysis data such as most talked speakers, total duration, etc.
        :return: Tuple containing the summary json file and formatted text.
        """
        try:
            formatted_data = self.formatter.format_summary({
                "most_talked_speakers": analysis_data["most_talked_speakers"],
                "total_duration": analysis_data["total_duration"],
                "most_used_word": analysis_data["most_used_word"]
                })
            self.logger.info(f"Formatted english data: {formatted_data}")
        except Exception as e:
            self.logger.error(f"Error formatting English data: {e}")
            raise HTTPException(status_code=500, detail="Error formatting English data")
        
        try:    
            # Create Summary
            _, text = load_csv(csv_path=csv_path)
            
            json_summary_path = self.summary_service.create_summary(text=text)
            if not os.path.exists(json_summary_path):
                self.logger.info("Error english summary json file not found")
                raise HTTPException(status_code=500, detail="Summary JSON file not found")
            self.logger.info(f"Summary JSON created at: {json_summary_path}")
        except Exception as e: 
            self.logger.error(f"Error creating English summary: {e}")
            raise HTTPException(status_code=500, detail="Error creating English summary")
        
        try:
            # Get text data
            meeting_topic, summary = load_json(json_summary_path)
            final_text = f"""
                Meeting Topic is: {meeting_topic},
                This is some analysis of this audio: The total number of speakers is {analysis_data["total_speakers"]}, {formatted_data},
                Metting Summary is: {summary}
            """
            self.logger.info(f"Final text for TTS: {final_text}")
            return final_text, json_summary_path
        except Exception as e:
            self.logger.error(f"Error loading English JSON data: {e}")
            raise HTTPException(status_code=500, detail="Error loading English JSON data")