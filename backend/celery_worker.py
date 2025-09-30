import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add backend directory to Python path for consistent imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from celery import Celery
from settings import settings
from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from repositories.vector_store_repository import VectorStoreRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Celery configuration
celery = Celery(
    "internal_genius",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["celery_worker"],
)

celery.conf.update(settings.CELERY_CONFIG)


def sanitize_metadata_value(value: Any) -> Any:
    """
    Recursively sanitize a metadata value to ensure ChromaDB compatibility.

    Args:
        value: The value to sanitize

    Returns:
        ChromaDB-compatible value or None if unsanitizable
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        # Skip lists/tuples entirely as they often contain complex objects
        return None
    elif isinstance(value, dict):
        # Recursively sanitize dictionary values
        sanitized_dict = {}
        for k, v in value.items():
            sanitized_value = sanitize_metadata_value(v)
            if sanitized_value is not None:
                sanitized_dict[str(k)] = sanitized_value
        return sanitized_dict if sanitized_dict else None
    else:
        # Convert other types to string, but avoid complex objects
        try:
            str_value = str(value)
            # Skip if it looks like a complex object representation
            if str_value.startswith("<") or "object at 0x" in str_value:
                return None
            return str_value
        except Exception:
            return None


def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize metadata to only include ChromaDB-compatible types.

    Args:
        metadata: Raw metadata dictionary

    Returns:
        Sanitized metadata dictionary with only primitive types
    """
    sanitized = {}

    for key, value in metadata.items():
        sanitized_value = sanitize_metadata_value(value)
        if sanitized_value is not None:
            sanitized[str(key)] = sanitized_value
        else:
            logger.debug(
                f"Skipping complex metadata field '{key}' of type {type(value)}"
            )

    return sanitized


@celery.task(bind=True)
def process_document_task(self, file_path: str) -> Dict[str, Any]:
    """
    Process document asynchronously following Clean Architecture principles.

    Args:
        file_path: Path to the uploaded document

    Returns:
        Processing result with status and details
    """
    try:
        logger.info(f"Starting document processing for: {file_path}")

        # Update task state to PROGRESS
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 4, "status": "Initializing services..."},
        )

        # Initialize services following Clean Architecture
        document_service = DocumentService()
        embedding_service = EmbeddingService()
        vector_store_repository = VectorStoreRepository()

        # Extract document ID from file path
        document_id = Path(file_path).stem
        logger.info(f"Processing document with ID: {document_id}")

        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"current": 1, "total": 4, "status": "Processing document..."},
        )

        # Use the correct method name from DocumentService
        # Based on the original error, it should be load_and_chunk_documents
        chunks = document_service.load_and_chunk_documents([file_path])
        logger.info(f"Document processed into {len(chunks)} chunks")

        # Check if we got any chunks
        if not chunks:
            error_msg = f"No content could be extracted from document: {file_path}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg, "file_path": file_path}

        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={
                "current": 2,
                "total": 4,
                "status": f"Generating embeddings for {len(chunks)} chunks...",
            },
        )

        # Extract texts and prepare data following Clean Architecture
        texts = [chunk.text for chunk in chunks]
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]

        # Create clean metadata dictionaries - only primitive types
        metadatas: List[Dict[str, Any]] = []
        for i, chunk in enumerate(chunks):
            # Start with basic, known-safe metadata
            base_metadata = {
                "document_id": document_id,
                "chunk_index": i,
                "source": file_path,
                "file_type": Path(file_path).suffix.lower(),
                "text_length": len(chunk.text),
            }

            # Don't try to access chunk metadata since it contains complex objects
            # Keep metadata simple and safe for ChromaDB
            metadatas.append(base_metadata)

        # Generate embeddings using the service layer
        logger.info("Starting embedding generation...")
        try:
            embeddings = embedding_service.generate_embeddings(texts)
        except Exception as e:
            logger.error(f"Failed to generate embeddings for chunks: {str(e)}")
            # Retry the task with exponential backoff
            raise self.retry(
                countdown=60 * (2**self.request.retries), max_retries=3, exc=e
            )

        # Verify we have embeddings
        if not embeddings or len(embeddings) != len(texts):
            error_msg = f"Failed to generate embeddings for all chunks. Expected {len(texts)}, got {len(embeddings)}"
            logger.error(error_msg)
            return {"status": "error", "error": error_msg, "file_path": file_path}

        logger.info(f"Generated {len(embeddings)} embeddings successfully")

        # Update progress
        self.update_state(
            state="PROGRESS",
            meta={"current": 3, "total": 4, "status": "Storing in vector database..."},
        )

        # Final validation before storing
        logger.info("Validating data before storage...")
        logger.info(f"IDs count: {len(ids)}")
        logger.info(f"Texts count: {len(texts)}")
        logger.info(f"Metadatas count: {len(metadatas)}")
        logger.info(f"Embeddings count: {len(embeddings)}")

        # Sample metadata validation
        if metadatas:
            sample_metadata = metadatas[0]
            logger.info(f"Sample metadata keys: {list(sample_metadata.keys())}")
            for key, value in sample_metadata.items():
                logger.info(f"  {key}: {type(value)} = {value}")

        # Store in vector database through repository layer
        vector_store_repository.add_documents(ids, texts, metadatas, embeddings)
        logger.info("Documents stored in vector database successfully")

        # Final result
        result = {
            "status": "success",
            "document_id": document_id,
            "chunks_processed": len(chunks),
            "file_path": file_path,
            "embeddings_generated": len(embeddings),
        }

        logger.info(f"Document processing completed successfully: {result}")
        return result

    except Exception as e:
        # Log the full error with traceback
        logger.exception(f"Failed to process document {file_path}: {str(e)}")

        # Return error status
        error_result = {"status": "error", "error": str(e), "file_path": file_path}

        # Update task state to FAILURE
        self.update_state(state="FAILURE", meta=error_result)

        return error_result
