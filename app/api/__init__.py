from fastapi import APIRouter
from app.api.routers.page import router as page_router
from app.api.routers.auth import router as auth_router
from app.api.routers.user import router as user_router

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth", 
    tags=["auth"]
)

api_router.include_router(
    user_router,
    prefix="/user",
    tags=["user"]
)