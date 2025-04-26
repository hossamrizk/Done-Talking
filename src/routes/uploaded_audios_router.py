from fastapi import APIRouter, HTTPException
from services import AudioTransfer, AudioDiarization, SummarizationAgent, TTS
from fastapi import UploadFile, File
from helpers import load_csv, load_json

upload_audio_router = APIRouter()
@upload_audio_router.post("/upload_audio")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        # Upload and process audio
        at = AudioTransfer()
        result = at.upload_audio(file=audio)
        
        if result["status"] == "success" and "file_path" in result:
            uploaded_file_path = result["file_path"]
        else:
            raise HTTPException(status_code=400, detail="Failed to upload audio")

        # Run diarization
        ad = AudioDiarization()
        _, _, csv_path = ad.diarize(audio_file=uploaded_file_path)
        
        # Load csv file
        speakers, text = load_csv(csv_path=csv_path)

        # Summarization
        sg = SummarizationAgent()
        result = sg.run_summarization_crew(speakers=speakers, text=text)

        # Get text data
        meeting_topic, key_speakers, key_decisions, action_items, discussion_highlights = load_json(json_path = "/home/aitech/ssd/Done-Talking/src/assets/generated_reports/summarized_report.json") 

        text = f"""
            Metting Topic is: {meeting_topic},
            key Speakers are: {key_speakers},
            key Decisions are: {key_decisions},
            Action Items are: {action_items},
            Discussion Highlights are: {discussion_highlights}
        """
        
        # TTS
        tts = TTS()
        await tts.convert_text_to_speech(text)

        return {"A summarized audio saved successfully"}
        #return result.json_dict
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")