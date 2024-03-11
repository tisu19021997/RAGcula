from enum import Enum
from pathlib import Path
from typing import List, Optional, Self, Sequence, Union

from fsspec import AbstractFileSystem
from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    load_indices_from_storage,
    set_global_service_context,
)
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.chat_engine.types import (
    AgentChatResponse,
    StreamingAgentChatResponse,
)
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM, ChatMessage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.readers.base import BaseReader
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.schema import TransformComponent
from llama_index.core.selectors import LLMMultiSelector, LLMSingleSelector
from llama_index.core.tools import AsyncBaseTool, RetrieverTool
from rag.default import Default
from rag.prompt import LLM_SYSTEM_MESSAGE
from rag.systems.base import BaseSystem


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
            )
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
        fs: Optional[AbstractFileSystem] = None,
    ) -> List[Document]:
        """_summary_

        Args:
            file_path (Union[Path, str]): _description_
            document_id (str): Document ID for PostgreSQL.
            include_metadata (bool, optional): _description_. Defaults to True.
            fs (Optional[AbstractFileSystem], optional): _description_. Defaults to None.

        Returns:
            List[Document]: _description_
        """
        self.documents = self.data_loader.load_data(
            file_path, metadata=include_metadata, fs=fs
        )
        return self.documents

    def delete_indices(
        self, storage_context: StorageContext, doc_ids: Sequence[str]
    ) -> Self:
        self.load_indices(storage_context)
        for index in self.indices:
            for doc_id in doc_ids:
                index.delete_ref_doc(ref_doc_id=doc_id, delete_from_docstore=True)
                print(f"Deleteing {doc_id} from {index.index_struct.get_type()}")
        return self

    def build_retrievers(
        self,
        storage_context: StorageContext,
        mode: RouterMode = RouterMode.SINGLE,
        selector_template_str: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Self:
        if self.engine:
            print("Engine is already running.")
            return self

        self.load_indices(storage_context)

        # TODO: how to set description for RetrieverTool?
        self.retreiver_tools = [
            RetrieverTool.from_defaults(retriever=indice.as_retriever())
            for indice in self.indices
        ]
        selector = RouterMode(mode).selector.from_defaults(
            prompt_template_str=selector_template_str
        )
        self.context_retriever = RouterRetriever(
            selector=selector, retriever_tools=self.retreiver_tools
        )
        self.engine = ContextChatEngine.from_defaults(
            # retriever=self.context_retriever,
            retriever=self.indices[0].as_retriever(),
            memory=ChatMemoryBuffer.from_defaults(llm=Settings.llm),
            system_prompt=system_prompt or LLM_SYSTEM_MESSAGE,
        )
        return self

    def chat(
        self, message: str, chat_history: List[ChatMessage] | None = None
    ) -> Union[AgentChatResponse, StreamingAgentChatResponse]:
        return self.engine.chat(message, chat_history)

    def stream_chat(
        self, message: str, chat_history: List[ChatMessage] | None = None
    ) -> StreamingAgentChatResponse:
        return self.engine.stream_chat(message, chat_history)
