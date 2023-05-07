from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class System(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    configuration: Optional[str]
    value: Optional[str]

    created_at: datetime = Field(default = datetime.utcnow())
    updated_at: datetime = Field(default = datetime.utcnow())