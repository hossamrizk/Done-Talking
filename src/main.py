from fastapi import FastAPI
from routes import home_router
from routes import upload_audio_router

app  = FastAPI()
app.include_router(home_router)
app.include_router(upload_audio_router)
