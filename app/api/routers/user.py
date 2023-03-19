from fastapi import APIRouter

router = APIRouter()

@router.get("/{username}")
async def get_user(username: str):
  return {"message": f"This is the user {username}"}