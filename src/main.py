from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api import v1_router, get_api_key

app = FastAPI(
    title="Done-Talking",
    description="Done-Talking is a local-first, privacy-friendly pipeline that takes long, messy audio—whether from uploaded files or video links—and delivers clean, human-readable summaries and key insights.",
    version="0.2.0",
    contact={
        "name": "Hossam Eldein Rizk",
        "email": "hossamrizk048@gmail.com"}
)

# Mount static files
app.mount("/static", StaticFiles(directory="/home/hussam/Done-Talking/src/templates/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include your API router with API key dependency
app.include_router(v1_router, dependencies=[Depends(get_api_key)])

# Single page application route
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("podcast-demo.html", {"request": request})

# Redirect old routes to main page
@app.get("/upload", response_class=HTMLResponse)
async def redirect_upload(request: Request):
    return templates.TemplateResponse("podcast-demo.html", {"request": request})

@app.get("/download", response_class=HTMLResponse)
async def redirect_download(request: Request):
    return templates.TemplateResponse("podcast-demo.html", {"request": request})