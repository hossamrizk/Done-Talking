from fastapi import FastAPI
from routes.home import home_router
from routes.downloaded_audios_router import download_audio_router
from routes.uploaded_audios_router import upload_audio_router


app  = FastAPI()
app.include_router(home_router)
app.include_router(download_audio_router)
app.include_router(upload_audio_router)