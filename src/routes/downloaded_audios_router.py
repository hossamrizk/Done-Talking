from fastapi import APIRouter, HTTPException
from services import AudioTransfer, SummarizationAgent, AudioDiarization, TTS
from models import DownloadRequest
from helpers import load_csv, load_json
import os
download_audio_router = APIRouter()

@download_audio_router.post("/download_audio")
async def download_audio(request: DownloadRequest):
    try:
        video_url = request.video_url
        at = AudioTransfer()
        downloaded_file_path = at.download_audio(video_url=video_url)
        
        # Running Diralization
        ad = AudioDiarization()
        
        _, _, csv_path = ad.diarize(audio_file=downloaded_file_path)

        # Load csv file
        speakers, text = load_csv(csv_path=csv_path)

        audio_summaryization = SummarizationAgent()
        summary = audio_summaryization.summarization(text)

        # Summarization
        sg = SummarizationAgent()
        result = sg.run_summarization_crew(speakers=speakers, text=text)
        
        # Get text data
        json_path = os.path.join(sg.output_path, "summarized_report.json")
        
        # Check if the file was created
        if not os.path.exists(json_path):
            raise HTTPException(status_code=500, detail="File is not existing")

        # Get text data
        meeting_topic, key_speakers, key_decisions, action_items, discussion_highlights = load_json(json_path)
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

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")

