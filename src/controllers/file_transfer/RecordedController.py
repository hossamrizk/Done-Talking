from fastapi.responses import JSONResponse
from fastapi import File, UploadFile, Form
from .AbstractHandler import AbstractHandler
#from services import BaseService
from src.services.BaseService import BaseService
import shutil
import os

base_service = BaseService()

class RecordedController(AbstractHandler):
    def __init__(self):
        self.logger = base_service.logger
        self.output_dir = base_service.recorded_meetings_path
        
    def get_file_path(self, audio_file: UploadFile = File(...), platform: str = Form(...), timestamp: str = Form(...)):
        """
        Download the audio file from the given URL.
        
        :param video_url: URL of the video to download.
        :return: Path to the downloaded audio file.
        """
        try:
            recorded_meeting = audio_file
            meeting_platform = platform
            meeting_timestamp = timestamp

            if not recorded_meeting.content_type.startswith("audio/"):
                self.logger.exception(f"Received file is not audio file, Refusing it...")
                return JSONResponse(
                    status_code=400,
                    content={
                        "error":"The file is not audio file, Refused"
                    }
                ) 
            full_file_path = os.path.join(self.output_dir, recorded_meeting.filename)
            with open(full_file_path, "wb") as buffer:
                shutil.copyfileobj(recorded_meeting.file, buffer)
            self.logger.info(f"Received recorded meeting and its full path is {full_file_path}")
            return recorded_meeting ,full_file_path, meeting_platform, meeting_timestamp
        except Exception as e:
            self.logger.exception(f"Error While saving recorded meeting locally: {e}")
            raise
        
