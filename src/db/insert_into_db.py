from .models import MediaInput
from .session import get_db

def insert_into_db(source_type, source_location, duration, diarization_csv_path, summary_json_path, audio_summary_path):
    db = next(get_db())
    
    new_media = MediaInput(
        source_type = source_type,
        source_location = source_location,
        duration = duration,
        diarization_csv_path = diarization_csv_path,
        summary_json_path = summary_json_path,
        audio_summary_path = audio_summary_path
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    print(f"Successfully inserted data in DB")
    