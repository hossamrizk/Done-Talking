# 🎤 Done-Talking

> “Too much talk? I’ll handle it.”

**Done-Talking** is a local-first, privacy-friendly pipeline that takes long, messy audio—whether from uploaded files or video links—and delivers clean, human-readable summaries and key insights.

---

## 🧠 What It Does

- Accepts a **video URL** or **uploaded audio**.
- If video: downloads and extracts audio.
- Performs **speaker diarization** with `pyannote.audio` to separate voices.
- Transcribes using **OpenAI Whisper** (locally).
- Summarizes the transcript + extracts key points using **Ollama local models**.
- All processing runs **locally**, except for the summary model hosted on **Colab GPU**.
- Outputs a concise **.txt file** with the final summary.

---

## 🚀 Features

- ✅ Video URL input (e.g., YouTube)
- ✅ Local audio file support (`.mp3`, `.wav`, etc.)
- ✅ Multi-speaker diarization via `pyannote.audio`
- ✅ Whisper-based transcription
- ✅ Summarization using Ollama-hosted LLMs (e.g., Mistral, LLaMA 3)
- ✅ Key points extraction
- ✅ Offline-first, with remote LLM support via Colab
- ✅ Final output saved as `.txt`

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
| Summarization       | `ollama` (hosted on Colab) |
| API Server          | `Flask`                  |
| File I/O            | `os`, `tempfile`, `shutil`, `pathlib` |

---

## 📁 Folder Structure

```bash
done-talking/
│
├── src/
│   ├── assets/
│   │   ├── generated_reports/
│   │   ├── downloaded_audios/
│   │   └── uploaded_audios/
│   │
│   ├── helpers/
│   │   └── file_helpers.py
│   │
│   ├── models/
│   │   └── ollama_model.py
│   │
│   ├── routes/
│   │   └── api_routes.py
│   │
│   ├── services/
│   │   ├── download_video.py
│   │   ├── diarize.py
│   │   ├── transcribe.py
│   │   └── summarize.py
│   │
│   ├── .env
│   ├── requirements.txt
│   └── main.py
│
├── LICENSE
├── README.md
└── colab_server.ipynb
```

## 🧪 How to Run

1. Clone the repo

```bash
git clone https://github.com/your-username/done-talking.git
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

This project is licensed under the MIT License. See the `LICENSE` file for details.
