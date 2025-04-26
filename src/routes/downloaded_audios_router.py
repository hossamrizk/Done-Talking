from fastapi import APIRouter, HTTPException
from services import AudioTransfer, AudioSummarization, AudioDiarization
from models import DownloadRequest

download_audio_router = APIRouter()

@download_audio_router.post("/download_audio")
async def download_audio(request: DownloadRequest):
    try:
        video_url = request.video_url
        at = AudioTransfer()
        downloaded_file_path = at.download_audio(video_url=video_url)
        
        # Running Diralization
        ad = AudioDiarization()
        
        diarization_result, text_data = ad.diarize(audio_file=downloaded_file_path)

        audio_summaryization = AudioSummarization()
        summary = audio_summaryization.summarization(text_data)

        # Save report
        report_path = audio_summaryization.generate_report(summary)
        
        return {
            "status": "success",
            "message": "Audio processed successfully",
            "report_path": report_path
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")

