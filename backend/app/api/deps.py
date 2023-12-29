from typing import Generator, Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer(auto_error=False)


async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as db:
        yield db

AccessTokenDeps = Annotated[HTTPAuthorizationCredentials, Depends(security)]
