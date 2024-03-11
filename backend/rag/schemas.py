from typing import Optional
from pydantic import BaseModel, ConfigDict
from llama_index.core import DocumentSummaryIndex, VectorStoreIndex
from llama_index.core.indices import SummaryIndex


class RagIndex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    vector: VectorStoreIndex
    summary: Optional[SummaryIndex] = None
    doc_summary: Optional[DocumentSummaryIndex] = None
