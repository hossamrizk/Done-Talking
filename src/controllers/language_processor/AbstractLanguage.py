from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

class AbstractLanguage(ABC):
    @abstractmethod
    def process_text(self,csv_path: str, analysis_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Process the text from the CSV file and return the summary and TTS file paths.
        
        :param csv_path: Path to the CSV file containing the text data.
        :param analysis_data: Dictionary containing analysis data such as most talked speakers, total duration, etc.
        :return: Tuple containing the summary json file and formatted text.
        """
        pass