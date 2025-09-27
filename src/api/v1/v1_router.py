from fastapi import APIRouter
from src.api.v1.endpoints import upload_router, download_router, home_router

v1_router = APIRouter(
    prefix="/v1",
    tags=["v1"]
)
v1_router.include_router(upload_router)
v1_router.include_router(download_router)
v1_router.include_router(home_router)
