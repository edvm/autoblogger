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

# This module provides a wrapper for the Tavily search API (let LLMs browse the web).
from enum import StrEnum
from typing import Protocol, Literal, Sequence, Union, runtime_checkable
from dataclasses import dataclass, asdict
from tavily import TavilyClient
from configs.config import TAVILY_API_KEY
from configs.logging_config import logger


class SearchDepth(StrEnum):
    """Enum for search depth options."""

    BASIC = "basic"
    ADVANCED = "advanced"


class SearchTopic(StrEnum):
    """Enum for search topic options."""

    GENERAL = "general"
    NEWS = "news"
    FINANCE = "finance"


class TimeRange(StrEnum):
    """Enum for time range options."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class AnswerType(StrEnum):
    """Enum for answer type options."""

    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"


class ContentType(StrEnum):
    """Enum for content type options."""

    NONE = "none"
    MARKDOWN = "markdown"
    TEXT = "text"


@dataclass
class SearchConfig:
    """Configuration object for search parameters that can be expanded to dict."""

    search_depth: SearchDepth = SearchDepth.BASIC
    topic: SearchTopic = SearchTopic.GENERAL
    time_range: TimeRange = TimeRange.MONTH
    days: int = 7
    max_results: int = 5
    include_domains: Sequence[str] | None = None
    exclude_domains: Sequence[str] | None = None
    include_answer: AnswerType = AnswerType.NONE
    include_raw_content: ContentType = ContentType.NONE
    include_images: bool = False
    timeout: int = 60

    def to_dict(self) -> dict:
        """Convert SearchConfig to dictionary, excluding None values."""
        result = asdict(self)

        if result["include_answer"] == AnswerType.NONE:
            result["include_answer"] = False
        if result["include_raw_content"] == ContentType.NONE:
            result["include_raw_content"] = False

        # Filter out None values to let the search method use its defaults
        return {k: v for k, v in result.items() if v is not None}

    def __call__(self) -> dict:
        """Allow SearchConfig() to return dict when called."""
        return self.to_dict()


@runtime_checkable
class SearchTool(Protocol):
    """Protocol defining the interface for search tools."""

    def search(
        self,
        query: str,
        search_config: SearchConfig,
    ) -> dict:
        """Performs a search using the search tool.

        Args:
            query: The search query string
            search_config: Search configuration

        Returns:
            Dictionary containing search results with "results" key
        """
        ...


class TavilySearch(SearchTool):
    """Tavily API implementation of SearchTool protocol."""

    def __init__(self) -> None:
        self.client: TavilyClient = TavilyClient(api_key=TAVILY_API_KEY)

    def search(
        self,
        query: str,
        search_config: SearchConfig,
    ) -> dict:
        """Performs a search using the Tavily API.

        Args:
            query: The search query.
            search_depth: The depth of the search. Can be "basic" or "advanced".
            topic: The topic of the search. Can be "general", "news", or "finance".
            time_range: The time range for the search. Can be "day", "week",
                "month", or "year".
            days: The number of days to search back when time_range is not specified
                or is custom.
            max_results: The maximum number of results to return.
            include_domains: A sequence of domains to include in the search.
            exclude_domains: A sequence of domains to exclude from the search.
            include_answer: Whether to include a direct answer to the query.
                Can be True, False, "basic", or "advanced".
            include_raw_content: Whether to include raw content of the search results.
                Can be True, False, "markdown", or "text".
            include_images: Whether to include images in the search results.
            timeout: The timeout in seconds for the search request.

        Returns:
            A dictionary containing the search results from Tavily.

        Raises:
            Exception: If an error occurs during the Tavily search.
        """
        logger.info(f"Performing Tavily search for: '{query}'")
        try:
            response: dict = self.client.search(
                query=query,
                **search_config.to_dict(),
            )
            return response
        except Exception as e:
            logger.error(f"An error occurred during Tavily search: {e}")
            raise
