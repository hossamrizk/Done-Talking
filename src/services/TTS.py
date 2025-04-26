import edge_tts
import asyncio
import json 

class TTS:
    def __init__(self, text_path: str = "src/assets/generated_reports/summarized_report.json", voice: str = "en-GB-RyanNeural"):
        self.text_path = text_path
        self.voice = voice

    async def convert_text_to_speech(self, text: str):
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save("src/assets/voice/output.mp3")

def load_json(json_path: str):
    with open(json_path, 'r') as file:
        data = json.load(file)

    meeting_topic = data["meeting_topic"]
    key_speakers = data["key_speakers"]
    key_decisions = data["key_decisions"]
    action_items = data["action_items"]
    discussion_highlights = data["discussion_highlights"]

    return meeting_topic, key_speakers, key_decisions, action_items, discussion_highlights

tts = TTS()
meeting_topic, key_speakers, key_decisions, action_items, discussion_highlights = load_json(json_path = "src/assets/generated_reports/summarized_report.json") 
text = f"""
Metting Topic is: {meeting_topic},
key Speakers are: {key_speakers},
key Decisions are: {key_decisions},
Action Items are: {action_items},
Discussion Highlights are: {discussion_highlights}
"""
asyncio.run(tts.convert_text_to_speech(text))