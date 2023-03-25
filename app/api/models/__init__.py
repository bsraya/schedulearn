# initialize the database connection
from sqlmodel import SQLModel, create_engine, Session
from dotenv import dotenv_values
from .user import User

__all__ = ["User"]

url = dotenv_values(".env").get("DB_URL")

engine = create_engine(url, echo=True)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session