import uuid as uuid_pkg
# from app.orm_models.base import Base
from sqlmodel import Field, SQLModel
from typing import Optional

# class Document(Base):
#     __tablename__ = "documents"

#     id = Column(BIGINT, primary_key=True, autoincrement=True)
#     file_name = Column(VARCHAR, nullable=False)
#     s3_path = Column(VARCHAR, nullable=False)
#     is_active = Column(BOOLEAN, default=True)
#     description = Column(VARCHAR, nullable=False)
#     question = Column(VARCHAR, nullable=False)
#     user_id = Column(VARCHAR, unique=True, nullable=False)


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4, primary_key=True)
    s3_path: str
    is_active: bool
    description: str
    question: str
    user_id: str
