from fastapi import APIRouter, Request, File, UploadFile
from io import BytesIO

router = APIRouter()

@router.post("/add")
async def add_job(request: Request, file: UploadFile = File(...)):
    form: dict = await request.form()
    print(form["job_name"])
    print(form["job_type"])

    # read the file
    with BytesIO() as file_object:
        file_object.write(file.file.read())
        file_object.seek(0)
        print(file_object.read())
    return {"message": "Job added successfully"}