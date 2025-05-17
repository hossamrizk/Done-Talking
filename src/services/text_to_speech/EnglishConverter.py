from .AbstractConverter import AbstractConverter
import edge_tts

class EnglishConverter(AbstractConverter):
    def __init__(self, base_service=None):
        super().__init__(base_service=base_service, voice="en-GB-RyanNeural")

    async def convert(self, text: str):
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(self.audio_path)
            self.logger.info(f"Successfully converted english text into audio and file saved at {self.audio_path}")
            return self.audio_path
        except Exception as e:
            self.logger.exception(f"Error while trying to convert english text into audio {e}")
            raise