from jose import jwt
from dotenv import dotenv_values
from sqlmodel import select, Session
from datetime import datetime, timedelta
from app.api.models import engine
from app.api.models.user import User
from app.api.shared import pwd_context
from app.api.schemas.user import UserSignup
from fastapi import APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, JSONResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(username: str):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == username)
        ).first()
        return user


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expires = int(dotenv_values(".env").get("EXPIRE"))
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=expires)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, dotenv_values(".env").get("SECRET_KEY"), algorithm=dotenv_values(".env").get("JWT_ALGORITHM"))
    return encoded_jwt


@router.post("/signin")
async def signin(request: Request):
    expires = int(dotenv_values(".env").get("EXPIRE"))
    form: dict = await request.form()
    user = authenticate_user(form['username'], form['password'])

    if not user:
        return JSONResponse(
            status_code=400,
            content={
                "status_code": 400,
                "message": "Incorrect username or password",
            },
        )
        
    session_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=expires)
    )

    response = RedirectResponse(
        url="/dashboard",
        status_code=303
    )

    response.set_cookie(
        "Authorization", 
        f"Bearer {session_token}",
        domain="localhost",
        httponly=True,
        max_age=3600,
        expires=3600,
    )

    return response


@router.post("/signup", status_code=201)
async def signup(request: Request):
    form: dict = await request.form()
    
    with Session(engine) as session:
        db_user = session.exec(
            select(User).where(User.email == form["email"])
        ).first()

        if db_user:
            return JSONResponse(
                status_code=400,
                content={
                    "status_code": 400,
                    "message": "User with this email already exists!",
                },
            )
        
        validate_user = UserSignup(
            first_name = form["first_name"],
            last_name = form["last_name"],
            username = form["username"],
            email = form["email"],
            password = form["password"]
        )

        valid_user, errors = validate_user.is_valid()

        if not valid_user:
            return JSONResponse(
                status_code=400,
                content={
                    "status_code": 400,
                    "message": f"Invalid user information. Errors are {errors}",
                }
            )

        new_user = User(
            first_name=form["first_name"],
            last_name=form["last_name"],
            username=form["username"],
            email=form["email"],
            hashed_password=pwd_context.hash(form["password"]),
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        response = RedirectResponse(
            url="/signin",
            status_code=303
        )

        return response
    

@router.get("/signout")
async def signout():
    """Logout user"""
    response = RedirectResponse(url="/signin")
    response.delete_cookie("Authorization")
    return response