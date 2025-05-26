from fastapi import FastAPI, Depends
from api import v1_router, get_api_key

app  = FastAPI(
    title="Done-Talking",
    description="Done-Talking is a local-first, privacy-friendly pipeline that takes long, messy audio—whether from uploaded files or video links—and delivers clean, human-readable summaries and key insights.",
    version="0.2.0",
    contact={
        "name": "Hossam Eldein Rizk",
        "email": "hossamrizk048@gmail.com"}
    
)
app.include_router(v1_router, dependencies=[Depends(get_api_key)])