from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    container: Optional[str] = Field(default=None)
    status : Optional[str] = Field(default=None)
    script: Optional[str] = Field(default=None)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
