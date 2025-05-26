from fastapi import FastAPI
from routes import home_router, download_router, upload_router

app  = FastAPI()
app.include_router(home_router)
app.include_router(upload_router)
app.include_router(download_router)

