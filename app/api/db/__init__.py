from sqlmodel import SQLModel, create_engine
from dotenv import dotenv_values
from app.api.shared.utils.monitor import get_gpus
from app.api.models import System, Machine, Gpu
from sqlmodel import Session, select
from typing import Final

servers: Final = ["gpu3", "gpu4", "gpu5"]

configurations: Final = [
  {
    "configuration": "scheduler",
    "value": "FIFO"
  },
  {
    "configuration": "previous_server",
    "value": "gpu5"
  },
  {
    "configuration": "current_server",
    "value": "gpu3"
  },
  {
      "configuration": "next_server",
      "value": "gpu4"
  }
]

url = dotenv_values(".env").get("DATABASE_URL")

engine = create_engine(url, echo=True)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)

def save_system_settings():
  with Session(engine) as session:
    for server in servers:
      if not session.exec(select(Machine).where(Machine.name == server)).first():
        session.add(Machine(name=server))

    for configuration in configurations:
      if not session.exec(select(System).where(System.configuration == configuration["configuration"])).first():
        session.add(System(**configuration))

    gpus = get_gpus()
    for gpu in gpus:
      if not session.exec(select(Gpu).where(Gpu.uuid == gpu.uuid)).first():
        session.add(
          Gpu(
            name=gpu.name, 
            brand = "NVIDIA" if "NVIDIA" in gpu.name else "AMD",
            uuid=gpu.uuid,
            machine_id = gpu.machine_id
          )
        )
    session.commit()

__all__ = [
  "create_db_and_tables",
  "engine",
  "save_system_settings"
]