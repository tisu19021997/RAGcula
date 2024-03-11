import fsspec
from pathlib import Path
from typing import Dict, List, Optional, Union
from io import BytesIO
from datetime import timedelta
from cachetools import cached, TTLCache
from llama_index.core import StorageContext
from llama_index.core.readers.base import BaseReader
from llama_index.core import Document
from llama_index.core.vector_stores.types import VectorStore


class CustomPDFReader(BaseReader):
    def load_data(
        self,
        file_path: Union[Path, str],
        metadata: bool = True,
        extra_info: Optional[Dict] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> List[Document]:
        """Loads list of documents from PDF file and also accepts extra information in dict format."""
        return self.load(file_path, metadata=metadata, extra_info=extra_info, fs=fs)

    def load(
        self,
        file_path: Union[Path, str],
        metadata: bool = True,
        extra_info: Optional[Dict] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None
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


@cached(
    TTLCache(maxsize=10, ttl=timedelta(minutes=5).total_seconds()),
    key=lambda *args, **kwargs: "global_storage_context",
)
def get_storage_context(persist_dir: str, vector_store: VectorStore) -> StorageContext:
    print("Creating new storage context.")
    return StorageContext.from_defaults(
        persist_dir=persist_dir,
        vector_store=vector_store
    )
