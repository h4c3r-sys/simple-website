import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for local testing if env var not set, though docker-compose sets it.
    DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/discord_bot_db"

# Create the async engine. echo=False disables verbose SQL logging.
engine = create_async_engine(DATABASE_URL, echo=False)

# Session factory for creating async database sessions
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """
    Dependency generator to yield a database session.
    """
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """
    Creates all tables defined in models.py if they don't exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
