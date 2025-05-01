from pyannote.audio import Pipeline
from services.CSVHandler import CSVHandler  
from services.AudioTranscription import AudioTranscription
from services.BaseService import BaseService
from helpers.config import get_settings
import os
import torch

class AudioDiarization(BaseService):
    def __init__(self):
        super().__init__()

        self.output_path = self.diarization_output_path 

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")  
        
        # Load the pipeline and move it to the appropriate device
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization", 
            use_auth_token=get_settings().HF_TOKEN
        ).to(self.device)
         

    def diarize(self, audio_file: str, save_csv: bool = True):
        """
        Perform speaker diarization on the given audio file with transcription.
        
        :param audio_file: Path to the audio file to be diarized.
        :param save_csv: Whether to save the results to a CSV file.
        :return: Diarization result and transcript.
        """
        # 1. Perform diarization
        diarization = self.pipeline(audio_file)
        
        # 2. Initialize the transcription class
        transcriber = AudioTranscription(audio_file)
        
        # 3. Build the transcript with timestamps
        text_data = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            audio_segment = transcriber.extract_segments(turn.start, turn.end)
            text = transcriber.transcribe_segment(audio_segment)
            text_data.append({
                'start': turn.start,
                'end': turn.end,
                'text': text
            })
        
        if save_csv:
            csv_handler = CSVHandler(output_path=self.output_path)
            csv_path = csv_handler.save_to_csv(diarization, text_data, audio_file)
            print(f"Diarization results saved to CSV: {csv_path}")
        
        return diarization, text_data, csv_path
    
    def get_speaker_timeline(self, diarization_result):
        """
        Get a chronological timeline of speaker segments.
        
        :param diarization_result: The diarization result from pyannote.
        :return: List of dictionaries with speaker timeline info.
        """
        timeline = []
        for turn, _, speaker in diarization_result.itertracks(yield_label=True):
            timeline.append({
                'start': turn.start,
                'end': turn.end,
                'duration': turn.duration,
                'speaker': speaker
            })
        return timeline