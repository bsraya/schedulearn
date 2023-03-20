from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from jose import jwt, JWTError
from starlette.status import HTTP_403_FORBIDDEN
from sqlmodel import Session, select
from app.api.models.user import User
from dotenv import dotenv_values
from app.api.models import engine
from fastapi.security.utils import get_authorization_scheme_param

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/signin", response_class=HTMLResponse)
async def signin(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    """Dashboard page"""
    cookie_authorization: str = request.cookies.get('Authorization')
    
    if not cookie_authorization:
        response = RedirectResponse(url="/signin")
        response.delete_cookie("Auhorization")
        return response
    
    cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)

    if cookie_scheme.lower() == "bearer":
        authorization = True
        scheme = cookie_scheme
        param = cookie_param
    else:
        authorization = False

    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )
    
    try:
        payload = jwt.decode(param, dotenv_values(".env").get("SECRET_KEY"), algorithms=[dotenv_values(".env").get("JWT_ALGORITHM")])
    except JWTError:
        return "User Not found."
    
    username = payload.get("sub")

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == username)
        ).first()
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
