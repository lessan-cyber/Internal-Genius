from typing import List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from . import EmbeddingService, GenerationService
from repositories import VectorStoreRepository


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: The user's question.
        embedding: The embedding of the user's question.
        documents: The retrieved documents.
        response: The generated response.
    """

    question: str
    embedding: List[float]
    documents: List[Dict[str, Any]]
    response: str


class RAGService:
    """
    A service for orchestrating the RAG pipeline using LangGraph.
    """

    def __init__(self):
        """
        Initializes the RAGService.
        """
        self.embedding_service = EmbeddingService()
        self.generation_service = GenerationService()
        self.vector_store_repository = VectorStoreRepository()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Builds the LangGraph for the RAG pipeline.

        Returns:
            The compiled LangGraph.
        """
        workflow = StateGraph(GraphState)

        # Define the nodes
        workflow.add_node("embed_query", self.embed_query)
        workflow.add_node("retrieve_documents", self.retrieve_documents)
        workflow.add_node("generate_response", self.generate_response)

        # Build the graph
        workflow.set_entry_point("embed_query")
        workflow.add_edge("embed_query", "retrieve_documents")
        workflow.add_edge("retrieve_documents", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def embed_query(self, state: GraphState) -> GraphState:
        """
        Embeds the user's question.

        Args:
            state: The current graph state.

        Returns:
            The updated graph state.
        """
        question = state["question"]
        embedding = self.embedding_service.embed_query(question)
        return {**state, "embedding": embedding}

    def retrieve_documents(self, state: GraphState) -> GraphState:
        """
        Retrieves documents from the vector store.

        Args:
            state: The current graph state.

        Returns:
            The updated graph state.
        """
        embedding = state["embedding"]
        documents = self.vector_store_repository.query([embedding])
        return {**state, "documents": documents}

    def generate_response(self, state: GraphState) -> GraphState:
        """
        Generates a response to the user's question.

        Args:
            state: The current graph state.

        Returns:
            The updated graph state.
        """
        question = state["question"]
        documents = state["documents"]
        response = self.generation_service.generate_response(documents, question)
        return {**state, "response": response}

    def invoke(self, question: str) -> str:
        """
        Invokes the RAG pipeline with the user's question.

        Args:
            question: The user's question.

        Returns:
            The generated response.
        """
        result = self.graph.invoke({"question": question})
        return result["response"]
