from .AbstractLanguage import AbstractLanguage
from services import BaseService, ArabicSummary, ArabicFormatter, ArabicConverter
from typing import Dict, Any, Tuple
from helpers import load_csv, load_json
from fastapi import HTTPException
import os

class ArabicController(AbstractLanguage):
    def __init__(self):
        self.summary_service = ArabicSummary()
        self.formatter = ArabicFormatter()
        self.tts = ArabicConverter()
        
        base_service = BaseService()
        self.logger = base_service.logger
        
    def process_text(self, csv_path: str, analysis_data: Dict[str, Any]) -> Tuple[str,str]:
        """
        Process the text from the CSV file and return the summary and TTS file paths.
        
        :param csv_path: Path to the CSV file containing the text data.
        :param analysis_data: Dictionary containing analysis data such as most talked speakers, total duration, etc.
        :return: Tuple containing the summary json file and formatted text.
        """
        try:
            clean_word = self.formatter.replace_speaker_tags(
            self.formatter.clean_field(analysis_data["most_used_word"])
        )
            # Format data
            formatted_data = self.formatter.replace_speaker_tags(
                self.formatter.format_summary({
                    "أكثر المتحدثيين هم": analysis_data["most_talked_speakers"],
                    "اجمالى وقت التحدث": analysis_data["total_duration"],
                    "أكثر الكلمات استخدامآ": clean_word
                })
            )
            self.logger.info(f"Formatted Arabic data: {formatted_data}")
        except Exception as e:
            self.logger.error(f"Error formatting Arabic data: {e}")
            raise HTTPException(status_code=500, detail="Error formatting Arabic data")
        
        try:
            # Create Summary
            _, text = load_csv(csv_path=csv_path)
            clean_text = self.formatter.replace_speaker_tags(text)
            json_summary_path = self.summary_service.create_summary(text=clean_text)
            
            if not os.path.exists(json_summary_path):
                self.logger.info("Error Arabic summary json file not found")
                raise HTTPException(status_code=500, detail="Summary JSON file not found")
            self.logger.info(f"Summary JSON created at: {json_summary_path}")
        except Exception as e:
            self.logger.error(f"Error creating Arabic summary: {e}")
            raise HTTPException(status_code=500, detail="Error creating Arabic summary")
        
        try:
            # Get text data
            meeting_topic, summary = load_json(json_summary_path)
            final_text = f"""
                عنوان الاجتماع: {meeting_topic},
                هذه بعض الاحصائيات بخصوص الاجتماع: العدد الكلي للمتحدثين هو {analysis_data["total_speakers"]}, {formatted_data},
                ملخص الاجتماع: {summary}
            """
            self.logger.info(f"Final text for TTS: {final_text}")
            return final_text, json_summary_path
        except Exception as e:
            self.logger.error(f"Error loading Arabic JSON data: {e}")
            raise HTTPException(status_code=500, detail="Error loading Arabic JSON data")