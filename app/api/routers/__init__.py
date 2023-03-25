from fastapi import APIRouter
from .user import router as user_router
from .page import router as page_router
from .auth import router as auth_router
from .job import router as job_router

router = APIRouter()

router.include_router(page_router, tags=["page"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(job_router, prefix="/job", tags=["job"])