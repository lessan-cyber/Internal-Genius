import pytest
from unittest.mock import MagicMock
from services.reranking_service import RerankingService


@pytest.fixture
def mocked_cross_encoder(mocker):
    """
    Fixture to mock the CrossEncoder model.
    """
    mock_model = MagicMock()
    mocker.patch("services.reranking_service.CrossEncoder", return_value=mock_model)
    return mock_model


def test_rerank_documents(mocked_cross_encoder):
    """
    Tests that the rerank_documents method correctly re-ranks documents.
    """
    # Arrange
    reranking_service = RerankingService()
    query = "What is the capital of France?"
    retrieved_docs = {
        "ids": [["1", "2", "3"]],
        "documents": [
            [
                "Paris is the capital of France.",
                "London is a big city.",
                "Berlin is in Germany.",
            ]
        ],
        "metadatas": [
            [{"source": "doc1"}, {"source": "doc2"}, {"source": "doc3"}]
        ],
    }
    # Mock the scores from the cross-encoder
    mocked_cross_encoder.predict.return_value = [0.9, 0.1, 0.5]

    # Act
    reranked_docs = reranking_service.rerank_documents(query, retrieved_docs)

    # Assert
    # The expected order is doc1, doc3, doc2
    expected_order_ids = ["1", "3", "2"]
    expected_order_docs = [
        "Paris is the capital of France.",
        "Berlin is in Germany.",
        "London is a big city.",
    ]
    expected_order_metadatas = [
        {"source": "doc1"},
        {"source": "doc3"},
        {"source": "doc2"},
    ]

    assert reranked_docs["ids"][0] == expected_order_ids
    assert reranked_docs["documents"][0] == expected_order_docs
    assert reranked_docs["metadatas"][0] == expected_order_metadatas
    mocked_cross_encoder.predict.assert_called_once_with(
        [
            ["What is the capital of France?", "Paris is the capital of France."],
            ["What is the capital of France?", "London is a big city."],
            ["What is the capital of France?", "Berlin is in Germany."],
        ]
    )


def test_rerank_documents_empty_input(mocked_cross_encoder):
    """
    Tests that the rerank_documents method handles empty input correctly.
    """
    # Arrange
    reranking_service = RerankingService()
    query = "What is the capital of France?"
    retrieved_docs = {"ids": [[]], "documents": [[]], "metadatas": [[]]}

    # Act
    reranked_docs = reranking_service.rerank_documents(query, retrieved_docs)

    # Assert
    assert reranked_docs == retrieved_docs


def test_reranking_service_model_loading():
    """
    Tests that the RerankingService can be initialized with the correct model.
    """
    try:
        RerankingService()
    except Exception as e:
        pytest.fail(f"Failed to initialize RerankingService: {e}")
