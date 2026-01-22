from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:yourpassword@localhost:5432/ecommerce_db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # shows SQL in console
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()
