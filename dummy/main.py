import config
import uvicorn
import logging
import database as db

from fastapi import FastAPI
from pydantic import BaseModel
from sqlmodel import Session, select, col
from logging.config import dictConfig
from fastapi.middleware.cors import CORSMiddleware

dictConfig(config.LOGGING)
logger = logging.getLogger("schedulearn")
app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:3000",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Job(BaseModel):
    name: str
    type: str
    container_image: str
    command: str
    required_gpus: int


@app.on_event("startup")
def on_startup():
    db.initialize()


@app.post("/jobs", response_model=Job, status_code=201)
async def add_job(job: Job):
    # print out the job
    logger.info(f"Adding job: {job.dict()}")
    "Add a job to the scheduler"
    with Session(db.engine) as session:
        job = db.Job(**job.dict())
        session.add(job)
        session.commit()
        session.refresh(job)


@app.get("/jobs")
async def get_jobs():
    "Get all jobs"
    with Session(db.engine) as session:
        jobs = session.exec(
            select(db.Job)
            .order_by(col(db.Job.created_at).desc())
        ).fetchall()
        return jobs


@app.get("/jobs/{id}")
async def get_job(id: int):
    "Get status of a job"
    with Session(db.engine) as session:
        job = session.exec(
            select(db.Job)
            .where(col(db.Job.id) == id)
        ).one()
        return job


@app.delete("/jobs/{id}", status_code=204)
async def kill_job(id: int):
    """
    If a model is on progress, delete the pod immediately, as well as the
    metadata of a model in the database.
    """
    with Session(db.engine) as session:
        job = session.exec(
            select(db.Job)
            .where(col(db.Job.id) == id)
        ).one()

        # kill the container running the job
        # ....

        # delete the job from the database
        session.delete(job)
        session.commit()
        return job


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=int(config.PORT))
