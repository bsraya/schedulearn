from fastapi import APIRouter

router = APIRouter()

@router.get("/create")
async def get_user():
  return {"message": "This is the user api"}

@router.get("/{username}")
async def get_user(username: str):
  return {"message": f"This is the user {username}"}