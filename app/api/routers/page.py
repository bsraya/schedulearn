from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from app.api.models import engine
from app.api.models.user import User
from app.api.models.job import Job
from app.api.shared.utils.security import authorize_user, get_authorized_user
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = get_authorized_user(request)

    if not user:
        return templates.TemplateResponse("index.html", {"request": request})
    
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@router.get("/signin", response_class=HTMLResponse)
async def signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})


@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(authorize_user)):
    with Session(engine) as session:
        user_jobs = session.exec(
            select(Job).where(Job.user_id == user.get("id"))
        )
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "jobs": user_jobs})


@router.get("/user/{prefix:path}", response_class=HTMLResponse)
async def get_user(prefix: str, request: Request, user: dict = Depends(authorize_user)):
    if prefix == "create":
        if not user.get('admin'):
            return HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authorized")
        return templates.TemplateResponse("user/create.html", {"request": request, "user": user})
    elif prefix.isnumeric():
        with Session(engine) as session:
            db_user = session.exec(
                select(User).where(User.id == prefix)
            ).first()
            user_jobs = session.exec(
                select(Job).where(Job.user_id == prefix)
            ).all()
            if len(user_jobs) > 0:
                return templates.TemplateResponse("user/view.html", {"request": request, "user": user, "db_user": db_user, "jobs": user_jobs})
            return templates.TemplateResponse("user/view.html", {"request": request, "user": user, "db_user": db_user})
    elif prefix.endswith("/edit"):
        with Session(engine) as session:
            db_user = session.exec(
                select(User).where(User.id == prefix.split("/")[0])
            ).first()
            return templates.TemplateResponse("user/edit.html", {"request": request, "user": user, "db_user": db_user})


@router.get("/settings/{prefix:path}", response_class=HTMLResponse)
async def get_settings(prefix: str, request: Request, user: dict = Depends(authorize_user)):
    if user.get("admin") == False:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authorized")

    with Session(engine) as session:
        if prefix == "":
            return templates.TemplateResponse("settings.html", {"request": request, "user": user})
        elif prefix == "users":
            users = session.exec(select(User)).all()
            return templates.TemplateResponse("settings/users.html", {"request": request, "user": user, "users": users})
        elif prefix == "jobs":
            jobs = session.exec(select(Job)).all()
            return templates.TemplateResponse("settings/jobs.html", {"request": request, "user": user, "jobs": jobs})
        else:
            return RedirectResponse(url="/settings")