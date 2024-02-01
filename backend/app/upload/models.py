import uuid as uuid_pkg
from sqlmodel import Field, SQLModel, Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from typing import Optional, List


class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4, primary_key=True)
    display_name: str
    path: str
    is_active: bool
    description: str
    question: str
    user_id: str
    llamaindex_ref_doc_ids: List[str] = Field(
        default=None, sa_column=Column(ARRAY(String())))
