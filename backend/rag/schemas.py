from typing import Optional
from pydantic import BaseModel, ConfigDict
from llama_index import (
    DocumentSummaryIndex,
    VectorStoreIndex,
    SummaryIndex,
)


class RagIndex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    vector: VectorStoreIndex
    summary: Optional[SummaryIndex] = None
    doc_summary: Optional[DocumentSummaryIndex] = None
