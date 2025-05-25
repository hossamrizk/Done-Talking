from ..BaseService import BaseService
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import re

class TextAnalyzer(BaseService):
    def __init__(self, df, stopwords: set):
        """
        Initialize the TextAnalyzerService with a DataFrame and a set of stopwords.
        
        Args:
            df (pd.DataFrame): DataFrame containing the text data.
            stopwords (set): Set of stopwords to be ignored in analysis.
        """
        super().__init__()
        self.df = df
        self.stopwords = stopwords
        self.logger.info("TextAnalyzerService initialized with DataFrame and stopwords.")

    def get_all_words(self) -> List[str]:
        """
        Get all words from the DataFrame, excluding stopwords.
        
        Returns:
            List[str]: List of all words.
        """
        self.logger.info("Extracting all words from the DataFrame.")
        text = ' '.join(self.df['text'].dropna()).lower()
        return re.findall(r'\b\w+\b', text)
    
    def get_most_used_word(self) -> Tuple[str, int, Dict[str, int]]:
        """
        Get the most used word in the DataFrame, excluding stopwords.
        
        Returns:
            Tuple[str, int, Dict[str, int]]: Most used word, its count, and a dictionary of all words with their counts.
        """
        self.logger.info("Calculating the most used word in the DataFrame.")
        word_counts = Counter()
        speaker_word_map = defaultdict(Counter)

        for _, row in self.df.iterrows():
            test = str(row['text']).lower()
            speaker = row['speaker']
            words = re.findall(r'\b\w+\b', test)
            filtered = [w for w in words if w not in self.stopwords]
            word_counts.update(filtered)
            speaker_word_map[speaker].update(filtered)
        
        top_word, freq = word_counts.most_common(1)[0]
        speaker_counts = {
            speaker: counter[top_word]
            for speaker, counter in speaker_word_map.items()
            if top_word in counter
        }
        return top_word, freq, speaker_counts
    
    