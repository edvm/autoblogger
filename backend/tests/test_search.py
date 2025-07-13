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

"""Tests for search functionality."""

from unittest.mock import Mock, patch

import pytest

from tools.search import (
    AnswerType,
    ContentType,
    SearchConfig,
    SearchDepth,
    SearchTool,
    SearchTopic,
    TavilySearch,
    TimeRange,
)


class TestSearchConfig:
    """Test cases for SearchConfig."""

    def test_default_search_config(self):
        """Test SearchConfig with default values."""
        config = SearchConfig()

        assert config.search_depth == SearchDepth.BASIC
        assert config.topic == SearchTopic.GENERAL
        assert config.time_range == TimeRange.MONTH
        assert config.days == 7
        assert config.max_results == 5
        assert config.include_domains is None
        assert config.exclude_domains is None
        assert config.include_answer == AnswerType.NONE
        assert config.include_raw_content == ContentType.NONE
        assert config.include_images is False
        assert config.timeout == 60

    def test_custom_search_config(self):
        """Test SearchConfig with custom values."""
        config = SearchConfig(
            search_depth=SearchDepth.ADVANCED,
            topic=SearchTopic.NEWS,
            time_range=TimeRange.WEEK,
            days=14,
            max_results=10,
            include_domains=["example.com", "test.com"],
            exclude_domains=["spam.com"],
            include_answer=AnswerType.BASIC,
            include_raw_content=ContentType.MARKDOWN,
            include_images=True,
            timeout=120,
        )

        assert config.search_depth == SearchDepth.ADVANCED
        assert config.topic == SearchTopic.NEWS
        assert config.time_range == TimeRange.WEEK
        assert config.days == 14
        assert config.max_results == 10
        assert config.include_domains == ["example.com", "test.com"]
        assert config.exclude_domains == ["spam.com"]
        assert config.include_answer == AnswerType.BASIC
        assert config.include_raw_content == ContentType.MARKDOWN
        assert config.include_images is True
        assert config.timeout == 120

    def test_search_config_to_dict(self):
        """Test SearchConfig conversion to dictionary."""
        config = SearchConfig(
            search_depth=SearchDepth.ADVANCED,
            max_results=8,
            include_answer=AnswerType.NONE,
            include_raw_content=ContentType.NONE,
        )

        result = config.to_dict()

        # NONE values should be converted to False
        assert result["include_answer"] is False
        assert result["include_raw_content"] is False

        # Other values should be preserved
        assert result["search_depth"] == SearchDepth.ADVANCED
        assert result["max_results"] == 8

        # None values should be filtered out
        assert "include_domains" not in result
        assert "exclude_domains" not in result

    def test_search_config_callable(self):
        """Test SearchConfig as callable returning dict."""
        config = SearchConfig(max_results=3)
        result = config()

        assert isinstance(result, dict)
        assert result["max_results"] == 3

    def test_search_config_enum_values(self):
        """Test that enum values are correctly assigned."""
        assert SearchDepth.BASIC == "basic"
        assert SearchDepth.ADVANCED == "advanced"

        assert SearchTopic.GENERAL == "general"
        assert SearchTopic.NEWS == "news"
        assert SearchTopic.FINANCE == "finance"

        assert TimeRange.DAY == "day"
        assert TimeRange.WEEK == "week"
        assert TimeRange.MONTH == "month"
        assert TimeRange.YEAR == "year"

        assert AnswerType.NONE == "none"
        assert AnswerType.BASIC == "basic"
        assert AnswerType.ADVANCED == "advanced"

        assert ContentType.NONE == "none"
        assert ContentType.MARKDOWN == "markdown"
        assert ContentType.TEXT == "text"


class TestTavilySearch:
    """Test cases for TavilySearch."""

    @patch("tools.search.TavilyClient")
    def test_tavily_search_initialization(self, mock_tavily_client):
        """Test TavilySearch initialization."""
        search = TavilySearch()

        # Should create TavilyClient with API key
        mock_tavily_client.assert_called_once()
        assert search.client is not None

    @patch("tools.search.TavilyClient")
    def test_tavily_search_success(self, mock_tavily_client):
        """Test successful Tavily search."""
        # Mock the client
        mock_client = Mock()
        mock_tavily_client.return_value = mock_client

        # Mock response
        mock_response = {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com/test",
                    "content": "Test content",
                    "score": 0.9,
                }
            ],
            "query": "test query",
            "response_time": 1.2,
        }
        mock_client.search.return_value = mock_response

        search = TavilySearch()
        config = SearchConfig(max_results=5)

        result = search.search(query="test query", search_config=config)

        assert result == mock_response

        # Verify client was called with correct parameters
        mock_client.search.assert_called_once_with(
            query="test query", **config.to_dict()
        )

    @patch("tools.search.TavilyClient")
    def test_tavily_search_with_custom_config(self, mock_tavily_client):
        """Test Tavily search with custom configuration."""
        mock_client = Mock()
        mock_tavily_client.return_value = mock_client
        mock_client.search.return_value = {"results": []}

        search = TavilySearch()
        config = SearchConfig(
            search_depth=SearchDepth.ADVANCED,
            topic=SearchTopic.NEWS,
            max_results=10,
            include_domains=["news.com"],
        )

        search.search(query="news query", search_config=config)

        # Verify the config was properly converted and passed
        expected_config = config.to_dict()
        mock_client.search.assert_called_once_with(
            query="news query", **expected_config
        )

    @patch("tools.search.TavilyClient")
    def test_tavily_search_api_error(self, mock_tavily_client):
        """Test Tavily search when API call fails."""
        mock_client = Mock()
        mock_tavily_client.return_value = mock_client
        mock_client.search.side_effect = Exception("API Error")

        search = TavilySearch()
        config = SearchConfig()

        with pytest.raises(Exception) as exc_info:
            search.search(query="test query", search_config=config)

        assert "API Error" in str(exc_info.value)

    def test_search_tool_protocol(self):
        """Test that TavilySearch implements SearchTool protocol."""
        # This is a runtime check
        assert isinstance(TavilySearch(), SearchTool)

    @patch("tools.search.TavilyClient")
    def test_tavily_search_empty_results(self, mock_tavily_client):
        """Test Tavily search returning empty results."""
        mock_client = Mock()
        mock_tavily_client.return_value = mock_client
        mock_client.search.return_value = {"results": [], "query": "empty query"}

        search = TavilySearch()
        config = SearchConfig()

        result = search.search(query="empty query", search_config=config)

        assert result["results"] == []
        assert result["query"] == "empty query"

    @patch("tools.search.TavilyClient")
    def test_tavily_search_filters_none_values(self, mock_tavily_client):
        """Test that None values are filtered out when calling Tavily API."""
        mock_client = Mock()
        mock_tavily_client.return_value = mock_client
        mock_client.search.return_value = {"results": []}

        search = TavilySearch()
        config = SearchConfig(
            max_results=5,
            include_domains=None,  # Should be filtered out
            exclude_domains=None,  # Should be filtered out
        )

        search.search(query="test", search_config=config)

        # Get the actual call arguments
        call_args = mock_client.search.call_args
        assert call_args[1]["max_results"] == 5
        assert "include_domains" not in call_args[1]
        assert "exclude_domains" not in call_args[1]
