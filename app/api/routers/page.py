from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

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
async def dashboard(request: Request):
  return templates.TemplateResponse("dashboard.html", {"request": request})