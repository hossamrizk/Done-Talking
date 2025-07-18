from controllers import UploadController, AudioController
from db import SourceType
from fastapi import APIRouter, UploadFile, File, HTTPException


upload_handler = UploadController()
audio_processor = AudioController()


upload_router = APIRouter()
@upload_router.post("/upload_audio")
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
