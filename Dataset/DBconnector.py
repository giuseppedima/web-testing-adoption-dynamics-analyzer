from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
#SCRIVERE QUI IL PATH PER IL FILE DI DATABASE
db = r"sqlite:////home/sergio/Scaricati/E2EGit.db"
Base = declarative_base()
engine = create_engine(db, echo=True)
Session = sessionmaker()
