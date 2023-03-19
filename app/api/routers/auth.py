from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(
    schemes=["sha256_crypt", "ldap_salted_md5"],
    sha256_crypt__default_rounds=91234,
    ldap_salted_md5__salt_size=16,
    deprecated="auto"
)

@router.get("/")
async def get_user():
  return {"message": "This is the auth api"}