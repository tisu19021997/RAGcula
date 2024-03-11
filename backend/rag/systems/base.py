from typing import Any, List, Mapping, Optional, Union, Self
from fsspec import AbstractFileSystem
from pathlib import Path
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict
from llama_index.core import (
    StorageContext,
    ServiceContext,
    Settings,
    Document,
    load_indices_from_storage,
    set_global_service_context
)
from llama_index.core.readers.base import BaseReader
from llama_index.core.llms import LLM
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.query_engine import BaseQueryEngine
from llama_index.core.schema import TransformComponent
from llama_index.core.indices.base import BaseIndex
from llama_index.core.data_structs.data_structs import IndexStruct
from llama_index.core.chat_engine.types import BaseChatEngine

from rag.default import Default


class Indexer(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    index: BaseIndex[IndexStruct]
    retriever_kwargs: Mapping[str, Any]
    description: str


class BaseSystem(ABC):
    data_loader: BaseReader
    llm: LLM
    embed_model: BaseEmbedding
    indices: List[BaseIndex[IndexStruct]] = None
    storage: StorageContext
    response_composer: BaseSynthesizer
    context_retriever: BaseRetriever
    engine: Union[BaseQueryEngine, BaseChatEngine] = None
    documents: List[Document] = None

    def __init__(
        self,
        data_loader: BaseReader,
        transformations: List[TransformComponent],
        llm: Optional[LLM] = None,
        embed_model: Optional[BaseEmbedding] = None,
        response_composer: Optional[BaseSynthesizer] = None,
        # retriever: BaseRetriever
    ) -> "BaseSystem":
        self.data_loader = data_loader
        self.response_composer = response_composer
        Settings.llm = llm or Default.llm()
        Settings.embed_model = embed_model or Default.embedding_model()
        Settings.chunk_size = Settings.embed_model.max_length
        Settings.transformations = transformations
        
        # self.retriever = retriever

    @abstractmethod
    def load_data(self):
        raise NotImplementedError("load_data not implemented")

    @abstractmethod
    def delete_indices(self):
        raise NotImplementedError("delete_indices not implemented")

    @abstractmethod
    def build_retrievers(self):
        raise NotImplementedError("build_retrievers not implemented")

    def add_indice(self, index: BaseIndex[IndexStruct], namespace: str) -> Self:
        index.set_index_id(
            f"{namespace}.{index.index_struct.get_type().value}")
        if not self.indices:
            self.indices = []
        self.indices.append(index)
        return self

    def load_indices(self, storage_context: StorageContext) -> Self:
        # If there are already indices, just return it.
        if not self.indices:
            self.indices = load_indices_from_storage(
                storage_context=storage_context)
        return self

    # TODO: implement method to print tree structure of the system.
    # just like Haystack pipeline.draw().
    def __str__(self) -> str:
        # pygraphviz
        return f"LLM={self.service_context.llm.__module__}, Encoder={self.service_context.embed_model.model_name}"

    def docs_to_index(self, documents: List[Document]) -> Self:
        for index in self.indices:
            for document in documents:
                index.insert(document)
        return self

    def save_indices(self, save_dir: Union[Path, str], fs: Optional[AbstractFileSystem] = None) -> Self:
        for indexer in self.indices:
            indexer.storage_context.persist(persist_dir=save_dir, fs=fs)
        return self

    def chat(self):
        """Chat using chat engine"""
