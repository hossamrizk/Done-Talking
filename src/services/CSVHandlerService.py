from .BaseService import BaseService
from datetime import datetime
from path import Path
import pandas as pd
import os

class CSVHandlerService(BaseService):
    def __init__(self, output_path: Path):
        super().__init__()
        self.output_path = Path(self.diarization_output_path)

    def save_to_csv(self, diarization_result, text_data,audio_file_path: str):
        """
        Save diarization results to a CSV file.
        
        :param diarization_result: The diarization result from pyannote.
        :param audio_file_path: Path to the original audio file.
        :return: Path to the saved CSV file.
        """

        base_filename = os.path.basename(audio_file_path)
        self.logger.info(f"Processing file: {base_filename}")
        print(f"Processing file: {base_filename}")
        audio_name = os.path.splitext(base_filename)[0]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{audio_name}_diarization_{timestamp}.csv"  
        csv_path = os.path.join(self.output_path, csv_filename)

        segments = []

        for turn, _, speaker in diarization_result.itertracks(yield_label=True):  
            mathcing_text = [
                t['text'] for t in text_data
                if t['start'] >= turn.start and t['end'] <= turn.end
            ]
            text = ' '.join(mathcing_text) if mathcing_text else ''
            segment = {
                'start': turn.start,
                'end': turn.end,
                'duration': turn.duration,
                'speaker': speaker,
                'text':text
            }
            segments.append(segment)
        
        df = pd.DataFrame(segments)  

        # Save to CSV
        df.to_csv(csv_path, index=False)
        self.logger.info(f"CSV saved to: {csv_path}")
        print(f"CSV saved to: {csv_path}")

        return csv_path