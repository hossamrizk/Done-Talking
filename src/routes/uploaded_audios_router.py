from fastapi import APIRouter, HTTPException
from services import AudioTransfer, AudioSummarization, AudioDiarization, SummarizationAgent
from fastapi import UploadFile, File
from helpers import load_csv
import os

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

        # Generate summary
        #audio_summaryization = AudioSummarization()
        #summary = audio_summaryization.summarization(text_data)
        
        # Save report
        #report_path = audio_summaryization.generate_report(summary)
        
        return result.json_dict
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")