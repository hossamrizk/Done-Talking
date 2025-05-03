from pyannote.audio import Pipeline
from .CSVHandlerService import CSVHandler  
from .AudioTranscriptionService import AudioTranscription
from .BaseService import BaseService
from helpers.config import get_settings
from pathlib import Path
import torch

class AudioDiarizationService(BaseService):
    def __init__(self):
        super().__init__()

        self.output_path = Path(self.diarization_output_path) 

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger.info(f"Using device: {self.device}")  
        print(f"Using device: {self.device}")  
        
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

        self.logger.info(f"Starting diarization for {audio_file}")

        diarization = self.pipeline(audio_file)
        self.logger.info(f"Diarization completed for {audio_file}")
        
        transcriber = AudioTranscription(audio_file)
        self.logger.info(f"Transcriber initialized for {audio_file}")

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
            self.logger.info(f"Diarization results saved to CSV: {csv_path}")
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