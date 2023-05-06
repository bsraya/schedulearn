import uvicorn
from app import app
from app.api.db import create_db_and_tables, save_system_settings
from dotenv import dotenv_values

@app.on_event("startup")
async def startup_event():
  create_db_and_tables() 
  save_system_settings()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, log_level="info", port=int(dotenv_values(".env").get("PORT")))
