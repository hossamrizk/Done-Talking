from .AbstractConverter import AbstractConverter
import edge_tts

class ArabicConverter(AbstractConverter):
    def __init__(self, base_service=None):
        super().__init__(base_service=base_service, voice="ar-SA-HamedNeural")

    async def convert(self, text: str):
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(self.audio_path)
            self.logger.info(f"Successfully converted arabic text into audio and file saved at {self.audio_path}")
            return self.audio_path
        except Exception as e:
            self.logger.exception(f"Error while trying to convert arabic text into audio {e}")
            raise