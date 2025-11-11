"""Tests for core Ragi class."""

import os
from unittest.mock import MagicMock, patch

import pytest

from ragi import Ragi
from ragi.types import Answer, Citation


@pytest.fixture
def mock_embeddings():
    """Mock embedding responses."""
    return [[0.1] * 4096]  # nvidia/llama-embed-nemotron-8b dimension


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return "This is a test answer based on the provided context."


class TestRagiInit:
    """Tests for Ragi initialization."""

    def test_init_without_sources(self, temp_dir):
        """Test initialization without sources."""
        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)

        assert kb.store.count() == 0

    @patch("ragi.retrieval.OpenAI")
    def test_init_with_config(self, mock_openai, temp_dir):
        """Test initialization with custom config."""
        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(
            persist_dir=persist_dir,
            config={"llm": {"model": "gpt-4", "api_key": "custom-key"}}
        )

        # Verify OpenAI was initialized
        mock_openai.assert_called()


class TestRagiAdd:
    """Tests for adding documents."""

    @patch("ragi.embeddings.SentenceTransformer")
    def test_add_single_file(self, mock_model, temp_dir, sample_text_file, mock_embeddings):
        """Test adding a single file."""
        # Mock embedding generation
        mock_instance = MagicMock()
        import numpy as np
        mock_instance.encode_document.return_value = np.array(mock_embeddings)
        mock_model.return_value = mock_instance

        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        kb.add(sample_text_file)

        assert kb.count() > 0

    @patch("ragi.embeddings.SentenceTransformer")
    def test_add_multiple_files(
        self, mock_model, temp_dir, sample_text_file, sample_markdown_file, mock_embeddings
    ):
        """Test adding multiple files."""
        # Mock embedding generation
        mock_instance = MagicMock()
        import numpy as np
        mock_instance.encode_document.return_value = np.array(mock_embeddings)
        mock_model.return_value = mock_instance

        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        kb.add([sample_text_file, sample_markdown_file])

        assert kb.count() > 0

    @patch("ragi.embeddings.SentenceTransformer")
    def test_add_returns_self(self, mock_model, temp_dir, sample_text_file, mock_embeddings):
        """Test that add() returns self for chaining."""
        # Mock embedding generation
        mock_instance = MagicMock()
        import numpy as np
        mock_instance.encode_document.return_value = np.array(mock_embeddings)
        mock_model.return_value = mock_instance

        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        result = kb.add(sample_text_file)

        assert result is kb


class TestRagiQuery:
    """Tests for querying."""

    @patch("ragi.retrieval.OpenAI")
    @patch("ragi.embeddings.SentenceTransformer")
    def test_ask_question(
        self,
        mock_model,
        mock_openai,
        temp_dir,
        sample_text_file,
        mock_embeddings,
        mock_llm_response,
    ):
        """Test asking a question."""
        # Mock embedding generation
        mock_instance = MagicMock()
        import numpy as np
        mock_instance.encode_document.return_value = np.array(mock_embeddings)
        mock_instance.encode_query.return_value = np.array(mock_embeddings[0])
        mock_model.return_value = mock_instance

        # Mock OpenAI response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_llm_response))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        kb.add(sample_text_file)

        answer = kb.ask("What is this document about?")

        assert isinstance(answer, Answer)
        assert answer.text
        assert answer.query == "What is this document about?"

    @patch("ragi.retrieval.OpenAI")
    @patch("ragi.embeddings.SentenceTransformer")
    def test_callable_interface(
        self,
        mock_model,
        mock_openai,
        temp_dir,
        sample_text_file,
        mock_embeddings,
        mock_llm_response,
    ):
        """Test using Ragi as callable."""
        # Mock embedding generation
        mock_instance = MagicMock()
        import numpy as np
        mock_instance.encode_document.return_value = np.array(mock_embeddings)
        mock_instance.encode_query.return_value = np.array(mock_embeddings[0])
        mock_model.return_value = mock_instance

        # Mock LLM response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_llm_response))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        kb.add(sample_text_file)

        answer = kb("What is this?")

        assert isinstance(answer, Answer)


class TestRagiFilter:
    """Tests for metadata filtering."""

    def test_filter_returns_self(self, temp_dir):
        """Test that filter() returns self for chaining."""
        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        result = kb.filter(type="test")

        assert result is kb

    @patch("ragi.retrieval.OpenAI")
    @patch("ragi.embeddings.SentenceTransformer")
    def test_filter_chaining(
        self,
        mock_model,
        mock_openai,
        temp_dir,
        sample_text_file,
        mock_embeddings,
        mock_llm_response,
    ):
        """Test filter chaining with ask."""
        # Mock embedding generation
        mock_instance = MagicMock()
        import numpy as np
        mock_instance.encode_document.return_value = np.array(mock_embeddings)
        mock_instance.encode_query.return_value = np.array(mock_embeddings[0])
        mock_model.return_value = mock_instance

        # Mock LLM response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=mock_llm_response))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client

        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        kb.add(sample_text_file)

        answer = kb.filter(type="test").ask("What is this?")

        assert isinstance(answer, Answer)


class TestRagiUtility:
    """Tests for utility methods."""

    def test_count_empty(self, temp_dir):
        """Test count on empty store."""
        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)

        assert kb.count() == 0

    @patch("ragi.embeddings.OpenAI")
    def test_clear(self, mock_openai, temp_dir, sample_text_file, mock_embeddings):
        """Test clearing the knowledge base."""
        # Mock embedding generation
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embeddings[0])]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        persist_dir = os.path.join(temp_dir, "test_ragi")
        kb = Ragi(persist_dir=persist_dir)
        kb.add(sample_text_file)

        assert kb.count() > 0

        kb.clear()
        assert kb.count() == 0
