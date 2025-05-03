from fastapi import APIRouter, HTTPException, UploadFile, File
from services import AudioTransferService, SummarizationService, AudioDiarizationService, TTSService
from helpers import load_csv, load_json
import os

upload_audio_router = APIRouter()

@upload_audio_router.post("/upload_audio")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        # Upload and process audio
        at = AudioTransferService()
        result = at.upload_audio(file=audio)
        
        if result["status"] == "success" and "file_path" in result:
            uploaded_file_path = result["file_path"]
        else:
            raise HTTPException(status_code=400, detail="Failed to upload audio")

        # Run diarization
        ad = AudioDiarizationService()
        _, _, csv_path = ad.diarize(audio_file=uploaded_file_path)
        
        # Load csv file
        speakers, text = load_csv(csv_path=csv_path)

        # Summarization
        sg = SummarizationService()
        result = sg.run_summarization_crew(speakers=speakers, text=text)
        
        # Determine the path to the JSON file
        json_path = os.path.join(sg.output_path, "summarized_report.json")
        
        # Check if the file was created
        if not os.path.exists(json_path):
            raise HTTPException(status_code=500, detail="File is not existing")

        # Get text data
        meeting_topic, key_speakers, key_decisions, action_items, discussion_highlights = load_json(json_path)

        text = f"""
            Meeting Topic is: {meeting_topic},
            Key Speakers are: {', '.join(key_speakers)},
            Key Decisions are: {', '.join(key_decisions)},
            Action Items are: {', '.join(action_items)},
            Discussion Highlights are: {', '.join(discussion_highlights)}
        """
        
        # TTS
        tts = TTSService()
        audio_path = await tts.convert_text_to_speech(text)

        return {
            "status": "success", 
            "message": "Meeting summarized successfully", 
            "audio_path": audio_path
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    