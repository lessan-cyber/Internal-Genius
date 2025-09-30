import logging
from pathlib import Path
from typing import List
from docling_core.types.doc import DoclingDocument
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker


class DocumentService:
    """
    A service for handling document loading and processing.
    """

    def __init__(self):
        """Initialize the document service with a document converter."""
        self.converter = DocumentConverter()
        self.chunker = HybridChunker()

    def load_and_chunk_documents(self, file_paths: List[Path]) -> List[DoclingDocument]:
        """
        Loads and chunks documents from the given file paths.

        Args:
            file_paths: A list of paths to the documents.

        Returns:
            A list of chunked documents.
        """
        documents = []
        # supported_extensions = [".pdf", ".docx", ".md", ".txt"]
        for file_path in file_paths:
            try:
                result = self.converter.convert(file_path)
                documents.append(result.document)
            except Exception as e:
                logging.error(f"Error loading document {file_path}: {e}")

        chunked_documents = []
        for doc in documents:
            try:
                chunks = self.chunker.chunk(doc)
                chunked_documents.extend(chunks)
            except Exception as e:
                logging.error(f"Error chunking document: {e}")
        return chunked_documents
