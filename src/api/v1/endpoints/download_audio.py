from fastapi import HTTPException, APIRouter, Request
from src.controllers import DownloadController, AudioController
from src.middleware.rate_limit import RateLimits, limiter
from src.db import SourceType
from src.schemas import DownloadRequest


download_handler = DownloadController()
audio_processor = AudioController()


download_router = APIRouter()
@download_router.post("/download_audio")
@limiter.limit(RateLimits.DOWNLOAD)
async def download_audio(download_request: DownloadRequest, request: Request):
    """Download and process audio file"""
    try:
        video_url = download_request.video_url
        file_path = download_handler.get_file_path(video_url = video_url)
        return await audio_processor.process(file_path, SourceType.URL)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
