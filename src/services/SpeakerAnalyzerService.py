from .BaseService import BaseService
from typing import List, Dict
import pandas as pd 
from langdetect import detect

class SpeakerAnalyzerService(BaseService):
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the SpeakerAnalyzer with a DataFrame containing diarization results.
        
        Args:
            df (pd.DataFrame): DataFrame containing the diarization results.
        """
        super().__init__()
        self.df = df
        self.logger.info("SpeakerAnalyzer initialized with DataFrame.")

    def get_most_talked(self, n: int = 5) -> List[str]:
        """
        Get the most talked speakers from the DataFrame.
        
        Args:
            n (int): Number of top speakers to return.
        
        Returns:
            List[str]: List of most talked speakers.
        """
        self.logger.info(f"Getting the top {n} most talked speakers.")
        return self.df['speaker'].value_counts().head(n).index.tolist()
    
    def get_total_duration(self) -> Dict[str, int]:
        """
        Get the total duration of each speaker as integers.
        
        Returns:
            Dict[str, int]: Dictionary with speakers as keys and their total duration (int) as values.
        """
        self.logger.info("Calculating total duration for each speaker.")
        total_duration = self.df.groupby('speaker')['duration'].sum().to_dict()
        return {speaker: int(duration) for speaker, duration in total_duration.items()}
    
    def get_total_number_of_speakers(self) -> int:
        """
        Get the total number of unique speakers.
        
        Returns:
            int: Total number of unique speakers
        """
        self.logger.info("Calculating total number of unique speakers")
        return self.df['speaker'].unique().size

    def get_text_language(self) -> str:
        """
        Detect the language of the text in the DataFrame.
        
        Returns:
            str: Detected language code (e.g., 'en' for English).
        """
        self.logger.info("Detecting language of the text.")
        text = str(self.df['text'].iloc[0])
        return detect(text)