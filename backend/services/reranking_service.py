from typing import List, Dict, Any
from sentence_transformers import CrossEncoder


class RerankingService:
    """
    A service for re-ranking documents using a cross-encoder model.
    """

    def __init__(self):
        """
        Initializes the RerankingService.
        """
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2", max_length=512)

    def rerank_documents(
        self, query: str, retrieved_docs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Re-ranks a list of documents based on their relevance to a query.

        Args:
            query: The user's query.
            retrieved_docs: The documents retrieved from the vector store.

        Returns:
            A dictionary of re-ranked documents in the same format as the input.
        """
        if not retrieved_docs["documents"] or not retrieved_docs["documents"][0]:
            return retrieved_docs

        doc_texts = retrieved_docs["documents"][0]
        metadatas = retrieved_docs["metadatas"][0]
        ids = retrieved_docs["ids"][0]

        pairs = [[query, doc_text] for doc_text in doc_texts]
        scores = self.model.predict(pairs)

        # Combine documents with their scores and sort
        scored_docs = sorted(
            zip(scores, doc_texts, metadatas, ids), key=lambda x: x[0], reverse=True
        )

        # Unzip the sorted documents
        scores, doc_texts, metadatas, ids = zip(*scored_docs)

        return {
            "documents": [list(doc_texts)],
            "metadatas": [list(metadatas)],
            "ids": [list(ids)],
        }
