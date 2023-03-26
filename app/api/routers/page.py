from sqlmodel import Session, select
from app.api.models import engine
from app.api.models.user import User
from app.api.models.job import Job
from app.api.shared.utils.security import authorize_user, get_authorized_user
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends
from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.security.utils import get_authorization_scheme_param
from dotenv import dotenv_values
from jose import jwt, JWTError

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    payload = get_authorized_user(request)

    if not payload:
        return templates.TemplateResponse("index.html", {"request": request})
    
    with Session(engine) as session:
        current_user = session.exec(
            select(User).where(User.username == payload.get("sub"))
        ).first()
        return templates.TemplateResponse("index.html", {"request": request, "user": current_user})


@router.get("/signin", response_class=HTMLResponse)
async def signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, payload: dict = Depends(authorize_user)):
    username = payload.get("sub")

    with Session(engine) as session:
        current_user = session.exec(
            select(User).where(User.username == username)
        ).first()

        user_jobs = session.exec(
            select(Job).where(Job.user_id == current_user.id)
        )
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user, "jobs": user_jobs})


@router.get("/user/{prefix:path}", response_class=HTMLResponse)
async def get_user(prefix: str, request: Request):
    if prefix == "create":
        return templates.TemplateResponse("user/create.html", {"request": request})

@router.get("/settings/{prefix:path}", response_class=HTMLResponse)
async def get_settings(prefix: str, request: Request):
    payload = authorize_user(request)
    
    if payload == "Invalid token":
        return RedirectResponse(url="/signin", status_code=302)
    
    is_admin = payload.get("admin")

    if is_admin == False:
        return RedirectResponse(url="/dashboard")

    with Session(engine) as session:
        current_user = session.exec(
            select(User).where(User.username == payload.get("sub"))
        ).first()
        if prefix == "":
            return templates.TemplateResponse("settings.html", {"request": request, "user": current_user})
        elif prefix == "users":
            users = session.exec(select(User)).all()
            return templates.TemplateResponse("settings/users.html", {"request": request, "user": current_user, "users": users})
        elif prefix == "jobs":
            jobs = session.exec(select(Job)).all()
            return templates.TemplateResponse("settings/jobs.html", {"request": request, "user": current_user, "jobs": jobs})
        else:
            return RedirectResponse(url="/settings")