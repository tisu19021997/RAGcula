from enum import Enum
from pathlib import Path
from typing import List, Optional, Self, Sequence, Union

from app.database import get_vector_store_singleton
from app.upload.crud import get_all_documents
from fsspec import AbstractFileSystem
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    load_indices_from_storage,
    set_global_service_context,
)
from llama_index.core.agent import ReActAgent
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine import ContextChatEngine, SimpleChatEngine
from llama_index.core.chat_engine.types import (
    AgentChatResponse,
    StreamingAgentChatResponse,
)
from llama_index.core.data_structs.data_structs import IndexStruct
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.indices import VectorStoreIndex
from llama_index.core.indices.base import BaseIndex
from llama_index.core.indices.vector_store.retrievers import VectorIndexRetriever
from llama_index.core.llms import LLM, ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.query_engine import (
    BaseQueryEngine,
    RouterQueryEngine,
    SubQuestionQueryEngine,
)
from llama_index.core.readers.base import BaseReader
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.schema import TransformComponent
from llama_index.core.selectors import LLMMultiSelector, LLMSingleSelector
from llama_index.core.tools import AsyncBaseTool, QueryEngineTool, ToolMetadata
from llama_index.core.vector_stores import (
    FilterCondition,
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)
from rag.default import Default
from rag.prompt import LLM_SYSTEM_MESSAGE
from rag.systems.base import BaseSystem, DocumentIndices
from rag.transform.cleaner import UnstructuredIOCleaner
from rag.utils import (
    custom_react_chat_formatter,
    index_to_query_engine_tool_mapping,
    select_files_to_retrieve,
)


class RouterMode(Enum):
    SINGLE = "single"
    MULTI = "multi"

    def __init__(self, mode: str):
        self.mode = mode

    @property
    def selector(self) -> Union[LLMMultiSelector, LLMSingleSelector]:
        if self.mode == "single":
            return LLMSingleSelector
        elif self.mode == "multi":
            return LLMMultiSelector
        raise ValueError(f"mode must be either single or multi, found {self.mode}")


class RouterSystem(BaseSystem):
    retriever_tools: List[AsyncBaseTool] = None

    def __init__(
        self,
        data_loader: BaseReader,
        llm: Optional[LLM] = None,
        embed_model: Optional[BaseEmbedding] = None,
        transformations: Optional[List[TransformComponent]] = None,
    ) -> None:
        llm = llm or Default.llm()
        embed_model = embed_model or Default.embedding_model()
        transformations = transformations or [
            TokenTextSplitter(
                separator=" ",
                chunk_size=embed_model.max_length,
                chunk_overlap=24,
                tokenizer=embed_model._tokenizer,
            ),
            UnstructuredIOCleaner(),
        ]
        super().__init__(
            data_loader=data_loader,
            llm=llm,
            embed_model=embed_model,
            transformations=transformations,
        )

    @classmethod
    def from_defaults(
        cls,
    ):
        pass

    def load_data(
        self,
        file_path: Union[Path, str],
        include_metadata: bool = True,
    ) -> List[Document]:
        self.documents = self.data_loader.load_data(
            file_path, metadata=include_metadata
        )
        return self.documents

    def add_indices(
        self, indices: List[BaseIndex[IndexStruct]], namespace: str, doc_id: str
    ) -> Self:
        if not self.indices:
            self.indices = {}
        # Set unique id for each index.
        for index in indices:
            index.set_index_id(
                f"{namespace}.{index.index_struct.get_type().value}.{doc_id}"
            )
        self.indices[doc_id] = DocumentIndices(indices=indices)
        return self

    async def load_indices(
        self, storage_context: StorageContext, force_reload: bool = False
    ) -> Self:
        vector_store = await get_vector_store_singleton()
        # If there are already indices, just return it.
        if not self.indices or force_reload:
            self.indices = {}
            documents = get_all_documents()
            for document in documents:
                # TODO: abstract this for abitrary indices.
                indices = load_indices_from_storage(
                    storage_context=storage_context,
                    index_ids=document.llama_index_metadata["index_ids"],
                )
                # Hard code vector store for now.
                vector_index = VectorStoreIndex.from_vector_store(vector_store)
                indices.append(vector_index)

                self.indices[str(document.id)] = DocumentIndices(indices=indices)
        return self

    async def delete_indices(
        self, storage_context: StorageContext, doc_id: str, ref_doc_ids: Sequence[str]
    ) -> Self:
        await self.load_indices(storage_context)
        for _, indices in self.indices.items():
            for ref_doc_id in ref_doc_ids:
                # TODO: this not delete the actual index from index_store.json, just reference nodes.
                # try use index.delete_nodes(node_ids) or index.delete()
                for index in indices.indices:
                    index.delete_ref_doc(
                        ref_doc_id=ref_doc_id, delete_from_docstore=True
                    )
                    print(
                        f"Deleteing doc_ids={ref_doc_id} from {index.index_struct.get_type()}"
                    )
        del self.indices[doc_id]

        return self

    def _index_to_query_engine(
        self, doc_id: str, index: VectorStoreIndex
    ) -> BaseQueryEngine:
        """Filter the vector store index to only nodes related to a document."""
        filters = MetadataFilters(
            filters=[
                MetadataFilter(key="doc_uuid", operator=FilterOperator.EQ, value=doc_id)
            ]
        )
        kwargs = {"similarity_top_k": 2, "filters": filters}
        return index.as_query_engine(**kwargs)

    # TODO: an agent for each document.
    async def build_engine(
        self,
        storage_context: StorageContext,
        document_ids: List[str],
        document_names: List[str],
        document_summaries: List[str],
        force_reload: bool = False,
    ) -> Self:
        # Engine is already loaded.
        if self.engine and not force_reload:
            print("Engine already started. Skip loading.")
            return self
        await self.load_indices(storage_context)

        # Not uploaded any documents. Do causal chat.
        if len(self.indices) == 0:
            print("No document uploaded. Use simple chat interface.")
            self.engine = SimpleChatEngine.from_defaults(
                memory=ChatMemoryBuffer.from_defaults(),
                system_prompt="You are a helpful assistant.",
            )
            return self

        agents = {}
        for doc_id, indices in self.indices.items():
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="doc_uuid", operator=FilterOperator.EQ, value=doc_id
                    )
                ]
            )
            query_engine_tools = [
                index_to_query_engine_tool_mapping(
                    indices.vector, tool_name=f"vector_store_index", filters=filters
                ),
                index_to_query_engine_tool_mapping(
                    indices.summary, tool_name=f"summary_index"
                ),
            ]
            agent = RouterQueryEngine.from_defaults(
                query_engine_tools=query_engine_tools, select_multi=False
            )
            agents[doc_id] = agent

        # TODO: add null tools for questions that do not need retrieval at all.
        top_level_tools = [
            QueryEngineTool(
                query_engine=agents[str(document_id)],
                metadata=ToolMetadata(
                    name=f"file_{i}",
                    description="Provide information about a document with a summary:"
                    + document_summaries[i],
                ),
            )
            for i, document_id in enumerate(document_ids)
        ]
        self.engine = ReActAgent.from_tools(
            tools=top_level_tools,
            react_chat_formatter=custom_react_chat_formatter(document_names),
            memory=ChatMemoryBuffer.from_defaults(token_limit=4096),
            max_iterations=10,
            verbose=True,
        )

        return self

    def chat(
        self,
        message: str,
        storage_context: StorageContext,
        chat_history: List[ChatMessage] | None = None,
    ) -> Union[AgentChatResponse, StreamingAgentChatResponse]:
        self.build_engine(message, storage_context)
        return self.engine.chat(message, chat_history)

    def stream_chat(
        self,
        message: str,
        storage_context: StorageContext,
        chat_history: List[ChatMessage] | None = None,
    ) -> StreamingAgentChatResponse:
        self.build_engine(message, storage_context)
        return self.engine.stream_chat(message, chat_history)
