from typing import Final
from dotenv import dotenv_values
from sqlmodel import select, Session
from datetime import datetime, timedelta
from app.api.models import engine
from app.api.models.user import User
from app.api.schemas.user import SignupForm
from fastapi import APIRouter, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse, JSONResponse
from app.api.shared.utils.security import pwd_context, authenticate_user, create_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/signin")
async def signin(request: Request):
    EXPIRE_IN_MINUTES: Final = int(dotenv_values(".env").get("EXPIRE"))
    form = await request.form()

    if form.get("username") is None or form.get("password") is None:
        return JSONResponse(
            status_code=400,
            content={
                "status_code": 400,
                "message": "Username or password is required",
            },
        )

    user = authenticate_user(form["username"], form["password"])
        
    session_token = create_access_token(
        data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "admin": user.admin
        }, 
        expires_delta = timedelta(minutes=EXPIRE_IN_MINUTES)
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
        max_age=EXPIRE_IN_MINUTES * 60,
        expires=EXPIRE_IN_MINUTES * 60,
    )

    return response


@router.post("/signup", status_code=201)
async def signup(request: Request):
    form: dict = await request.form()

    validate_form = SignupForm(
        first_name = form["first_name"],
        last_name = form["last_name"],
        username = form["username"],
        email = form["email"],
        password = form["password"]
    )

    valid_user, errors = validate_form.is_valid()

    if not valid_user:
        raise HTTPException(
            status_code=400,
            detail=errors
        )
    
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
        
        new_user = User(
            first_name=form["first_name"],
            last_name=form["last_name"],
            username=form["username"],
            email=form["email"],
            hashed_password=pwd_context.hash(form["password"]),
            admin=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return RedirectResponse(
            url="/signin",
            status_code=303
        )

# change password endpoint
@router.post("/change-password")
async def change_password(request: Request):
    pass

@router.get("/signout")
async def signout():
    """Logout user"""
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response