from .AbstractAudioHandler import AbstractAudioHandler
from yt_dlp import YoutubeDL
from pathlib import Path
from fastapi import HTTPException

class DownloadAudio(AbstractAudioHandler):
    def __init__(self):
        super().__init__()
        self.download_dir = Path(self.base_service.downloaded_audios_path)
        

    def handle(self, video_url: str) -> dict:
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
    