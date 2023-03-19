from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_user():
  return {"message": "This is the auth api"}