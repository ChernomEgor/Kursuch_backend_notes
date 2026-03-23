
from typing import Annotated

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import settings

from fastapi import Depends


engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True
)

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]