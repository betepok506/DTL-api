from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aerial_photography.config import settings


# ======== Sync ============

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ======== Async ============
# engine = create_async_engine(settings.DATABASE_URL,  pool_pre_ping=True)
# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False,bind=engine, class_=AsyncSession)

# ======== End ============
