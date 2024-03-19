from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

import fsspec
from app.upload.models import Document as D
from cachetools import TTLCache, cached
from llama_index.core import (
    Document,
    PromptTemplate,
    Settings,
    StorageContext,
    SummaryIndex,
    VectorStoreIndex,
    get_response_synthesizer,
)
from llama_index.core.agent import ReActChatFormatter
from llama_index.core.indices.base import BaseIndex
from llama_index.core.llms import LLM
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.readers.base import BaseReader
from llama_index.core.response_synthesizers import BaseSynthesizer, ResponseMode
from llama_index.core.selectors import LLMMultiSelector
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.core.vector_stores.types import VectorStore


class CustomPDFReader(BaseReader):
    def load_data(
        self,
        file_path: Union[Path, str],
        metadata: bool = True,
        extra_info: Optional[Dict] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> List[Document]:
        """Loads list of documents from PDF file and also accepts extra information in dict format."""
        return self.load(file_path, metadata=metadata, extra_info=extra_info, fs=fs)

    def load(
        self,
        file_path: Union[Path, str],
        metadata: bool = True,
        extra_info: Optional[Dict] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> List[Document]:
        """Loads list of documents from PDF file and also accepts extra information in dict format.

        Args:
            file_path (Union[Path, str]): file path of PDF file (accepts string or Path).
            metadata (bool, optional): if metadata to be included or not. Defaults to True.
            extra_info (Optional[Dict], optional): extra information related to each document in dict format. Defaults to None.

        Raises:
            TypeError: if extra_info is not a dictionary.
            TypeError: if file_path is not a string or Path.

        Returns:
            List[Document]: list of documents.
        """
        import fitz

        # check if file_path is a string or Path
        if not isinstance(file_path, str) and not isinstance(file_path, Path):
            raise TypeError("file_path must be a string or Path.")

        # open PDF file
        with fs.open(file_path, "rb") as fp:
            doc = fitz.open("pdf", stream=BytesIO(fp.read()))

        # if extra_info is not None, check if it is a dictionary
        if extra_info:
            if not isinstance(extra_info, dict):
                raise TypeError("extra_info must be a dictionary.")

        # if metadata is True, add metadata to each document
        if metadata:
            if not extra_info:
                extra_info = {}
            extra_info["total_pages"] = len(doc)
            extra_info["file_path"] = file_path

            # return list of documents
            return [
                Document(
                    text=page.get_text().encode("utf-8"),
                    extra_info=dict(
                        extra_info,
                        **{
                            "source": f"{page.number+1}",
                        },
                    ),
                )
                for page in doc
            ]

        else:
            return [
                Document(
                    text=page.get_text().encode("utf-8"), extra_info=extra_info or {}
                )
                for page in doc
            ]


storage_cache = TTLCache(maxsize=10, ttl=timedelta(minutes=5).total_seconds())


# @cached(
#     storage_cache,
#     key=lambda *args, **kwargs: "global_storage_context",
# )
def get_storage_context(persist_dir: str, vector_store: VectorStore) -> StorageContext:
    print("Creating new storage context.")
    return StorageContext.from_defaults(
        persist_dir=persist_dir, vector_store=vector_store
    )


def select_files_to_retrieve(query: str, documents: Sequence[D]) -> D:
    choices = [
        ToolMetadata(description=document.summary, name=document.display_name)
        for document in documents
    ]
    selector = LLMMultiSelector.from_defaults()
    selected_docs = [
        documents[selection.index]
        for selection in selector.select(choices, query=query).selections
    ]
    return selected_docs


def summarize_documents(
    documents: Sequence[Document],
    storage_context: Optional[StorageContext] = None,
    n_sentences: int = 1,
    index: SummaryIndex = None,
) -> str:
    if not storage_context:
        storage_context = StorageContext.from_defaults()

    if not index:
        index = SummaryIndex.from_documents(
            documents, storage_context=storage_context, show_progress=True
        )
    rs = get_response_synthesizer(
        response_mode=ResponseMode.TREE_SUMMARIZE, use_async=True
    )
    qe = index.as_query_engine(response_synthesizer=rs)
    query = f"Summarize the given document in {n_sentences} sentences. Do not use bullet points."
    summary = qe.query(query).response

    return summary


def get_custom_response_synth(documents: Sequence[D]) -> BaseSynthesizer:
    doc_titles = "\n".join(
        [f"({index}) {doc.display_name}" for index, doc in enumerate(documents)]
    )
    refine_str = f"""A user has uploaded a set of documents and has asked a question about them.
The documents have the following titles: {doc_titles}
The original query is as follow: {{query_str}}
We have provided an existing answer: {{existing_answer}}
We have the opportunity to refine the existing answer (only if needed) with some more context below.
------------\n{{context_msg}}\n------------
Given the new context, refine the original answer to better answer the query. If the context isn't useful, return the original answer.
Refined Answer:""".strip()
    refine_prompt = PromptTemplate(
        refine_str,
        prompt_type=PromptType.REFINE,
    )

    qa_str = f"""A user has uploaded a set of documents and has asked a question about them.
The documents have the following titles: {doc_titles}
Context information is below.\n
------------\n{{context_msg}}\n------------
Given the context information and not prior knowledge, answer the query.
Query: {{query_str}}
Answer:""".strip()
    qa_prompt = PromptTemplate(
        qa_str,
        prompt_type=PromptType.QUESTION_ANSWER,
    )
    return get_response_synthesizer(
        text_qa_template=qa_prompt, refine_template=refine_prompt
    )


def custom_react_chat_formatter(uploads: List[D]) -> ReActChatFormatter:
    doc_titles = "\n".join(
        [f"({idx}) {upload.display_name}" for idx, upload in enumerate(uploads)]
    )
    context = f"""A user has uploaded a set of documents and has asked a question about them.
Here are the documents that the user has uploaded to discuss with you:
{doc_titles}"""
    chat_formatter = ReActChatFormatter.from_defaults(context=context)
    return chat_formatter


def index_to_query_engine_tool_mapping(
    index: BaseIndex,
    llm: LLM = None,
    tool_name: str = "query_engine_tool",
    filters: Sequence[MetadataFilters] = None,
) -> QueryEngineTool | None:
    llm = llm or Settings.llm
    # Filters only available for vector store.
    qe = index.as_query_engine(llm=llm, filters=filters)
    tool = None

    if isinstance(index, VectorStoreIndex):
        tool = QueryEngineTool(
            query_engine=qe,
            metadata=ToolMetadata(
                name=f"vector_store_{tool_name}",
                description=(
                    "Useful for questions, queries related specific aspects of a document or topic. "
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        )
    elif isinstance(index, SummaryIndex):
        tool = QueryEngineTool(
            query_engine=qe,
            metadata=ToolMetadata(
                name=f"summary_{tool_name}",
                description=(
                    "Useful for questions, queries that require a holistic summary. "
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        )
    return tool


def get_node_ids(document: D, storage_context: StorageContext) -> List[str] | None:
    all_ref_doc = storage_context.docstore.get_all_ref_doc_info()
    if len(all_ref_doc) == 0:
        return None

    node_ids = [
        node_id
        for llama_ref_doc in document.llama_index_metadata.ref_doc_ids
        for node_id in all_ref_doc[llama_ref_doc].node_ids
    ]
    return node_ids


def get_tool_description_from_upload(upload: D) -> str:
    description = (
        f"Contains information about the document named {upload.display_name}.\n"
        f"Tool summary: {upload.summary}\n"
        f"Use a detailed plain text question as input to the tool."
    )
    return description
