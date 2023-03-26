from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(default=None)
    username: str = Field(default=None)
    last_name: str = Field(default=None)
    first_name: str = Field(default=None)
    hashed_password: str = Field(default=None)
    admin: bool = Field(default=False)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)