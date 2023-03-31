from fastapi import APIRouter
from app.api.models import engine
from app.api.models.user import User
from sqlmodel import select, Session

router = APIRouter()