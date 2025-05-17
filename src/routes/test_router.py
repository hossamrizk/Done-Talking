from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from services.file_transfer import UploadAudio
from services.diarization import AudioDiarization
from services.analysis import AnalysisService
from services.summarization import EnglishSummary, ArabicSummary
from services.text_to_speech import EnglishConverter, ArabicConverter
from services.formatters import EnglishFormatter, ArabicFormatter
from langdetect import detect
from helpers import load_csv, load_json, format_analized_data
import os


at = UploadAudio()
ad = AudioDiarization()

es = EnglishSummary()
ef = EnglishFormatter()
es_tts = EnglishConverter()

ars = ArabicSummary()
arf = ArabicFormatter()
ar_tts = ArabicConverter()

test_router = APIRouter()
@test_router.post("/test")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        # Upload and process audio
        result = at.handle(file=audio)
        
        if result["status"] == "success" and "file_path" in result:
            uploaded_file_path = result["file_path"]
        else:
            raise HTTPException(status_code=400, detail="Failed to upload audio")

        # Run diarization
        _, _, csv_path = ad.diarize(audio_file=uploaded_file_path)
        analysis_service = AnalysisService(csv_path=csv_path)
        most_talked_speakers = analysis_service.get_most_talked_speakers(top_n=2)
        total_duration = analysis_service.get_total_duration_for_each_speaker()
        most_used_word = analysis_service.get_most_used_word()
        total_speakers = analysis_service.get_total_number_of_speakers()
        language_type = analysis_service.get_language_type()

        if language_type == 'en':
            data = {
                "most_talked_speakers": most_talked_speakers,
                "total_duration": total_duration,
                "most_used_word": most_used_word
            }
            formatted_data = ef.format_summary(data=data)
            print(formatted_data)
                    
            # Load csv file
            _, text = load_csv(csv_path=csv_path)
        
            json_path = es.create_summary(text=text)

            # Check if the file was created
            if not os.path.exists(json_path):
                raise HTTPException(status_code=500, detail="File is not existing")

            # Get text data
            meeting_topic, summary = load_json(json_path)

            text = f"""
                Meeting Topic is: {meeting_topic},
                This is some analysis of this audio: The total number of speakers is {total_speakers}, {formatted_data},
                Metting Summary is: {summary}
            """
            
            # TTS
            audio_path = await es_tts.convert(text)
            
            if not os.path.exists(audio_path):
                raise HTTPException(status_code=500, detail="Audio file not found")

            return FileResponse(
                audio_path,
                media_type="audio/mpeg"
            )

        if language_type == 'ar':
            # Clean most used words
            most_used_word = arf.clean_field(most_used_word)
            most_used_word = arf.replace_speaker_tags(most_used_word)
            data = {
                "أكثر المتحدثيين هم": most_talked_speakers,
                "اجمالى وقت التحدث": total_duration,
                "أكثر الكلمات استخدامآ": most_used_word
            }

            # Format Arabic output and clean tags
            formatted_data = arf.format_summary(data)
            formatted_data = arf.replace_speaker_tags(formatted_data)

            # Langchain summary
            speakers, text = load_csv(csv_path=csv_path)
            text = arf.replace_speaker_tags(text)
            json_path = ars.create_summary(text=text)
            meeting_topic, summary = load_json(json_path)
            text = f"""
                عنوان الاجتماع: {meeting_topic},
                هذه بعض الاحصائيات بخصوص الاجتماع: العدد الكلي للمتحدثين هو {total_speakers}, {formatted_data},
                ملخص الاجتماع: {summary}
            """
            # TTS
            audio_path = await ar_tts.convert(text)
            
            if not os.path.exists(audio_path):
                raise HTTPException(status_code=500, detail="Audio file not found")

            return FileResponse(
                audio_path,
                media_type="audio/mpeg"
            )            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
