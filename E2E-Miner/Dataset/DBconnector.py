from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

from environment import DB_URL

Base = declarative_base()
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker()
