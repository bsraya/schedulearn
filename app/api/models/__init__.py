# initialize the database connection
from sqlmodel import SQLModel, create_engine, Session
from dotenv import dotenv_values
from .user import User

__all__ = ["User"]

# get DATABASE_URL from .env
url = dotenv_values(".env").get("DATABASE_URL")

engine = create_engine(url, echo=True)

def create_db_and_tables():
  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session