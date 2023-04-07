from datetime import datetime
from sqlmodel import select, Session
from app.api.models import engine
from app.api.models.user import User
from app.api.schemas.user import SignupForm
from app.api.shared.utils.security import pwd_context
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from app.api.shared.utils.security import authorize_user, determine_role

router = APIRouter()

@router.post("/create_user", response_class=HTMLResponse)
async def create_user(request: Request, user: dict = Depends(authorize_user)):
    if determine_role(user.get('role_mask')) not in ["superadmin", "admin"]:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a user!"
        )

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
        
        if form["admin"].isnumeric and int(form["admin"]) == 1:
            role_mask = int(0b011)
        elif form["admin"].isnumeric and int(form["admin"]) == 0:
            role_mask = int(0b001)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid role mask!"
            )
        
        new_user = User(
            first_name=form["first_name"],
            last_name=form["last_name"],
            username=form["username"],
            email=form["email"],
            hashed_password=pwd_context.hash(form["password"]),
            role_mask = role_mask,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return RedirectResponse(
            url="/dashboard/users",
            status_code=303
        )


@router.post("/users", response_class=HTMLResponse)
async def users(request: Request, user: dict = Depends(authorize_user)):
    if determine_role(user.get('role_mask')) not in ["superadmin", "admin"]:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a user!"
        )


@router.put("/edit_user/{user_id}", response_class=HTMLResponse)
async def edit_user(request: Request, user_id: int, user: dict = Depends(authorize_user)):
    if determine_role(user.get('role_mask')) not in ["superadmin", "admin"]:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a user!"
        )


@router.delete("/delete_user/{user_id}", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: int, user: dict = Depends(authorize_user)):
    if determine_role(user.get('role_mask')) not in ["superadmin", "admin"]:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a user!"
        )


@router.put("/change_schduler", response_class=HTMLResponse)
async def change_scheduler(request: Request, user: dict = Depends(authorize_user)):
    if determine_role(user.get('role_mask')) not in ["superadmin", "admin"]:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You are not authorized to create a user!"
        )