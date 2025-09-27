from abc import ABC, abstractmethod
from src.services.BaseService import BaseService
from src.helpers import unique_file_name
from pathlib import Path
import os

class AbstractConverter(ABC):
    def __init__(self, base_service=None, voice=None):
        self.base_service = base_service or BaseService()
        self.logger = self.base_service.logger
        self.generated_audios_path = Path(self.base_service.generated_audios_path)
        self.output_filename = unique_file_name(file_extension="mp3")
        self.audio_path = os.path.join(self.generated_audios_path, self.output_filename)
        self.voice = voice
        
    @abstractmethod
    async def convert(self, text: str) -> str:
        pass