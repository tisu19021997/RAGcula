import uuid as uuid_pkg
from typing import Dict, List, Optional

from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import JSON, Column, Field, SQLModel, String


class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4, primary_key=True
    )
    display_name: str
    path: str
    is_active: bool
    summary: str
    # llamaindex_ref_doc_ids: List[str] = Field(
    #     default=None, sa_column=Column(ARRAY(String()))
    # )
    llama_index_metadata: Dict = Field(
        default={"ref_doc_ids": List[str], "index_ids": List[str]},
        sa_column=Column(JSON),
    )
