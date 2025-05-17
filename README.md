# 🎤 Done-Talking

> “Too much talk? I’ll handle it.”

**Done-Talking** is a local-first, privacy-friendly pipeline that takes long, messy audio—whether from uploaded files or video links—and delivers clean, human-readable summaries and key insights.

---

## 🧠 What It Does

- Accepts a **video URL** or **uploaded audio**.
- If video: downloads and extracts audio.
- Performs **speaker diarization** with `pyannote.audio` to separate voices.
- Transcribes using **OpenAI Whisper** (locally).
- Summarizes the transcript + extracts key points using **Crewai and Ollama local models**.
- All processing runs **locally**.
- Outputs a concise **.json file** with the final summary.
- Convert text summary into audio using **edge_tts**.

---

## 🚀 Features

- ✅ Video URL input (e.g., YouTube)
- ✅ Local audio file support (`.mp3`, `.wav`, etc.)
- ✅ Multi-speaker diarization via `pyannote.audio`
- ✅ Whisper-based transcription
- ✅ Summarization using Crewai and Ollama LLMs.
- ✅ Key points extraction
- ✅ Final output saved as `.json`
- ✅ Convert summary into audio using `edge_tts`

---

## 🔗 API Endpoints

The project includes three REST API endpoints:

| Endpoint          | Method | Description |
|-------------------|--------|-------------|
| `/`               | GET    | Returns basic app info |
| `/download_audio` | POST   | Accepts a JSON body: `{ "video_url": "<url>" }` and downloads + processes audio |
| `/upload_audio`   | POST   | Accepts a `multipart/form-data` audio file upload (from user’s PC) |

---

## 🔧 Tech Stack

| Component           | Tool                     |
|--------------------|--------------------------|
| Audio/Video Handling | `moviepy`, `ffmpeg`     |
| Diarization         | `pyannote.audio`         |
| Transcription       | `whisper`                |
| Summarization       | `Crewai with ollama` (Locally) |
| Endpoints           | `FastAPI`                  |
| File I/O            | `os`, `tempfile`, `shutil`|

---

## 📁 Folder Structure

```bash
done-talking/
│
├── docker/
│   ├── docker-compose.yaml
│   └── Dockerfile
│
├── src/
│   ├── assets/
│   │   ├── downloaded_audios/
│   │   ├── diarization_output/
│   │   ├── generated_reports/
│   │   ├── logs/
│   │   └── uploaded_audios/
│   │
│   ├── helpers/
│   │   ├── config.py
│   │   ├── load_csv.py
│   │   ├── load_json.py
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── DownloadRequest.py
│   │   ├── MeetingSummary.py
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   ├── downloaded_audios_router.py
│   │   ├── home.py
│   │   ├── uploaded_audios_router.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── BaseService.py
│   │   └── __init__.py
│   │
│   │   ├── analysis/
│   │   │   ├── AnalysisService.py
│   │   │   ├── DataLoader.py
│   │   │   ├── SpeakerAnalyzer.py
│   │   │   ├── TextAnalyzer.py
│   │   │   ├── __init__.py
│   │   │   └── stopwords/
│   │   │       ├── AbstractStopWords.py
│   │   │       ├── ArabicStopWords.py
│   │   │       ├── EnglishStopWords.py
│   │   │       └── __init__.py
│   │
│   │   ├── diarization/
│   │   │   ├── AudioDiarization.py
│   │   │   ├── CsvHandler.py
│   │   │   └── __init__.py
│   │
│   │   ├── file_transfer/
│   │   │   ├── AbstractAudioHandler.py
│   │   │   ├── DownloadAudio.py
│   │   │   ├── UploadAudio.py
│   │   │   └── __init__.py
│   │
│   │   ├── formatters/
│   │   │   ├── AbstractFormatter.py
│   │   │   ├── ArabicFormatter.py
│   │   │   ├── EnglishFormatter.py
│   │   │   └── __init__.py
│   │
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── prompts/
│   │   │   │   ├── BasePrompt.py
│   │   │   │   ├── ArabicPrompt.py
│   │   │   │   ├── EnglishPrompt.py
│   │   │   │   └── __init__.py
│   │   │   └── providers/
│   │   │       ├── BaseLLMProvider.py
│   │   │       ├── GoogleProvider.py
│   │   │       ├── OllamaProvider.py
│   │   │       └── __init__.py
│   │
│   │   ├── summarization/
│   │   │   ├── AbstractSummary.py
│   │   │   ├── ArabicSummary.py
│   │   │   ├── EnglishSummary.py
│   │   │   ├── JSONOutputHandler.py
│   │   │   └── __init__.py
│   │
│   │   ├── text_to_speech/
│   │   │   ├── AbstractConverter.py
│   │   │   ├── ArabicConverter.py
│   │   │   ├── EnglishConverter.py
│   │   │   └── __init__.py
│   │
│   │   └── transcription/
│   │       ├── AudioTranscription.py
│   │       └── __init__.py
│
│   ├── .env
│   ├── .env.example
│   ├── main.py
│   └── requirements.txt
│
├── LICENSE
└── README.md
```

## 🧪 How to Run

1. Clone the repo

```bash
git clone https://github.com/hossamrizk/done-talking.git
cd done-talking
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Run

```bash
uvicorn main:app --port 8000 --host 0.0.0.0
```

## 💡 Example Use Cases

Meeting summarizer

Podcast note-taker

Lecture distiller

Multi-speaker content analyzer

## 📜 License

This project is proprietary and all rights are reserved by `Hossam Eldein Rizk`. Unauthorized copying or distribution is prohibited. See the LICENSE file for full terms.