from pydantic import BaseModel

# TODO: delete or archive this and the whole manual authentication.


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class BaseUser(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None


class RawUser(BaseUser):
    password: str


class UserInDB(BaseUser):
    hashed_password: str
