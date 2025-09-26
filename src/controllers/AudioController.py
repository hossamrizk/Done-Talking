from .language_processor import EnglishController, ArabicController
from services import AudioDiarization, AnalysisService
from fastapi import HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any, Tuple
from db import SourceType, insert_into_db
from pydub import AudioSegment
import os

class AudioController:
    """Main processor that orchestrates everything"""
    
    def __init__(self):
        self.diarization = AudioDiarization()
        self.processors = {
            'en': EnglishController(),
            'ar': ArabicController()
        }
    
    def _analyze_audio(self, file_path: str) -> Tuple[str, Dict[str, Any], str]:
        """Analyze audio and return CSV path, analysis data, and language"""
        print(file_path)
        _, _, csv_path = self.diarization.diarize(audio_file=file_path)
        analysis_service = AnalysisService(csv_path=csv_path)
        
        analysis_data = {
            "most_talked_speakers": analysis_service.get_most_talked_speakers(top_n=2),
            "total_duration": analysis_service.get_total_duration_for_each_speaker(),
            "most_used_word": analysis_service.get_most_used_word(),
            "total_speakers": analysis_service.get_total_number_of_speakers(),
            "audio_duration": analysis_service.get_total_audio_duration(audio_path=file_path)
        }
        
        language = analysis_service.get_language_type()
        return csv_path, analysis_data, language
    
    async def process(self, file_path: str, source_type: SourceType) -> FileResponse:
        """Process audio file and return result"""
        try:
            # Convert audio format to mp3
            if file_path.endswith(".webm"):
                print(f"Processing WebM file: {file_path}")
                audio = AudioSegment.from_file(file_path, format="webm")
                output_path = file_path.replace(".webm", ".mp3")
                audio.export(output_path, format="mp3", bitrate="192k")
                print(f"Converted to: {output_path}")
                file_path = output_path

            # Analyze audio
            csv_path, analysis_data, language = self._analyze_audio(file_path)
            
            # Get processor for language
            if language not in self.processors:
                raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
            
            processor = self.processors[language]
            
            # Process text
            final_text, json_path = processor.process_text(csv_path, analysis_data)
            
            # Convert to audio
            audio_path = await processor.tts.convert(final_text)
            
            if not os.path.exists(audio_path):
                raise HTTPException(status_code=500, detail="Audio generation failed")
            
            # Save to database
            insert_into_db(
                source_type=source_type,
                source_location=file_path,
                duration=analysis_data["audio_duration"],
                diarization_csv_path=csv_path,
                summary_json_path=json_path,
                audio_summary_path=audio_path
            )
            
            return FileResponse(audio_path, media_type="audio/mpeg")
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Processing error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
