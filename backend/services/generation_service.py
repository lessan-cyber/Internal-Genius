from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from settings import settings


class GenerationService:
    """
    A service for generating responses using a large language model.
    """

    def __init__(self):
        """
        Initializes the GenerationService.
        """
        with open("backend/prompts/system_prompt.md", "r") as f:
            self.system_prompt = f.read()

        self.llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL, temperature=settings.TEMPERATURE
        )
        self.prompt_template = ChatPromptTemplate.from_template(self.system_prompt)

    def generate_response(self, retrieved_docs: Dict[str, Any], question: str) -> str:
        """
        Generates a response to the user's question based on the provided context.

        Args:
            retrieved_docs: The retrieved documents from the vector store.
            question: The user's question.

        Returns:
            The generated response.
        """

        context = ""
        for i in range(len(retrieved_docs["ids"][0])):
            source = retrieved_docs["metadatas"][0][i]["source"]
            chunk_id = retrieved_docs["ids"][0][i]
            text = retrieved_docs["documents"][0][i]
            context += f"[Source: {source}, chunk_id: {chunk_id}]\n{text}\n\n"

        chain = self.prompt_template | self.llm
        response = chain.invoke({"context": context, "question": question})
        return response.content
