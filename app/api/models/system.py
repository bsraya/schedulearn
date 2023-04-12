from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class System(SQLModel, table=True):
    scheduler: Optional[str] = Field(default="ElasticFIFO")
    previous_server: str = "gpu5"
    current_server: str = "gpu3"
    next_server: str = "gpu4"