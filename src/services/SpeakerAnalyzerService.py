from .BaseService import BaseService
from typing import List, Dict
import pandas as pd 

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
    
    def get_total_duration(self) -> Dict[str, float]:
        """
        Get the total duration of each speaker.
        
        Returns:
            Dict[str, float]: Dictionary with speakers as keys and their total duration as values.
        """
        self.logger.info("Calculating total duration for each speaker.")
        return self.df.groupby('speaker')['duration'].sum().to_dict()