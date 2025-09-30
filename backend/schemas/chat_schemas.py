from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    A Pydantic schema for the chat request.
    """

    question: str


class ChatResponse(BaseModel):
    """
    A Pydantic schema for the chat response.
    """

    response: str
