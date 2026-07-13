from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Base class for SQLAlchemy declarative models
class Base(DeclarativeBase):
    pass

# Engine configuration (different check_same_thread configuration for SQLite vs PostgreSQL)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Session Local factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# DB Dependency injection session helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
