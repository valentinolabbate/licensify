"""
Database Session Management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Convert standard PostgreSQL URL to async URL
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
