import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from passlib.context import CryptContext

from app import schema
from app.api.deps import get_db
from app.orm_models.db import User

load_dotenv(find_dotenv())

logger = logging.getLogger("uvicorn")
user_router = r = APIRouter()

SECRET_KEY = os.environ["APP_AUTH_SECRET_KEY"]
ALGORITHM = os.environ["APP_AUTH_ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ["APP_AUTH_ACCESS_TOKEN_EXPIRE_MINUTES"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"}
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, username: str):
    stmt = select(User).filter_by(username=username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    return schema.UserInDB(
        username=user.username,
        email=user.email,
        disabled=user.disabled,
        hashed_password=user.hashed_password
    )


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_token(token: str):
    """Validate a give access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return False
    return payload


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
):
    # Authenticate the given token.
    payload = authenticate_token(token)
    if not payload:
        raise credentials_exception

    # Parse the payload username.
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    token_data = schema.TokenData(username=username)

    # Retrieve the user from database.
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[schema.UserInDB, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return current_user


@r.post("")
async def create_user(
    user: schema.RawUser,
    db: AsyncSession = Depends(get_db)
):
    """CREATE a new user in database after hasing their password.

    Args:
        user (schema.RawUser): user informations like username, email and password.
        db (AsyncSession): the local async session.
    """
    hashed_password = get_password_hash(user.password)
    # user_dict.update({"hashed_password": hashed_password})
    user = User(
        username=user.username,
        email=user.email,
        disabled=user.disabled,
        hashed_password=hashed_password)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@r.post("/token", response_model=schema.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """Given user information from the form data, try to log in. 
    If success, return the Bearer access token. Else, raise the exception.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@r.get("/me", response_model=schema.UserInDB)
async def read_users_me(
    current_user: Annotated[schema.UserInDB, Depends(get_current_active_user)]
):
    return current_user
