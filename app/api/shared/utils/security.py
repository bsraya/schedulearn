from jose import jwt, JWTError
from sqlmodel import select, Session
from dotenv import dotenv_values
from app.api.models import engine
from app.api.models.user import User
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.security.utils import get_authorization_scheme_param
from typing import Final

pwd_context = CryptContext(
    schemes=["sha256_crypt", "ldap_salted_md5"],
    sha256_crypt__default_rounds=91234,
    ldap_salted_md5__salt_size=16,
    deprecated="auto"
)

ROLE_MASKS: Final = {
    bin(0b001): "user",
    bin(0b011): "admin",
    bin(0b101): "superadmin"
}

def get_authorized_user(request: Request) -> dict | None:
    cookie_authorization: str = request.cookies.get('Authorization')

    if not cookie_authorization:
        return None

    cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)

    if cookie_scheme.lower() == "bearer":
        authorization = True
        scheme = cookie_scheme
        param = cookie_param
    else:
        authorization = False

    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )
    
    return jwt.decode(param, dotenv_values(".env").get("SECRET_KEY"), algorithms=[dotenv_values(".env").get("JWT_ALGORITHM")])


def authenticate_user(username: str, password: str) -> User | bool:
    with Session(engine) as session:
        user = session.exec(
            select(User)
            .where(
                User.username == username
            )
        ).first()

        if not user or not pwd_context.verify(password, user.hashed_password):
            return JSONResponse(
                status_code=400,
                content={
                    "status_code": 400,
                    "message": "Incorrect username or password",
                },
            )
        
        return user


def authorize_user(request: Request):
    cookie_authorization: str = request.cookies.get('Authorization')
    
    if not cookie_authorization:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)

    if cookie_scheme.lower() == "bearer":
        authorization = True
        scheme = cookie_scheme
        param = cookie_param
    else:
        authorization = False

    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            param, 
            dotenv_values(".env").get("SECRET_KEY"), 
            algorithms=[dotenv_values(".env").get("JWT_ALGORITHM")]
        )
    except JWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )
    
    return payload


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expires = int(dotenv_values(".env").get("EXPIRE"))
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=expires)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        dotenv_values(".env").get("SECRET_KEY"), 
        algorithm=dotenv_values(".env").get("JWT_ALGORITHM")
    )

    return encoded_jwt

def determine_role(role_mask: int) -> str:
    return ROLE_MASKS.get(bin(role_mask), "user")