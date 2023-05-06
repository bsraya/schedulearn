from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Machine(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  name: Optional[str] = Field(default=None)

  created_at: datetime = Field(default = datetime.utcnow())
  updated_at: datetime = Field(default = datetime.utcnow())