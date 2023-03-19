from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import router as api_router
from app.api.models import create_db_and_tables
import uvicorn
app = FastAPI()

# Add the API router to the application
app.include_router(api_router)

# Add CORS middleware to the application
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
  create_db_and_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, log_level="info", port=8000)
