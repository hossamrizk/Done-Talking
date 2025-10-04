from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from src.controllers import RecordedController, AudioController
from src.db import SourceType
from src.middleware.rate_limit import RateLimits, limiter



accept_audio_router = APIRouter()
recorded_controller = RecordedController()
audio_processor = AudioController()

@accept_audio_router.post("/receive_meeting")
@limiter.limit(RateLimits.UPLOAD)
async def process_audio(
    audio_file: UploadFile = File(...),
    platform: str = Form(...),
    timestamp: str = Form(...)
):
    
    try:
        file_result = recorded_controller.get_file_path(
            audio_file=audio_file,
            platform=platform,
            timestamp=timestamp
        )

        if isinstance(file_result, JSONResponse):
            return file_result

        recorded_meeting, full_file_path, meeting_platform, meeting_timestamp = file_result
        result = await audio_processor.process(full_file_path, SourceType.RECORDED)
        return result

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"An error occurred: {str(e)}"
            }
        )
