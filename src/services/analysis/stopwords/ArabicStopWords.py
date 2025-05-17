from .AbstractStopWords import AbstractStopWords
from arabicstopwords import arabicstopwords as stp
from nltk.tokenize import word_tokenize

class ArabicStopWords(AbstractStopWords):
    def __init__(self):
        super().__init__()

    def get(self) -> set:
        try:
            set_stopwords = set(stp.stopwords_list())
            self.logger.info("Successfully got all arabic stopwords")
            return set_stopwords
        except Exception as e:
            self.logger.exception(f"Error while removing arabic stopwords {e}")
            raise