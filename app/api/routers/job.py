from io import BytesIO
from datetime import datetime
from sqlmodel import select, Session
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request, File, UploadFile
from app.api.models import engine
from app.api.models.job import Job
from app.api.models.user import User
from app.api.shared.utils.security import authorize_user

router = APIRouter()


@router.post("/delete")
async def delete_job(request: Request):
    payload = authorize_user(request)

    if not payload:
        return RedirectResponse(url="/signin")
    
    pass


@router.post("/add")
async def add_job(request: Request, file: UploadFile = File(...)):
    payload = authorize_user(request)

    if not payload:
        return RedirectResponse(url="/signin")

    form: dict = await request.form()

    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == payload.get("sub"))
        ).first()

        # read the file
        with BytesIO() as file_object:
            file_object.write(file.file.read())
            file_object.seek(0)
            print(file_object.read())
            
            # convert the file_content from binary to string
            file_content = file_object.getvalue().decode("utf-8")
            file_name = form["file"].filename
            with open(f"scripts/{file_name}", "w") as f:
                f.write(file_content)

        new_job = Job(
            name=form["job_name"],
            type=form["job_type"],
            script=f"scripts/{form['file'].filename}",
            user_id=user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(new_job)
        session.commit()
        session.refresh(new_job)

    return RedirectResponse(url="/dashboard", status_code=303)