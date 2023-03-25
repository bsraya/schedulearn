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
        
        # convert the file_content from binary to string
        file_content = file_object.getvalue().decode("utf-8")
        file_name = form["file"].filename
        with open(f"scripts/{file_name}", "w") as f:
            f.write(file_content)

    return {"message": "Job added successfully"}