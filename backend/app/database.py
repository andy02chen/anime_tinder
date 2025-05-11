from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Use the correct async format for PostgreSQL URL
# Example: postgresql+asyncpg://user:password@localhost/dbname
engine = create_async_engine(DATABASE_URL, echo=True)

# Async session factory
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Base model with async support
class Base(DeclarativeBase):
    pass
