from datetime import datetime
import pandas as pd
import os

class CSVHandler:
    def __init__(self, output_path: str = "assets/diarization_output"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

    def save_to_csv(self, diarization_result, text_data,audio_file_path: str):
        """
        Save diarization results to a CSV file.
        
        :param diarization_result: The diarization result from pyannote.
        :param audio_file_path: Path to the original audio file.
        :return: Path to the saved CSV file.
        """

        # Extract filename from the path without extension
        base_filename = os.path.basename(audio_file_path)
        print(f"Processing file: {base_filename}")
        audio_name = os.path.splitext(base_filename)[0]

        # Create timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{audio_name}_diarization_{timestamp}.csv"  # Added .csv extension
        csv_path = os.path.join(self.output_path, csv_filename)

        # Create a list to store all segments
        segments = []

        # Extract segments from diarization result
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
        
        # Convert to DataFrame for easy CSV export
        df = pd.DataFrame(segments)  # Fixed variable name: segment → segments

        # Save to CSV
        df.to_csv(csv_path, index=False)
        print(f"CSV saved to: {csv_path}")

        return csv_path