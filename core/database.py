"""
Database connection management using SQLAlchemy.
Provides session management with context manager pattern.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from core.config import DB_URL

# Base class for ORM models
Base = declarative_base()

# Create database engine
engine = create_engine(DB_URL, echo=True)

# Create session factory
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    
    Usage:
        with session_scope() as session:
            session.add(obj)
            # Changes are automatically committed
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
