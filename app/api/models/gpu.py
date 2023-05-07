from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Gpu(SQLModel, table=True):
    id: Optional[int] = Field(default = None, primary_key = True)
    name: Optional[str] = Field(default = None)
    brand: Optional[str] = Field(default = None)
    uuid: Optional[str] = Field(default = None)
    
    added_at: datetime = Field(default = datetime.utcnow())
    updated_at: datetime = Field(default = datetime.utcnow())

    machine_id: Optional[int] = Field(default = None, foreign_key = "machine.id")