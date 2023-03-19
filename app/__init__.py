from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routers import router as api_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
app.include_router(api_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
static_dir = os.path.abspath(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add CORS middleware to the application
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)