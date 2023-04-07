from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from app.api.models import engine
from app.api.models.user import User
from app.api.models.job import Job
from app.api.shared.utils.security import authorize_user, get_authorized_user, determine_role
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_403_FORBIDDEN
from app.api.shared.utils.filters import format_date

templates = Jinja2Templates(directory="app/templates")

templates.env.filters["format_date"] = format_date
templates.env.filters["determine_role"] = determine_role

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


@router.get("/users/{prefix:path}", response_class=HTMLResponse)
async def get_user(prefix: str, request: Request, user: dict = Depends(authorize_user)):
    if prefix == "create":
        with Session(engine) as session:
            users = session.exec(select(User)).all()
            return templates.TemplateResponse("users/create.html", {"request": request, "user": user, "users": users})
    elif prefix.isnumeric():
        with Session(engine) as session:
            db_user = session.exec(
                select(User).where(User.id == prefix)
            ).first()
            user_jobs = session.exec(
                select(Job).where(Job.user_id == prefix)
            ).all()
            if len(user_jobs) > 0:
                return templates.TemplateResponse("users/view.html", {"request": request, "user": user, "db_user": db_user, "jobs": user_jobs})
            return templates.TemplateResponse("users/view.html", {"request": request, "user": user, "db_user": db_user})
    else:
        return RedirectResponse(url="/dashboard/users")


@router.get("/jobs/{prefix:path}", response_class=HTMLResponse)
async def get_jobs(prefix: str, request: Request, user: dict = Depends(authorize_user)):
    if prefix == "create":
        with Session(engine) as session:
            if user.get("admin"):
                jobs = session.exec(select(Job)).all()
            else:
                jobs = session.exec(select(Job).where(Job.user_id == user.id)).all()

            return templates.TemplateResponse("jobs/create.html", {"request": request, "user": user, "jobs": jobs})
    elif prefix.isnumeric():
        with Session(engine) as session:
            job = session.exec(
                select(Job).where(Job.id == prefix)
            ).first()
            return templates.TemplateResponse("jobs/view.html", {"request": request, "user": user, "job": job})


@router.get("/dashboard/{prefix:path}", response_class=HTMLResponse)
async def get_settings(prefix: str, request: Request, user: dict = Depends(authorize_user)):
    with Session(engine) as session:
        if prefix == "":
            with Session(engine) as session:
                if determine_role(user.get("role_mask")) in ["admin", "superadmin"]:
                    jobs = session.exec(select(Job)).all()
                else:
                    jobs = session.exec(select(Job).where(Job.user_id == user.get("id"))).all()
                users = session.exec(select(User)).all()
                return templates.TemplateResponse(
                    "dashboard.html", 
                    {
                        "request": request, 
                        "user": user, 
                        "dashboard": True,
                        "jobs": jobs,
                        "users": users,
                        "no_of_servers": 3,
                        "no_of_gpus": 12
                    }
                )
        elif prefix == "users":
            users = session.exec(select(User)).all()
            return templates.TemplateResponse("dashboard/users.html", {"request": request, "user": user, "users": users })
        elif prefix == "jobs":
            if determine_role(user.get("role_mask")) in ["admin", "superadmin"]:
                jobs = session.exec(select(Job)).all()
            else:
                jobs = session.exec(select(Job).where(Job.user_id == user.get("id"))).all()
            return templates.TemplateResponse("dashboard/jobs.html", {"request": request, "user": user, "jobs": jobs })
        elif prefix == "profile":
            return templates.TemplateResponse("dashboard/profile.html", {"request": request, "user": user })
        elif prefix == "settings":
            if determine_role(user.get("role_mask")) not in ["admin", "superadmin"]:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authorized")
            return templates.TemplateResponse("dashboard/settings.html", {"request": request, "user": user })
        else:
            return RedirectResponse(url="/dashboard")