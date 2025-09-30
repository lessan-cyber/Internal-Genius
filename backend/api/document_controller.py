from pathlib import Path
from fastapi import APIRouter, UploadFile, File, status
from schemas.chat_schemas import ChatRequest, ChatResponse
from services.rag_service import RAGService
from utils import validate_document_type, get_supported_extensions

# from ..celery_worker import process_document_task
from schemas.upload_schemas import UploadResponse
from celery_worker import process_document_task

router = APIRouter()
rag_service = RAGService()
# Use the mounted data directory for uploads
UPLOAD_DIR = Path("/data")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/upload", status_code=status.HTTP_202_ACCEPTED, response_model=UploadResponse
)
async def upload_document(file: UploadFile = File(...)):
    """
    An endpoint to upload a document.

    Args:
        file: The file to upload.

    Returns:
        A response with the task ID and the filename.
    """
    await validate_document_type(file.filename)
    # Create a safe file path using the uploads directory
    file_path = UPLOAD_DIR / file.filename

    # Write the uploaded file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Start the background task to process the document
    task = process_document_task.delay(str(file_path))
    return {"task_id": task.id, "filename": file.filename}


@router.post("/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    """
    An endpoint to chat with the document.

    Args:
        request: The chat request with the user's question.

    Returns:
        A response with the generated answer.
    """
    response = rag_service.invoke(request.question)
    return {"response": response}
