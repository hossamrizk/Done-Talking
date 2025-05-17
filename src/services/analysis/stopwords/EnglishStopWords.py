from .AbstractStopWords import AbstractStopWords
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

class EnglishStopWords(AbstractStopWords):
    def __init__(self):
        super().__init__()
        nltk.download('stopwords', quiet=True)

    def get(self) -> set:
        try: 
            set_stopwords = set(stopwords.words('english'))
            self.logger.info("Successfully got all english stopwords")
            return set_stopwords
        except Exception as e:
            self.logger.exception(f"Error while removing english stopwords {e}")
            raise