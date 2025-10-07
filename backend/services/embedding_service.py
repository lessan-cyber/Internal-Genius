import logging
import time
from typing import List
import google.generativeai as genai
from settings import settings


class EmbeddingService:
    """
    A service for generating embeddings for text chunks.
    """

    def __init__(self):
        """
        Initializes the EmbeddingService.
        """
        genai.configure(api_key=settings.GOOGLE_API_KEY)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for the given texts.

        Args:
            texts: A list of texts to embed.

        Returns:
            A list of embeddings.
        """
        embeddings = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                result = self._embed_batch_with_retry(batch)
                embeddings.extend(result)
            except Exception as e:
                logging.error(f"Error generating embedding for batch: {e}")
            time.sleep(1)  # Wait for 1 second between batches
        return embeddings

    def _embed_batch_with_retry(
        self, batch: List[str], max_retries=5, initial_delay=1
    ) -> List[List[float]]:
        """
        Embeds a batch of texts with retry logic.

        Args:
            batch: A list of texts to embed.
            max_retries: The maximum number of retries.
            initial_delay: The initial delay between retries.

        Returns:
            A list of embeddings.
        """
        delay = initial_delay
        for i in range(max_retries):
            try:
                result = genai.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    content=batch,
                    task_type="retrieval_document",
                )
                return result["embedding"]
            except Exception as e:
                if "Rate limit exceeded" in str(e) and i < max_retries - 1:
                    logging.info(f"Rate limit exceeded. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise e
        return []  # Return an empty list if all retries fail

    def embed_query(self, query: str) -> List[float]:
        """
        Generates an embedding for a single query.

        Args:
            query: The query to embed.

        Returns:
            The embedding for the query.
        """
        try:
            result = genai.embed_content(
                model=settings.EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as e:
            logging.error(f"Error generating embedding for query: {e}")
            return []
