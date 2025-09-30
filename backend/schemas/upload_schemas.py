from pydantic import BaseModel

class UploadResponse(BaseModel):
    """
    A Pydantic schema for the upload response.
    """
    task_id: str
    filename: str
