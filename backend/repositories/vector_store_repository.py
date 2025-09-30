import chromadb
from typing import List, Dict, Any
from settings import settings
import logging


class VectorStoreRepository:
    """
    A repository for interacting with the ChromaDB vector store.
    """

    def __init__(self):
        """
        Initializes the VectorStoreRepository.
        """
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST, port=settings.CHROMA_PORT
        )
        self.collection = self.client.get_or_create_collection(name="documents")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ):
        """
        Adds documents to the vector store.

        Args:
            ids: A list of unique ids for the documents.
            documents: A list of document texts.
            metadatas: A list of metadata for the documents.
            embeddings: A list of embeddings for the documents.
        """
        self.collection.add(
            ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
        )

    def query(
        self, query_embeddings: List[List[float]], n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Queries the vector store for similar documents.

        Args:
            query_embeddings: A list of embeddings for the query.
            n_results: The number of results to return.

        Returns:
            Query results from the vector store.
        """
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=["metadatas", "documents"],
        )

    def health_check(self) -> bool:
        """
        Checks the connection to the vector store.

        Returns:
            True if the connection is successful, False otherwise.
        """
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            logging.error(f"Error checking vector store health: {e}")
            return False
