#from ..base import Base
from src.db.base import Base
from sqlalchemy import Column, Integer, Enum, Float, DateTime, String
from datetime import datetime
import enum
import os

class SourceType(enum.Enum):
    UPLOAD = "UPLOAD"
    URL = "URL"
    RECORDED = "RECORDED"
    
class MediaInput(Base):
    __tablename__ = "media_inputs"
    
    id = Column(Integer, primary_key=True)
    source_type = Column(Enum(SourceType, name="source_type"), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    source_location = Column(String, nullable=False)
    duration = Column(Float, nullable=False) 
    diarization_csv_path = Column(String, nullable=True)
    summary_json_path = Column(String, nullable=True)
    audio_summary_path = Column(String, nullable=True)
    
    def __repr__(self):
        return (
            f"<MediaInput(id={self.id}, source_type={self.source_type.value}, "
            f"uploaded_at={self.uploaded_at.isoformat()}, "
            f"source_location='{self.source_location}', "
            f"duration={self.duration:.2f}, "
            f"diarization='{os.path.basename(self.diarization_csv_path) if self.diarization_csv_path else None}', "
            f"summary='{os.path.basename(self.summary_json_path) if self.summary_json_path else None}', "
            f"audio='{os.path.basename(self.audio_summary_path) if self.audio_summary_path else None}')>"
        )