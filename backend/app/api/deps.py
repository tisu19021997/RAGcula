from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal


async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as db:
        yield db
