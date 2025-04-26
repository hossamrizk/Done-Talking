import edge_tts

class TTS:
    def __init__(self, voice: str = "en-GB-RyanNeural"):
        self.voice = voice

    async def convert_text_to_speech(self, text: str):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save("/home/aitech/ssd/Done-Talking/src/assets/voice/output.mp3")


