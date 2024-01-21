from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import BIGINT, VARCHAR, BOOLEAN
from app.orm_models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    username = Column(VARCHAR, unique=True, index=True)
    email = Column(VARCHAR)
    disabled = Column(BOOLEAN, default=False)
    hashed_password = Column(VARCHAR, nullable=False)
