from controllers import DownloadController, AudioController
from db import SourceType
from schemas import DownloadRequest
from fastapi import HTTPException, APIRouter


download_handler = DownloadController()
audio_processor = AudioController()


download_router = APIRouter()
@download_router.post("/download_audio")
async def upload_audio(request: DownloadRequest):
    """Download and process audio file"""
    try:
        video_url = request.video_url
        file_path = download_handler.get_file_path(video_url = video_url)
        return await audio_processor.process(file_path, SourceType.URL)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
