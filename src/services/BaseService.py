from helpers import get_settings
import logging
import os

class BaseService:
    def __init__(self):
        self.app_settings = get_settings()

        # Get the absolute path to the services directory
        services_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Project root is one level up from services directory
        project_root = os.path.dirname(services_dir)
        
        # Assets directory is in the project root
        self.base_dir = os.path.join(project_root, "assets")
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        self.diarization_output_path = self.ensure_path("diarization_output")
        self.downloaded_audios_path = self.ensure_path("downloaded_audios")
        self.uploaded_audios_path = self.ensure_path("uploaded_audios")
        self.generated_reports_path = self.ensure_path("generated_reports")
        self.generated_audios_path = self.ensure_path("generated_audios")

    def ensure_path(self, *segments):
        path = os.path.join(self.base_dir, *segments)
        try:
            os.makedirs(path, exist_ok=True)
            self.logger.info(f"Directory ensured: {path}")
            return path
        except Exception as e:
            self.logger.error(f"Failed to create directory {path}: {str(e)}")
            raise
    
    def setup_logging(self):
        log_dir = self.ensure_path("logs")
        
        log_file = os.path.join(log_dir, "project.log")
        os.makedirs(log_dir, exist_ok=True) 
        # Set up logging to a file
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,  
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Get the logger instance
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging initialized.")