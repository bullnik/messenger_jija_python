from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

USER = getenv("POSTGRES_USER")
PASSWORD = getenv("POSTGRES_PASSWORD")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("POSTGRES_DB")

db_url = f"postgresql://{USER}:{PASSWORD}@postgres:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)
session = sessionmaker(engine)
