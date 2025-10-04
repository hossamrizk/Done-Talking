from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from src.api.v1 import v1_router
from src.api.v2 import v2_router
from src.api.security import get_api_key
from src.core import Settings, get_settings
from src.middleware.rate_limit import limiter

app = FastAPI(
    title="Done-Talking",
    description="Done-Talking is a local-first, privacy-friendly pipeline that takes long, messy audio—whether from uploaded files or video links—and delivers clean, human-readable summaries and key insights.",
    version="0.2.0",
    contact={
        "name": "Hossam Eldein Rizk",
        "email": "hossamrizk048@gmail.com"}
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "Content-Type"], 
)

app.mount("/static", StaticFiles(directory="src/templates/static"), name="static")

templates = Jinja2Templates(directory="src/templates")

app.include_router(v1_router, dependencies=[Depends(get_api_key)])
app.include_router(v2_router, dependencies=[Depends(get_api_key)])

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request, app_settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("Done-Talking.html", {
        "request": request,
        "api_token": app_settings.API_TOKEN.get_secret_value()
    })


@app.get("/upload", response_class=HTMLResponse)
async def redirect_upload(request: Request, app_settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("Done-Talking.html", {
        "request": request,
        "api_token": app_settings.API_TOKEN.get_secret_value()
    })

@app.get("/download", response_class=HTMLResponse)
async def redirect_download(request: Request, app_settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("Done-Talking.html", {
        "request": request,
        "api_token": app_settings.API_TOKEN.get_secret_value()
    })