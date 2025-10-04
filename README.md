# 🎤 Done-Talking

> "Too much talk? I'll handle it."

**Done-Talking** is a local-first, privacy-friendly pipeline that takes long, messy audio—whether from uploaded files or video links—and delivers clean, human-readable summaries and key insights.

**Current Version:** 0.2.0

---

## 🧠 What It Does

- Accepts a **video URL** or **uploaded audio**.
- **Chrome Extension** for recording meetings directly from Zoom, Teams, Webex, and Google Meet - automatically starts the processing pipeline when meetings end.
- If video: downloads and extracts audio.
- Performs **speaker diarization** with `pyannote.audio` to separate voices.
- Transcribes using **OpenAI Whisper** (locally).
- Summarizes the transcript + extracts key points using **Ollama local models**.
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

The project includes versioned REST API endpoints:

### V1 Endpoints
| Endpoint              | Method | Description |
|----------------------|--------|-------------|
| `/`                  | GET    | Web interface for audio processing |
| `/v1/download_audio` | POST   | Accepts a JSON body: `{ "video_url": "<url>" }` and downloads + processes audio |
| `/v1/upload_audio`   | POST   | Accepts a `multipart/form-data` audio file upload (from user's PC) |

### V2 Endpoints
| Endpoint              | Method | Description |
|----------------------|--------|-------------|
| `/v2/receive_audio`   | POST   | Enhanced audio processing with advanced features |

**Authentication:** All API endpoints require an API token for security.

---

## 🔧 Tech Stack

| Component           | Tool                     |
|--------------------|--------------------------|
| **Backend Framework** | `FastAPI` with `uvicorn` |
| **Audio/Video Handling** | `moviepy`, `ffmpeg`, `yt-dlp` |
| **Diarization**     | `pyannote.audio`         |
| **Transcription**   | `OpenAI Whisper`         |
| **LLM Integration** | `Langchain` with `Ollama`, `Google Gemini`, `OpenAI` |
| **Text-to-Speech**  | `edge-tts`              |
| **Database**        | `PostgreSQL` with `Alembic` migrations |
| **Security**        | API token authentication, rate limiting |
| **Language Processing** | `NLTK`, `langdetect`, `Arabic-Stopwords` |
| **Data Processing** | `pandas`, `pydub`        |
| **Containerization** | `Docker` with CUDA support |

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

### Prerequisites
- Python 3.11+
- PostgreSQL database
- NVIDIA GPU (optional, for CUDA acceleration)
- FFmpeg
- Ollama (for local LLM inference)
- **Required Ollama Model:** `mistral:7b-instruct-q4_0`

### Method 1: Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/hossamrizk/done-talking.git
cd done-talking
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration values
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install and set up Ollama:**
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the required model
ollama pull mistral:7b-instruct-q4_0
```

5. **Set up database:**
```bash
# Run PostgreSQL and update connection details in .env
alembic upgrade head
```

6. **Run the application:**
```bash
uvicorn src.main:app --port 8000 --host 0.0.0.0
```

### Method 2: Docker (Recommended)

1. **Clone and configure:**
```bash
git clone https://github.com/hossamrizk/done-talking.git
cd done-talking
cp .env.example .env
# Edit .env with your configuration
```

2. **Run with Docker Compose:**
```bash
cd docker
docker-compose up -d
```

3. **Pull the required Ollama model:**
```bash
# Wait for Ollama service to be ready, then pull the model
docker-compose exec ollama ollama pull mistral:7b-instruct-q4_0
```

This will start:
- PostgreSQL database
- Ollama service for local LLM inference
- Done-Talking application with CUDA support

**Note:** The Ollama model download is ~4GB and may take several minutes depending on your internet connection.

### Method 3: Browser Extension

The project includes a browser extension for recording meeting audio:

1. Load the `browser-extension` directory as an unpacked extension in Chrome
2. Extension works with Google Meet, Zoom, Microsoft Teams, and Webex
3. Configure the extension to connect to your local Done-Talking instance

## 🔧 Configuration

### Required Environment Variables

```bash
# Application
APP_NAME=Done-Talking
APP_VERSION=0.2.0
API_TOKEN=your_secure_api_token

# Database
POSTGRES_USERNAME=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE_NAME=done_talking

# AI Services 
HF_TOKEN=your_huggingface_token
GOOGLE_API_KEY=your_google_api_key
```

## 💡 Example Use Cases

- **Meeting Summarizer:** Record and analyze business meetings, generating action items and key decisions
- **Podcast Note-Taker:** Extract main topics and insights from long-form audio content
- **Lecture Distiller:** Convert educational content into digestible summaries and study notes
- **Interview Analyzer:** Process interviews with speaker identification and topic extraction
- **Multi-speaker Content Analyzer:** Analyze group discussions with per-speaker insights

## 🌐 Supported Platforms

### Browser Extension Support
- ✅ Google Meet
- ✅ Zoom
- ✅ Microsoft Teams
- ✅ Webex

### Audio Format Support
- ✅ MP3, WAV, FLAC, M4A
- ✅ YouTube videos (automatic audio extraction)
- ✅ Most common video formats via yt-dlp

### Language Support
- ✅ English (full support using Ollama local models)
- ✅ Arabic (full support with specialized handling via Google Gemini due to limited resources for serving quality Arabic models locally)

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

Copyright 2025 Hossam Eldein Rizk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.