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
    role_mask: int = Field(default=1)

    created_at: datetime = Field(default = datetime.utcnow())
    updated_at: datetime = Field(default = datetime.utcnow())