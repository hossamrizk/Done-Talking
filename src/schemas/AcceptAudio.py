from pydantic import BaseModel
from fastapi import File, UploadFile, Form

class AcceptAudio(BaseModel):
    audio_file: UploadFile = File(...)
    platform: str = Form(...)
    timestamp: str = Form(...)

