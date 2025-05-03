from .BaseService import BaseService
import edge_tts
import os
class TTSService(BaseService):
    def __init__(self, voice: str = "en-GB-RyanNeural"):
        super().__init__()
        self.voice = voice

    async def convert_text_to_speech(self, text: str):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(os.path.join(self.generated_audios_path, "output.mp3"))


