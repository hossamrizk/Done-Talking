from controllers import DownloadController, AudioController
from db import SourceType
from fastapi import APIRouter, UploadFile, File, HTTPException


download_handler = DownloadController()
audio_processor = AudioController()


download_router = APIRouter()
@download_router.post("/download_audio")
async def upload_audio(audio: UploadFile = File(...)):
    """Download and process audio file"""
    try:
        file_path = download_handler.get_file_path(audio)
        return await audio_processor.process(file_path, SourceType.URL)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
