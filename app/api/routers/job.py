import os
from io import BytesIO
from datetime import datetime
from sqlmodel import Session
from fastapi import APIRouter, Request, File, UploadFile, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse
from app.api.models import engine
from app.api.models.job import Job
from app.api.shared.utils.security import authorize_user

router = APIRouter()

def run_job(job_id: int):
    with Session(engine) as session:
        job: Job = session.get(Job, job_id)
        job.status = "running"
        job.started_at = datetime.now()
        session.commit()

        # run the job
        with open(job.script, "r") as f:
            script = f.read()
            print(script)
            exec(script)

        job.status = "completed"
        job.completed_at = datetime.now()
        session.commit()


@router.post("/delete/{job_id}")
async def delete_job(request: Request, job_id: int = None, user: dict = Depends(authorize_user)):
    pass


@router.post("/add")
async def add_job(request: Request, file: UploadFile = File(...), user: dict = Depends(authorize_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    form: dict = await request.form()

    with Session(engine) as session:
        # read the file
        with BytesIO() as file_object:
            file_object.write(file.file.read())
            file_object.seek(0)
            print(file_object.read())
            
            # convert the file_content from binary to string
            file_content = file_object.getvalue().decode("utf-8")
            file_name = form["file"].filename
            
            user_folder_path = f"scripts/{user.get('name')}"
            # create the user folder if it doesn't exist
            if not os.path.exists(user_folder_path):
                os.makedirs(user_folder_path)

            with open(f"{user_folder_path}/{file_name}", "w") as f:
                f.write(file_content)

        new_job = Job(
            name=form["job_name"],
            type=form["job_type"],
            script=f"{user_folder_path}/{form['file'].filename}",
            user_id=user.get("id"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(new_job)
        session.commit()
        session.refresh(new_job)

        background_tasks.add_task(run_job, new_job.id)

    return RedirectResponse(url="/dashboard", status_code=303)