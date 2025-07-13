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

import json

import pytest

from agents.research_agent import ResearchAgent
from core.exceptions import ErrorConstants
from tools.search import SearchConfig

"""Tests for ResearchAgent."""


class TestResearchAgent:
    """Test cases for ResearchAgent."""

    def test_research_agent_initialization(
        self, mock_llm_service, mock_search_tool, search_config
    ):
        """Test ResearchAgent initialization."""
        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        assert agent.llm_service == mock_llm_service
        assert agent.search_tool == mock_search_tool
        assert agent.search_config == search_config
        assert (
            agent.research_system_message
            == ResearchAgent.DEFAULT_RESEARCH_SYSTEM_MESSAGE
        )

    def test_research_agent_custom_system_message(
        self, mock_llm_service, mock_search_tool, search_config, mocker
    ):
        """Test ResearchAgent with custom system message."""
        custom_message = "Custom research system message"
        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
            research_system_message=custom_message,
        )

        assert agent.research_system_message == custom_message

    def test_successful_research_execution(self, basic_workflow_state, mocker):
        """Test successful research execution."""
        # Create mock services with specific responses
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {
            "results": [
                {
                    "url": "https://example.com/article1",
                    "content": "AI is transforming industries rapidly.",
                    "title": "AI Revolution",
                },
                {
                    "url": "https://example.com/article2",
                    "content": "Machine learning adoption is growing.",
                    "title": "ML Growth",
                },
            ]
        }

        mock_llm_service = mocker.Mock()
        research_brief = {
            "main_points": ["AI transformation", "ML growth"],
            "statistics": ["80% adoption rate"],
            "quotes": ["AI will change everything"],
            "counter_arguments": ["Privacy concerns"],
        }
        mock_llm_service.generate_response.return_value.content = json.dumps(
            research_brief
        )
        mock_llm_service.generate_response.return_value.usage.total_tokens = 100

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=SearchConfig(),
        )

        result_state = agent.execute(basic_workflow_state)

        # Verify search was called
        mock_search_tool.search.assert_called_once_with(
            basic_workflow_state.initial_topic, agent.search_config
        )

        # Verify LLM was called
        mock_llm_service.generate_response.assert_called_once()

        # Verify state updates
        assert result_state.status == "RESEARCHING"
        assert result_state.research_brief == research_brief
        assert len(result_state.sources) == 2
        assert "https://example.com/article1" in result_state.sources
        assert "https://example.com/article2" in result_state.sources

        # Verify log entries
        assert len(result_state.run_log) > 0
        assert any("Research Agent: Started" in entry for entry in result_state.run_log)
        assert any("Brief created" in entry for entry in result_state.run_log)

    def test_research_no_search_results(
        self, basic_workflow_state, mock_llm_service, search_config, mocker
    ):
        """Test research when search returns no results."""
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {"results": []}

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        result_state = agent.execute(basic_workflow_state)

        # Should handle no content gracefully
        assert result_state.research_brief == {
            "error": "No content found from search results."
        }
        assert result_state.sources == []

        # Should have warning log entry
        assert any(
            "found no content from search results" in entry
            for entry in result_state.run_log
        )

        # LLM should not have been called
        mock_llm_service.generate_response.assert_not_called()

    def test_research_empty_content_results(
        self, basic_workflow_state, mock_llm_service, search_config, mocker
    ):
        """Test research when search returns results without content."""
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {
            "results": [
                {"url": "https://example.com/article1", "title": "Article 1"},
                {"url": "https://example.com/article2", "title": "Article 2"},
            ]
        }

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        result_state = agent.execute(basic_workflow_state)

        # Should handle no content gracefully (no content field in results)
        assert result_state.research_brief == {
            "error": "No content found from search results."
        }
        assert result_state.sources == [
            "https://example.com/article1",
            "https://example.com/article2",
        ]

    def test_research_llm_error_flag(self, basic_workflow_state, search_config, mocker):
        """Test research when LLM returns error flag."""
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {
            "results": [{"url": "https://example.com/test", "content": "Test content"}]
        }

        mock_llm_service = mocker.Mock()
        mock_llm_service.generate_response.return_value.content = (
            ErrorConstants.LLM_NO_RESPONSE
        )
        mock_llm_service.generate_response.return_value.usage = None

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        result_state = agent.execute(basic_workflow_state)

        # Should handle LLM error gracefully
        assert result_state.research_brief == {
            "error": "LLM query failed to produce content."
        }
        assert any(
            "received error from LLM query" in entry for entry in result_state.run_log
        )

    def test_research_json_parse_error(
        self, basic_workflow_state, search_config, mocker
    ):
        """Test research when LLM returns invalid JSON."""
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {
            "results": [{"url": "https://example.com/test", "content": "Test content"}]
        }

        mock_llm_service = mocker.Mock()
        invalid_json = "This is not valid JSON"
        mock_llm_service.generate_response.return_value.content = invalid_json
        mock_llm_service.generate_response.return_value.usage = None

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        result_state = agent.execute(basic_workflow_state)

        # Should handle JSON parse error gracefully
        assert result_state.research_brief == {
            "raw_content": invalid_json,
            "parse_error": True,
        }
        assert any(
            "failed to parse LLM response into JSON" in entry
            for entry in result_state.run_log
        )

    def test_research_llm_exception(self, basic_workflow_state, search_config, mocker):
        """Test research when LLM service raises exception."""
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {
            "results": [{"url": "https://example.com/test", "content": "Test content"}]
        }

        mock_llm_service = mocker.Mock()
        mock_llm_service.generate_response.side_effect = Exception("LLM service error")

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        with pytest.raises(Exception) as exc_info:
            agent.execute(basic_workflow_state)

        assert "LLM service error" in str(exc_info.value)

    def test_research_prompt_construction(
        self, basic_workflow_state, search_config, mocker
    ):
        """Test that research prompt is properly constructed."""
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {
            "results": [
                {"url": "https://example.com/test", "content": "Test content about AI"}
            ]
        }

        mock_llm_service = mocker.Mock()
        mock_llm_service.generate_response.return_value.content = '{"test": "response"}'
        mock_llm_service.generate_response.return_value.usage = None

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        agent.execute(basic_workflow_state)

        # Check that LLM was called with correct parameters
        call_args = mock_llm_service.generate_response.call_args
        prompt = call_args[1]["prompt"]
        system_message = call_args[1]["system_message"]

        # Verify prompt contains topic and context
        assert basic_workflow_state.initial_topic in prompt
        assert "Test content about AI" in prompt
        assert "--- CONTEXT ---" in prompt
        assert "--- END CONTEXT ---" in prompt

        # Verify system message
        assert system_message == ResearchAgent.DEFAULT_RESEARCH_SYSTEM_MESSAGE

    def test_research_sources_extraction(
        self, basic_workflow_state, mock_llm_service, search_config, mocker
    ):
        """Test that sources are correctly extracted from search results."""
        mock_search_tool = mocker.Mock()
        mock_search_tool.search.return_value = {
            "results": [
                {"url": "https://example.com/article1", "content": "Content 1"},
                {"title": "Article without URL", "content": "Content 2"},  # No URL
                {"url": "https://example.com/article3", "content": "Content 3"},
                {"url": "https://example.com/article4"},  # No content
            ]
        }

        mock_llm_service.generate_response.return_value.content = '{"test": "response"}'
        mock_llm_service.generate_response.return_value.usage = None

        agent = ResearchAgent(
            llm_service=mock_llm_service,
            search_tool=mock_search_tool,
            search_config=search_config,
        )

        result_state = agent.execute(basic_workflow_state)

        # Should extract URLs from all results that have them
        expected_sources = [
            "https://example.com/article1",
            "https://example.com/article3",
            "https://example.com/article4",
        ]
        assert result_state.sources == expected_sources
