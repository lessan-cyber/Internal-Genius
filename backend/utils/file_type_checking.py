from pathlib import Path
from typing import Set
from fastapi import HTTPException, status


# Supported file extensions
SUPPORTED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".txt", ".pptx", ".md", ".markdown"}


async def validate_document_type(filename: str) -> None:
    """
    Validate that the uploaded file has a supported extension.

    Args:
        filename: The name of the uploaded file

    Raises:
        HTTPException: If the file type is not supported
    """
    file_path = Path(filename)
    file_extension = file_path.suffix.lower()

    if not file_extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have an extension",
        )

    if file_extension not in SUPPORTED_EXTENSIONS:
        supported_types = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{file_extension}'. "
            f"Supported types: {supported_types}",
        )


def get_supported_extensions() -> Set[str]:
    """
    Get the set of supported file extensions.

    Returns:
        Set of supported file extensions
    """
    return SUPPORTED_EXTENSIONS.copy()
