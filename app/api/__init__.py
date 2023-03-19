from fastapi import APIRouter

from app.api.routers import router as api_router

api_router = APIRouter()

api_router.include_router(
    api_router,
    prefix="/users", 
    tags=["users"]
)