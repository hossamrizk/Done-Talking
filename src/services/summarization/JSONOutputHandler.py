from src.services.BaseService import BaseService
from src.helpers import unique_file_name
import json
import os

class JSONOutputHandler:
    """Implementation of OutputHandler that saves output data as a JSON file."""
    def __init__(self, base_service: BaseService):
        self.base_service = base_service
        self.output_path = self.base_service.generated_reports_path
        self.filename = unique_file_name(file_extension="json")
        self.filepath = os.path.join(self.output_path, self.filename)
        self.logger = self.base_service.logger
        self.logger.info(f"JSONOutputHandler initialized with output path: {self.output_path} and filename: {self.filename}")

    def save_output(self, data) -> str:
        """
        Saves data to a JSON file and returns the path to the saved file.

        Args:
            data: The data to save.

        Raises:
            FileNotFoundError: If the file could not be created.
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                return self.filepath
        except Exception as e:
            self.logger.error(f"Error saving JSON output: {e}")
            raise FileNotFoundError(f"Could not create file at {self.filepath}") from e