"""
Database Session Management
Supports SQLite and PostgreSQL via SQLAlchemy declarative ORM.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

# Normalize database URL (Render & cloud providers often output postgres:// instead of postgresql://)
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Configure connection arguments and connection pool parameters
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL / Neon Serverless configuration:
    # pool_pre_ping=True handles Neon automatic compute suspension/wake-up transparently
    # pool_recycle=300 recycles connections every 5 minutes to prevent stale socket errors
    pg_connect_args = {}
    if "sslmode" not in db_url:
        pg_connect_args["sslmode"] = "require"

    engine = create_engine(
        db_url,
        connect_args=pg_connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
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
