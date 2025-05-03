from fastapi import APIRouter, HTTPException, UploadFile, File
from services import AudioTransferService, SummarizationService, AudioDiarizationService, TTSService, AnalysisService
from helpers import load_csv, load_json, format_analized_data
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
        analysis_service = AnalysisService(csv_path=csv_path)
        most_talked_speakers = analysis_service.get_most_talked_speakers(top_n=2)
        total_duration = analysis_service.get_total_duration_for_each_speaker()
        most_used_word = analysis_service.get_most_used_word()
        data = {
            "most_talked_speakers": most_talked_speakers,
            "total_duration": total_duration,
            "most_used_word": most_used_word
        }
        formatted_data = format_analized_data(data)
        print(formatted_data)
                
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
        #meeting_topic, key_speakers, key_decisions, action_items, discussion_highlights = load_json(json_path)

        #text = f"""
            #Meeting Topic is: {meeting_topic},
            #Key Speakers are: {', '.join(key_speakers)},
            #Key Decisions are: {', '.join(key_decisions)},
            #Action Items are: {', '.join(action_items)},
            #Discussion Highlights are: {', '.join(discussion_highlights)}
        #"""
        # Get text data
        meeting_topic, summary = load_json(json_path)

        text = f"""
            Meeting Topic is: {meeting_topic},
            This is some analysis of this audio: {formatted_data},
            Metting Summary is: {summary}
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
    