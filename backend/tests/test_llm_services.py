"""
Autoblogger - Generate content on demand using online data in real time.
Copyright (C) 2025  Emiliano Dalla Verde Marcozzi <edvm.inbox@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""Tests for LLM services."""

import pytest
from core.llm_services import (
    LLMService,
    LLMServiceResponse,
    LLMUsage,
    LLMServiceException,
    OpenAIService,
    query_llm,
)
from core.state import WorkflowState


class TestLLMUsage:
    """Test cases for LLMUsage."""

    def test_llm_usage_creation(self):
        """Test LLMUsage creation."""
        usage = LLMUsage(total_tokens=100)
        assert usage.total_tokens == 100

    def test_llm_usage_string_representation(self):
        """Test LLMUsage string representation."""
        usage = LLMUsage(total_tokens=150)
        assert str(usage) == "LLMUsage(total_tokens=150)"


class TestLLMServiceResponse:
    """Test cases for LLMServiceResponse."""

    def test_response_creation_with_usage(self):
        """Test LLMServiceResponse creation with usage."""
        usage = LLMUsage(total_tokens=100)
        response = LLMServiceResponse(content="Test content", usage=usage)

        assert response.content == "Test content"
        assert response.usage == usage

    def test_response_creation_without_usage(self):
        """Test LLMServiceResponse creation without usage."""
        response = LLMServiceResponse(content="Test content")

        assert response.content == "Test content"
        assert response.usage is None

    def test_response_string_representation(self):
        """Test LLMServiceResponse string representation."""
        usage = LLMUsage(total_tokens=100)
        response = LLMServiceResponse(content="Test", usage=usage)

        expected = "LLMServiceResponse(content=Test, usage=LLMUsage(total_tokens=100))"
        assert str(response) == expected


class TestLLMServiceException:
    """Test cases for LLMServiceException."""

    def test_exception_creation(self):
        """Test LLMServiceException creation."""
        exception = LLMServiceException("Test error")
        assert exception.message == "Test error"
        assert str(exception) == "LLMServiceException: Test error"


class TestOpenAIService:
    """Test cases for OpenAIService."""

    def test_openai_service_initialization(self):
        """Test OpenAIService initialization."""
        service = OpenAIService(api_key="test-key")
        assert service.client is not None

    def test_generate_response_success(self, mocker):
        """Test successful response generation."""
        # Mock the OpenAI client and response
        mock_client = mocker.Mock()
        mock_openai_class = mocker.patch("openai.OpenAI", return_value=mock_client)

        mock_response = mocker.Mock()
        mock_response.choices = [mocker.Mock()]
        mock_response.choices[0].message.content = "Generated content"
        mock_response.usage.total_tokens = 150

        mock_client.chat.completions.create.return_value = mock_response

        service = OpenAIService(api_key="test-key")

        result = service.generate_response(
            prompt="Test prompt",
            system_message="Test system message",
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1000,
        )

        assert result.content == "Generated content"
        assert result.usage.total_tokens == 150

        # Verify the client was called correctly
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Test system message"},
                {"role": "user", "content": "Test prompt"},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

    def test_generate_response_no_usage(self, mocker):
        """Test response generation when usage is not available."""
        mock_client = mocker.Mock()
        mocker.patch("openai.OpenAI", return_value=mock_client)

        mock_response = mocker.Mock()
        mock_response.choices = [mocker.Mock()]
        mock_response.choices[0].message.content = "Generated content"
        mock_response.usage = None

        mock_client.chat.completions.create.return_value = mock_response

        service = OpenAIService(api_key="test-key")

        result = service.generate_response(
            prompt="Test prompt",
            system_message="Test system message",
            model="gpt-3.5-turbo",
        )

        assert result.content == "Generated content"
        assert result.usage is None

    def test_generate_response_api_error(self, mocker):
        """Test response generation when API call fails."""
        mock_client = mocker.Mock()
        mocker.patch("openai.OpenAI", return_value=mock_client)

        mock_client.chat.completions.create.side_effect = Exception("API Error")

        service = OpenAIService(api_key="test-key")

        with pytest.raises(LLMServiceException) as exc_info:
            service.generate_response(
                prompt="Test prompt",
                system_message="Test system message",
                model="gpt-3.5-turbo",
            )

        assert "Error querying OpenAI API: API Error" in str(exc_info.value)


class TestQueryLLM:
    """Test cases for query_llm function."""

    def test_query_llm_success(self, mocker):
        """Test successful LLM query."""
        mock_service = mocker.Mock(spec=LLMService)
        mock_usage = LLMUsage(total_tokens=100)
        mock_response = LLMServiceResponse(
            content="  Generated content  ", usage=mock_usage
        )
        mock_service.generate_response.return_value = mock_response

        state = WorkflowState(initial_topic="Test topic")

        result = query_llm(
            llm_service=mock_service,
            state=state,
            prompt="Test prompt",
            system_message="Test system message",
            model="gpt-3.5-turbo",
            temperature=0.8,
            max_tokens=2000,
        )

        assert result == "Generated content"  # Should be stripped

        # Verify service was called correctly
        mock_service.generate_response.assert_called_once_with(
            prompt="Test prompt",
            system_message="Test system message",
            model="gpt-3.5-turbo",
            temperature=0.8,
            max_tokens=2000,
        )

        # Verify state was updated with log entries
        assert len(state.run_log) == 2
        assert "Contacting LLM with model: gpt-3.5-turbo" in state.run_log[0]
        assert "Used 100 tokens" in state.run_log[1]

    def test_query_llm_empty_content(self, mocker):
        """Test LLM query returning empty content."""
        mock_service = mocker.Mock(spec=LLMService)
        mock_response = LLMServiceResponse(content="", usage=None)
        mock_service.generate_response.return_value = mock_response

        state = WorkflowState(initial_topic="Test topic")

        result = query_llm(
            llm_service=mock_service,
            state=state,
            prompt="Test prompt",
            system_message="Test system message",
            model="gpt-3.5-turbo",
        )

        assert result == "fucked up"  # ERROR_FLAG value

        # Verify warning was logged
        assert len(state.run_log) == 2
        assert "Warning: LLM returned no content" in state.run_log[1]

    def test_query_llm_none_content(self, mocker):
        """Test LLM query returning None content."""
        mock_service = mocker.Mock(spec=LLMService)
        mock_response = LLMServiceResponse(content=None, usage=None)
        mock_service.generate_response.return_value = mock_response

        state = WorkflowState(initial_topic="Test topic")

        result = query_llm(
            llm_service=mock_service,
            state=state,
            prompt="Test prompt",
            system_message="Test system message",
            model="gpt-3.5-turbo",
        )

        assert result == "fucked up"  # ERROR_FLAG value

    def test_query_llm_no_usage_info(self, mocker):
        """Test LLM query without usage information."""
        mock_service = mocker.Mock(spec=LLMService)
        mock_response = LLMServiceResponse(content="Generated content", usage=None)
        mock_service.generate_response.return_value = mock_response

        state = WorkflowState(initial_topic="Test topic")

        result = query_llm(
            llm_service=mock_service,
            state=state,
            prompt="Test prompt",
            system_message="Test system message",
            model="gpt-3.5-turbo",
        )

        assert result == "Generated content"

        # Should only have one log entry (no usage log)
        assert len(state.run_log) == 1
        assert "Contacting LLM with model: gpt-3.5-turbo" in state.run_log[0]

    def test_query_llm_service_exception(self, mocker):
        """Test LLM query when service raises exception."""
        mock_service = mocker.Mock(spec=LLMService)
        mock_service.generate_response.side_effect = LLMServiceException(
            "Service error"
        )

        state = WorkflowState(initial_topic="Test topic")

        with pytest.raises(LLMServiceException):
            query_llm(
                llm_service=mock_service,
                state=state,
                prompt="Test prompt",
                system_message="Test system message",
                model="gpt-3.5-turbo",
            )

        # Should have log entries including the error
        assert len(state.run_log) == 2
        assert "Error: LLM query failed" in state.run_log[1]
