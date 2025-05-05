from .BaseService import BaseService
import edge_tts
import os
import uuid

class TTSService(BaseService):
    def __init__(self, voice: str = "en-GB-RyanNeural"):
        super().__init__()
        self.voice = voice

    async def convert_text_to_speech(self, text: str):
        output_filename = f"output_{uuid.uuid4().hex}.mp3"
        audio_path = os.path.join(self.generated_audios_path, output_filename)
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(audio_path)
        return audio_path

