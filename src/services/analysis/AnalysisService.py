from ..BaseService import BaseService
from .DataLoader import DataLoader
from .SpeakerAnalyzer import SpeakerAnalyzer
from .TextAnalyzer import TextAnalyzer
from .stopwords import ArabicStopWords, EnglishStopWords
from langdetect import detect

class AnalysisService(BaseService):
    def __init__(self, csv_path: str):
        """
        Initialize the AnalysisService with a CSV file path.
        
        Args:
            csv_path (str): Path to the CSV file containing diarization results.
        """
        super().__init__()
        loader = DataLoader(csv_path)
        self.df = loader.get_data()
        sample_text = ' '.join(self.df['text'].dropna().astype(str).head(5).tolist())
        self.language_code = detect(sample_text)
        self.logger.info(f"Detected language is {self.language_code}")

        if self.language_code == 'ar':
            stopwords_provider = ArabicStopWords()
        elif self.language_code == 'en':
            stopwords_provider = EnglishStopWords()
        
        self.df = loader.get_data()
        self.text_analyzer = TextAnalyzer(self.df, stopwords_provider.get())
        self.speaker_analyzer = SpeakerAnalyzer(self.df)
        self.logger.info("AnalysisService initialized with CSV data.")

    def get_language_type(self):
        return self.language_code

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