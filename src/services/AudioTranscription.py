from services.BaseService import BaseService
from pydub import AudioSegment
import tempfile
import whisper
import os

class AudioTranscription(BaseService):
    def __init__(self, audio_path, transcribe_model: str = "base"):
        super().__init__()

        self.audio_path = audio_path
        self.transcribe_model = whisper.load_model(transcribe_model)
        self.logger.info(f"Transcription model {transcribe_model} loaded.")
    
    def extract_segments(self, start_time, end_time):

        """
        Extract segments from the audio file.
        
        :param start_time: Start time in milliseconds.
        :param end_time: End time in milliseconds.
        :return: Extracted audio segment.
        """
        audio = AudioSegment.from_file(self.audio_path)
        return audio[start_time*1000 : end_time*1000]
        
    def transcribe_segment(self, audio_segment):
        """
        Transcribe the given audio segment.
        
        :param audio_segment: Audio segment to be transcribed.
        :return: Transcription result.
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_segment.export(f.name, format="wav")
            result = self.transcribe_model.transcribe(f.name)
        os.remove(f.name)
        return result['text']
    
    def build_trascript(self, diarization):
        transcript = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            audio_segment = self.extract_segments(turn.start, turn.end)
            text = self.transcribe_segment(audio_segment=audio_segment)
            transcript.append((speaker, text))
        return transcript

