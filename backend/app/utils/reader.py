import fsspec

from pathlib import Path
from typing import Dict, List, Optional

from llama_index.readers.base import BaseReader
from llama_index.schema import Document


class PDFReader(BaseReader):
    """PDF parser."""

    def __init__(self, return_full_document: Optional[bool] = False) -> None:
        """
        Initialize PDFReader.
        """
        self.return_full_document = return_full_document

    def load_data(
        self,
        file: Path, extra_info: Optional[Dict] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> List[Document]:
        """Parse file."""
        if isinstance(file, str):
            file = Path(file)

        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf is required to read PDF files: `pip install pypdf`"
            )
        with fs.open(file, "rb") as fp:
            # Create a PDF object
            pdf = pypdf.PdfReader(fp)

            # Get the number of pages in the PDF document
            num_pages = len(pdf.pages)

            docs = []

            # This block returns a whole PDF as a single Document
            if self.return_full_document:
                text = ""
                metadata = {"file_name": file.name}

                for page in range(num_pages):
                    # Extract the text from the page
                    page_text = pdf.pages[page].extract_text()
                    text += page_text

                docs.append(Document(text=text, metadata=metadata))

            # This block returns each page of a PDF as its own Document
            else:
                # Iterate over every page

                for page in range(num_pages):
                    # Extract the text from the page
                    page_text = pdf.pages[page].extract_text()
                    page_label = pdf.page_labels[page]

                    metadata = {"page_label": page_label,
                                "file_name": file.name}
                    if extra_info is not None:
                        metadata.update(extra_info)

                    docs.append(Document(text=page_text, metadata=metadata))

            return docs
