"""
Database Session Management
Supports SQLite and PostgreSQL via SQLAlchemy declarative ORM.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

# SQLite requires check_same_thread=False for multithreaded FastAPI requests
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency helper providing a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
