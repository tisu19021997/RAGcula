import uuid as uuid_pkg
from sqlmodel import Field, SQLModel
from typing import Optional


class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4, primary_key=True)
    s3_path: str  # Bucket S3 URL
    s3_url: Optional[str]  # Preview S3 presigned URL
    is_active: bool
    description: str
    question: str
    user_id: str
