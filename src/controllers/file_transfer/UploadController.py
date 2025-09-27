from .AbstractHandler import AbstractHandler
from fastapi import UploadFile, HTTPException
#from services import UploadAudio, BaseService
from src.services.BaseService import BaseService
from src.services.file_transfer.UploadAudio import UploadAudio

class UploadController(AbstractHandler):
    """
    Handler for uploading files.
    """
    def __init__(self):
        self.upload_service = UploadAudio()
        base_service = BaseService()
        self.logger = base_service.logger
        
    def get_file_path(self, audio_file: UploadFile) -> str:
        """
        Returns the file path for the uploaded file.
        """
        try:
            result = self.upload_service.handle(file=audio_file)
            if result["status"] != "success" or "file_path" not in result:
                self.logger.error("Failed to upload file.")
                raise HTTPException(status_code=400, detail="Failed to upload file")
            return result["file_path"]
        except Exception as e:
            self.logger.exception(f"Error during file upload: {str(e)}")
            raise HTTPException(status_code=400, detail="Internal server error during file upload")
