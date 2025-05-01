from services.BaseService import BaseService
from yt_dlp import YoutubeDL
from pathlib import Path
from fastapi import UploadFile, HTTPException
import os


class AudioTransfer(BaseService):
    def __init__(self):
        super().__init__()
        self.download_dir = Path(self.downloaded_audios_path)
        self.uploaded_dir = Path(self.uploaded_audios_path)
        
    def download_audio(self, video_url: str) -> dict:
        try:
            ydl_opts = {
                'cookiesfrombrowser': ('chrome',),
                'format': 'bestaudio/best',
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                "socket_timeout": 60,
                "retries": 10,
                "quiet": False
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = Path(ydl.prepare_filename(info))
                mp3_filename = filename.with_suffix('.mp3')
                self.logger.info(f"Downloaded audio file: {mp3_filename}")
                
                return {
                    "status": "success",
                    "file_path": str(mp3_filename),
                    "filename": mp3_filename.name
                }
                
        except Exception as e:
            self.logger.error(f"Error downloading audio: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Audio download failed: {str(e)}"
            )
        
    def upload_audio(self, file: UploadFile) -> dict:
        if not file.filename or not file.filename.lower().endswith('.mp3'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .mp3 files are allowed."
            )

        try:
            destination = self.uploaded_dir / file.filename
            
            if destination.exists():
                self.logger.info(f"File already exists: {destination}")
                return {
                    "status": "success",
                    "message": "File already exists",
                    "file_path": str(destination),
                    "filename": file.filename
                }

            with open(destination, "wb") as buffer:
                buffer.write(file.file.read())

            return {
                "status": "success",
                "file_path": str(destination),
                "filename": file.filename
            }
            
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"File upload failed: {str(e)}"
            )