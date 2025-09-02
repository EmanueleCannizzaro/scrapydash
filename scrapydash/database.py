# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./scrapydweb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session() -> Generator[Session, None, None]:
    """Alternative name for database session dependency"""
    return get_db()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
