import nltk 
from nltk.corpus import stopwords
from .BaseService import BaseService

class StopwordsService(BaseService):
    def __init__(self, language: str = 'english'):
        """
        Initialize the StopwordsService with a specified language.
        
        Args:
            language (str): The language for which to load stopwords. Default is 'english'.
        """
        super().__init__()
        nltk.download('stopwords', quiet=True)
        self.stop_words = set(stopwords.words(language))
        self.logger.info(f"StopwordsService initialized with {language} stop words.")

    def get(self) -> set:
        """
        Get the set of stopwords.
        
        Returns:
            set: A set of stopwords for the specified language.
        """
        self.logger.info("Stop words retrieved.")
        return self.stop_words