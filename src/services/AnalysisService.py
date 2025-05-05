from .BaseService import BaseService
from .DataLoaderService import DataLoaderService
from .SpeakerAnalyzerService import SpeakerAnalyzerService
from .TextAnalyzerService import TextAnalyzerService
from .StopwordsService import StopwordsService

class AnalysisService(BaseService):
    def __init__(self, csv_path: str):
        """
        Initialize the AnalysisService with a CSV file path.
        
        Args:
            csv_path (str): Path to the CSV file containing diarization results.
        """
        super().__init__()
        loader = DataLoaderService(csv_path)
        stopwords_provider = StopwordsService()
        
        self.df = loader.get_data()
        self.text_analyzer = TextAnalyzerService(self.df, stopwords_provider.get())
        self.speaker_analyzer = SpeakerAnalyzerService(self.df)
        self.logger.info("AnalysisService initialized with CSV data.")

    def get_most_talked_speakers(self, top_n: int = 5):
        return self.speaker_analyzer.get_most_talked(top_n)
    
    def get_total_duration_for_each_speaker(self):
        return self.speaker_analyzer.get_total_duration()
    
    def get_all_words(self):
        return self.text_analyzer.get_all_words()
    
    def get_most_used_word(self):
        return self.text_analyzer.get_most_used_word()
    
    def get_total_number_of_speakers(self):
        return self.speaker_analyzer.get_total_number_of_speakers()