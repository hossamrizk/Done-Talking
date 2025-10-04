from fastapi import APIRouter, Depends
from src.core import get_settings, Settings
from src.middleware.rate_limit import limiter, RateLimits
home_router = APIRouter()

@home_router.get("/home")
@limiter.limit(RateLimits.HOME)
async def home(app_settings: Settings = Depends(get_settings)):
    app_name = app_settings.APP_NAME
    app_description = app_settings.APP_DESCRIPTION
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_description": app_description,
        "app_version": app_version
    }