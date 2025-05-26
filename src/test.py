from abc import ABC, abstractmethod
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from services import (UploadAudio, DownloadAudio, AudioDiarization, AnalysisService,
                      EnglishSummary, ArabicSummary, EnglishConverter, ArabicConverter,
                      EnglishFormatter, ArabicFormatter)
from db import insert_into_db, SourceType
from helpers import load_csv, load_json
import os
from typing import Dict, Any, Tuple
from pydantic import BaseModel

# Request model
class VideoDownloadRequest(BaseModel):
    url: str

# SOLID: Single Responsibility - Each class has one job
class AudioFileHandler(ABC):
    """Abstract base for getting audio files"""
    
    @abstractmethod
    def get_file_path(self, *args, **kwargs) -> str:
        pass

class UploadHandler(AudioFileHandler):
    """Handles file uploads"""
    
    def __init__(self):
        self.upload_service = UploadAudio()
    
    def get_file_path(self, audio: UploadFile) -> str:
        result = self.upload_service.handle(file=audio)
        if result["status"] != "success" or "file_path" not in result:
            raise HTTPException(status_code=400, detail="Failed to upload audio")
        return result["file_path"]

class DownloadHandler(AudioFileHandler):
    """Handles video downloads"""
    
    def __init__(self):
        self.download_service = DownloadAudio()
    
    def get_file_path(self, url: str) -> str:
        result = self.download_service.handle(url=url)
        if result["status"] != "success" or "file_path" not in result:
            raise HTTPException(status_code=400, detail="Failed to download video")
        return result["file_path"]

# SOLID: Open/Closed - Easy to add new language processors
class LanguageProcessor(ABC):
    """Base class for language processing"""
    
    @abstractmethod
    def process_text(self, csv_path: str, analysis_data: Dict[str, Any]) -> Tuple[str, str]:
        pass

class EnglishProcessor(LanguageProcessor):
    """Processes English audio"""
    
    def __init__(self):
        self.summary = EnglishSummary()
        self.formatter = EnglishFormatter()
        self.tts = EnglishConverter()
    
    def process_text(self, csv_path: str, analysis_data: Dict[str, Any]) -> Tuple[str, str]:
        # Format data
        formatted_data = self.formatter.format_summary({
            "most_talked_speakers": analysis_data["most_talked_speakers"],
            "total_duration": analysis_data["total_duration"],
            "most_used_word": analysis_data["most_used_word"]
        })
        
        # Create summary
        _, text = load_csv(csv_path=csv_path)
        json_path = self.summary.create_summary(text=text)
        
        if not os.path.exists(json_path):
            raise HTTPException(status_code=500, detail="Summary creation failed")
        
        meeting_topic, summary = load_json(json_path)
        
        final_text = f"""
            Meeting Topic: {meeting_topic}
            Analysis: Total speakers: {analysis_data["total_speakers"]}, {formatted_data}
            Summary: {summary}
        """
        
        return final_text, json_path

class ArabicProcessor(LanguageProcessor):
    """Processes Arabic audio"""
    
    def __init__(self):
        self.summary = ArabicSummary()
        self.formatter = ArabicFormatter()
        self.tts = ArabicConverter()
    
    def process_text(self, csv_path: str, analysis_data: Dict[str, Any]) -> Tuple[str, str]:
        # Clean Arabic data
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
        
        # Create summary
        _, text = load_csv(csv_path=csv_path)
        clean_text = self.formatter.replace_speaker_tags(text)
        json_path = self.summary.create_summary(text=clean_text)
        
        if not os.path.exists(json_path):
            raise HTTPException(status_code=500, detail="Summary creation failed")
        
        meeting_topic, summary = load_json(json_path)
        
        final_text = f"""
            عنوان الاجتماع: {meeting_topic}
            الاحصائيات: العدد الكلي للمتحدثين {analysis_data["total_speakers"]}, {formatted_data}
            ملخص الاجتماع: {summary}
        """
        
        return final_text, json_path

# SOLID: Dependency Inversion - Main service depends on abstractions
class AudioProcessor:
    """Main processor that orchestrates everything"""
    
    def __init__(self):
        self.diarization = AudioDiarization()
        self.processors = {
            'en': EnglishProcessor(),
            'ar': ArabicProcessor()
        }
    
    def _analyze_audio(self, file_path: str) -> Tuple[str, Dict[str, Any], str]:
        """Analyze audio and return CSV path, analysis data, and language"""
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

# Initialize services
upload_handler = UploadHandler()
download_handler = DownloadHandler()
audio_processor = AudioProcessor()
from fastapi import FastAPI

# Router
app = FastAPI()

@app.post("/upload_audio")
async def upload_audio(audio: UploadFile = File(...)):
    """Upload and process audio file"""
    try:
        file_path = upload_handler.get_file_path(audio)
        return await audio_processor.process(file_path, SourceType.UPLOAD)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

