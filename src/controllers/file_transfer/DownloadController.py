from .AbstractHandler import AbstractHandler
from services import DownloadAudio, BaseService
from fastapi import HTTPException
from schemas import DownloadRequest

class DownloadController(AbstractHandler):
    def __init__(self):
        base_service = BaseService()
        self.logger = base_service.logger
        
        self.download_service = DownloadAudio()
        
    def get_file_path(self, video_url: str) -> str :
        """
        Download the audio file from the given URL.
        
        :param video_url: URL of the video to download.
        :return: Path to the downloaded audio file.
        """
        try:
            video_url = DownloadRequest.video_url
            file_path = self.download_service.handle(video_url = video_url)
            self.logger.info(f"File downloaded successfully and saved at: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"File download failed: {str(e)}"
            )