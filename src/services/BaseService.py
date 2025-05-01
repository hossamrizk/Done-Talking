from helpers import get_settings
import logging
import os

class BaseService:
    def __init__(self):
        self.app_settings = get_settings()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.diarization_output_path = self.ensure_path("assets", "diarization_output")
        self.downloaded_audios_path = self.ensure_path("assets", "downloaded_audios")
        self.uploaded_audios_path = self.ensure_path("assets", "uploaded_audios")
        self.generated_reports_path = self.ensure_path("assets", "generated_reports")
        self.generated_audios_path = self.ensure_path("assets", "generated_audios")

    def ensure_path(self, *segments):
        path = os.path.join(self.base_dir, *segments)
        os.makedirs(path, exist_ok=True)
        return path
