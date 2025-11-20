from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from settings import settings

url = '{engine}://{user}:{password}@{host}:{port}/{db}'.format(
    engine=settings.postgres_engine,
    user=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    db=settings.postgres_db,
)
engine = create_async_engine(url)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def get_db_session_cm() -> AsyncSession:
    """Method to call AsyncSession outside of dependencies"""
    async with AsyncSessionLocal() as session:
        yield session