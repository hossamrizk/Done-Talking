from fastapi import APIRouter, HTTPException
from services import AudioTransfer, AudioSummarization, AudioDiarization
from fastapi import UploadFile, File
from typing import Dict, Any
import os

upload_audio_router = APIRouter()
@upload_audio_router.post("/upload_audio")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        # Upload and process audio
        at = AudioTransfer()
        uploaded_file_path = at.upload_audio(file=audio)
        
        # Run diarization
        ad = AudioDiarization()
        diarization_result, text_data = ad.diarize(audio_file=uploaded_file_path)
        
        # Generate summary
        audio_summaryization = AudioSummarization()
        summary = audio_summaryization.summarization(text_data)
        
        # Save report
        report_path = audio_summaryization.generate_report(summary)
        
        return {
            "status": "success",
            "message": "Audio processed successfully",
            "report_path": report_path
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")