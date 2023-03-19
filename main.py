import uvicorn
from app import app
from app.api.models import create_db_and_tables

@app.on_event("startup")
async def startup_event():
  create_db_and_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, log_level="info", port=8000)
