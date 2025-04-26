from yt_dlp import YoutubeDL
from pathlib import Path
from fastapi import UploadFile
import os


class AudioTransfer:
    def __init__(self, downloaded_audios_path: str = "assets/downloaded_audios", uploaded_audios_path: str = "assets/uploaded_audios"):
        self.download_dir = Path(downloaded_audios_path)
        self.uploaded_dir = Path(uploaded_audios_path)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.uploaded_dir.mkdir(parents=True, exist_ok=True)

    def download_audio(self, video_url: str) -> dict[str, str]:
        try:
            ydl_opts = {
                'cookiesfrombrowser': ('chrome',),
                'format': 'bestaudio/best',
                'outtmpl': f'{self.download_dir}/%(title)s.%(ext)s',
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
                # Get the filename from the info dictionary
                filename = ydl.prepare_filename(info)
                # Change extension to .mp3 since we're extracting audio
                mp3_filename = os.path.splitext(filename)[0] + '.mp3'
                return str(mp3_filename)
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
        
    def upload_audio(self, file: UploadFile) -> dict[str, str]:
        if not file.filename.endswith('.mp3'):
            raise ValueError("Invalid file type. Only .mp3 files are allowed.")

        destination = self.uploaded_dir / file.filename

        if destination.exists():
            print(f"File already exists: {destination}")
            return {"status": "success", "message": f"File {file.filename} already exists", "file_path": str(destination)}


        with open(destination, "wb") as buffer:
            buffer.write(file.file.read())

        return str(destination)