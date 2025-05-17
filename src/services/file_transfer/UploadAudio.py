from .AbstractAudioHandler import AbstractAudioHandler
from pathlib import Path
from fastapi import UploadFile, HTTPException

class UploadAudio(AbstractAudioHandler):
    def __init__(self):
        super().__init__()
        self.uploaded_audios_path = Path(self.base_service.uploaded_audios_path)

    def handle(self, file: UploadFile) -> dict:
        if not file.filename or not file.filename.lower().endswith('.mp3'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .mp3 files are allowed."
            )

        try:
            destination = self.uploaded_audios_path / file.filename
            
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