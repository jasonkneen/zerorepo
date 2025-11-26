"""
Unit tests for LLM Client.
Tests LLM communication, response handling, and error cases.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from zerorepo.tools.llm_client import LLMClient, LLMResponse


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_create_success_response(self):
        """Test creating successful response."""
        response = LLMResponse(
            content="Test content",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            success=True
        )
        assert response.content == "Test content"
        assert response.model == "gpt-4"
        assert response.success is True
        assert response.error is None

    def test_create_error_response(self):
        """Test creating error response."""
        response = LLMResponse(
            content="",
            model="gpt-4",
            usage={},
            success=False,
            error="Rate limit exceeded"
        )
        assert response.content == ""
        assert response.success is False
        assert response.error == "Rate limit exceeded"

    def test_response_usage_structure(self):
        """Test usage information structure."""
        response = LLMResponse(
            content="test",
            model="gpt-4o-mini",
            usage={
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            },
            success=True
        )
        assert response.usage["prompt_tokens"] == 100
        assert response.usage["completion_tokens"] == 50
        assert response.usage["total_tokens"] == 150


class TestLLMClientInit:
    """Tests for LLMClient initialization."""

    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    def test_init_with_api_key(self, mock_openai):
        """Test initialization with API key."""
        client = LLMClient(api_key="test-key", default_model="gpt-4o-mini")

        assert client.default_model == "gpt-4o-mini"
        mock_openai.assert_called_once_with(api_key="test-key")

    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    def test_init_default_model(self, mock_openai):
        """Test initialization with default model."""
        client = LLMClient(api_key="test-key")

        assert client.default_model == "gpt-4o-mini"


class TestLLMClientGenerate:
    """Tests for LLMClient.generate method."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create mock OpenAI client."""
        mock = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Generated text"))]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock.chat.completions.create = AsyncMock(return_value=mock_completion)
        return mock

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_success(self, mock_openai_class, mock_openai_client):
        """Test successful text generation."""
        mock_openai_class.return_value = mock_openai_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(prompt="Test prompt")

        assert response.success is True
        assert response.content == "Generated text"
        assert response.usage["prompt_tokens"] == 10

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_with_custom_parameters(self, mock_openai_class, mock_openai_client):
        """Test generation with custom parameters."""
        mock_openai_class.return_value = mock_openai_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(
            prompt="Test prompt",
            model="gpt-4",
            temperature=0.5,
            max_tokens=500,
            system_prompt="You are a helpful assistant"
        )

        assert response.success is True
        # Verify the API was called with correct parameters
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-4"
        assert call_args.kwargs["temperature"] == 0.5
        assert call_args.kwargs["max_tokens"] == 500

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_api_error(self, mock_openai_class):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(prompt="Test prompt")

        assert response.success is False
        assert "API Error" in response.error

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_empty_response(self, mock_openai_class):
        """Test handling of empty response."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=""))]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=0,
            total_tokens=10
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(prompt="Test prompt")

        assert response.success is True
        assert response.content == ""

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_none_content(self, mock_openai_class):
        """Test handling of None content in response."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=None))]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=0,
            total_tokens=10
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(prompt="Test prompt")

        assert response.success is True
        assert response.content == ""


class TestLLMClientGenerateJSON:
    """Tests for LLMClient.generate_json method."""

    @pytest.fixture
    def mock_json_response(self):
        """Create mock response with JSON content."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(
            message=MagicMock(content='{"key": "value", "number": 42}')
        )]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        return mock_client

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_json_success(self, mock_openai_class, mock_json_response):
        """Test successful JSON generation."""
        mock_openai_class.return_value = mock_json_response

        client = LLMClient(api_key="test-key")
        result = await client.generate_json(prompt="Generate JSON")

        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["number"] == 42

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_json_with_markdown_fencing(self, mock_openai_class):
        """Test JSON extraction from markdown code block."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        # Response with markdown fencing
        mock_completion.choices = [MagicMock(
            message=MagicMock(content='```json\n{"key": "value"}\n```')
        )]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        result = await client.generate_json(prompt="Generate JSON")

        assert result["key"] == "value"

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_json_invalid_json(self, mock_openai_class):
        """Test handling of invalid JSON response."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(
            message=MagicMock(content='This is not valid JSON')
        )]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")

        with pytest.raises(Exception) as exc_info:
            await client.generate_json(prompt="Generate JSON")

        assert "Invalid JSON" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_json_api_failure(self, mock_openai_class):
        """Test handling of API failure in JSON generation."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(
            message=MagicMock(content='')
        )]
        mock_completion.usage = None
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")

        with pytest.raises(Exception) as exc_info:
            await client.generate_json(prompt="Generate JSON")

        assert "failed" in str(exc_info.value).lower() or "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_generate_json_with_schema(self, mock_openai_class, mock_json_response):
        """Test JSON generation with schema parameter."""
        mock_openai_class.return_value = mock_json_response

        client = LLMClient(api_key="test-key")
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}

        result = await client.generate_json(prompt="Generate JSON", schema=schema)

        # Schema validation is currently a no-op, but method should complete
        assert isinstance(result, dict)


class TestLLMClientValidateJsonSchema:
    """Tests for JSON schema validation helper."""

    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    def test_validate_json_schema_returns_true(self, mock_openai_class):
        """Test that schema validation returns True (placeholder implementation)."""
        client = LLMClient(api_key="test-key")

        # Current implementation always returns True
        result = client._validate_json_schema(
            data={"key": "value"},
            schema={"type": "object"}
        )

        assert result is True


class TestLLMClientEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_very_long_prompt(self, mock_openai_class):
        """Test handling of very long prompts."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_completion.usage = MagicMock(
            prompt_tokens=10000,
            completion_tokens=20,
            total_tokens=10020
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        long_prompt = "Test " * 5000  # Very long prompt

        response = await client.generate(prompt=long_prompt)

        assert response.success is True

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_unicode_content(self, mock_openai_class):
        """Test handling of unicode content."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(
            message=MagicMock(content="Hello! Unicode: \u4e2d\u6587, \u65e5\u672c\u8a9e")
        )]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(prompt="Test unicode")

        assert response.success is True
        assert "\u4e2d\u6587" in response.content

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_special_characters_in_prompt(self, mock_openai_class):
        """Test handling of special characters in prompt."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        special_prompt = "Test with special chars: <>\"'&\n\t"

        response = await client.generate(prompt=special_prompt)

        assert response.success is True

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_code_in_response(self, mock_openai_class):
        """Test handling of code blocks in response."""
        mock_client = MagicMock()
        code_response = '''```python
def hello():
    print("Hello, World!")
```'''
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=code_response))]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=30,
            total_tokens=40
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(prompt="Write a function")

        assert response.success is True
        assert "def hello" in response.content

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_model_fallback(self, mock_openai_class):
        """Test model defaults to default_model when None."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_completion.usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key", default_model="gpt-3.5-turbo")
        response = await client.generate(prompt="Test", model=None)

        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "gpt-3.5-turbo"


class TestLLMClientIntegration:
    """Integration-style tests for LLM client behavior."""

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_typical_code_generation_workflow(self, mock_openai_class):
        """Test typical workflow for code generation."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(
            message=MagicMock(content='''```python
class Calculator:
    """A simple calculator class."""

    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b
```''')
        )]
        mock_completion.usage = MagicMock(
            prompt_tokens=50,
            completion_tokens=100,
            total_tokens=150
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        response = await client.generate(
            prompt="Generate a Calculator class with add and subtract methods",
            system_prompt="You are a Python code generation assistant",
            temperature=0.1
        )

        assert response.success is True
        assert "class Calculator" in response.content
        assert "def add" in response.content

    @pytest.mark.asyncio
    @patch('zerorepo.tools.llm_client.AsyncOpenAI')
    async def test_typical_json_workflow(self, mock_openai_class):
        """Test typical workflow for JSON generation."""
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(
            message=MagicMock(content='{"all_selected_feature_paths": ["ml/algorithms/linear", "ml/preprocessing/scaling"]}')
        )]
        mock_completion.usage = MagicMock(
            prompt_tokens=80,
            completion_tokens=40,
            total_tokens=120
        )
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai_class.return_value = mock_client

        client = LLMClient(api_key="test-key")
        result = await client.generate_json(
            prompt="Select relevant features for ML project",
            temperature=0.1
        )

        assert isinstance(result, dict)
        assert "all_selected_feature_paths" in result
        assert len(result["all_selected_feature_paths"]) == 2
