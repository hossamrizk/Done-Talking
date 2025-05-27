from fastapi import APIRouter, Depends
from core import get_settings, Settings

home_router = APIRouter()

@home_router.get("/home")
async def home(app_settings: Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_description = app_settings.APP_DESCRIPTION
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_description": app_description,
        "app_version": app_version
    }