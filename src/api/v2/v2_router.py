from fastapi import APIRouter
from src.api.v2.endpoints import accept_audio_router

v2_router = APIRouter(
    prefix="/v2",
    tags=["v2"]
)
v2_router.include_router(accept_audio_router)

