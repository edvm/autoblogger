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
from .base_agent import AbstractAgent
from core.state import WorkflowState
from core.llm_services import LLMService, query_llm
from core.exceptions import ErrorConstants
from tools.search import SearchTool, SearchConfig
from configs.config import FAST_LLM_MODEL
from configs.logging_config import logger


class ResearchAgent(AbstractAgent):
    """
    Agent responsible for conducting research and creating a brief.
    It can be customized by providing specific tools, LLM services,
    and parameters for search and summarization.
    """

    DEFAULT_RESEARCH_SYSTEM_MESSAGE = (
        "You are an expert research analyst. Your task is to synthesize the provided web search results "
        "into a structured research brief. Focus on key facts, statistics, compelling arguments, and direct quotes. "
        "Organize the output into a JSON object with keys like 'main_points', 'statistics', 'quotes', and 'counter_arguments'."
    )

    def __init__(
        self,
        llm_service: LLMService,
        search_tool: SearchTool,
        search_config: SearchConfig,
        research_system_message: str = DEFAULT_RESEARCH_SYSTEM_MESSAGE,
        llm_model: str = FAST_LLM_MODEL,
    ):
        self.llm_service = llm_service
        self.search_tool = search_tool
        self.search_config = search_config
        self.research_system_message = research_system_message
        self.llm_model = llm_model

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Executes the research phase of the blog workflow.

        Args:
            state: The current workflow state
        """
        logger.info("--- Starting Research Agent ---")
        state.status = "RESEARCHING"
        state.log_entry("Research Agent: Started.")

        topic = state.initial_topic
        logger.info(f"Performing search with query: '{topic}'")

        search_results = self.search_tool.search(topic, self.search_config)

        # TODO: Handle search results more robustly
        state.sources = [
            res["url"] for res in search_results.get("results", []) if "url" in res
        ]

        # TODO: Improve this (prepare context for LLM summarization)
        context_parts = []
        for res in search_results.get("results", []):
            if "url" in res and "content" in res:
                context_parts.append(f"Source: {res['url']}\nContent: {res['content']}")
        context = "\n\n".join(context_parts)

        if not context:
            logger.warning("No content found from search results to create a brief.")
            state.log_entry(
                "Warning: Research Agent found no content from search results."
            )
            # Decide how to handle this: raise error, return empty brief, etc.
            state.research_brief = {"error": "No content found from search results."}
            logger.info("--- Finished Research Agent (No Content) ---")
            return state

        system_message = self.research_system_message

        prompt = (
            f"Please create a structured research brief on the topic '{topic}' based on the following context:\n\n"
            f"--- CONTEXT ---\n{context}\n\n--- END CONTEXT ---\n\n"
            "Generate a JSON object containing the synthesized research brief."
        )

        try:
            brief_str = query_llm(
                self.llm_service, state, prompt, system_message, model=self.llm_model
            )
        except Exception as e:
            logger.error(
                f"An error occurred during LLM query in Research Agent: {e}",
                exc_info=True,
            )
            state.log_entry(f"Error: Research Agent LLM query failed. Reason: {e}")
            raise

        try:
            if brief_str == ErrorConstants.LLM_NO_RESPONSE:  # Handle error coming from query_llm
                logger.error("LLM query returned an error string.")
                state.log_entry("Error: Research Agent received error from LLM query.")
                state.research_brief = {"error": "LLM query failed to produce content."}
            else:
                state.research_brief = json.loads(brief_str)
                logger.info("Successfully created research brief.")
                state.log_entry("Research Agent: Brief created.")
        except json.JSONDecodeError:
            logger.error(
                f"Failed to parse research brief JSON from LLM response: {brief_str[:500]}..."
            )
            state.log_entry(
                "Error: Research Agent failed to parse LLM response into JSON."
            )
            state.research_brief = {"raw_content": brief_str, "parse_error": True}
        except Exception as e:
            logger.error(
                f"An unexpected error occurred after LLM query in Research Agent: {e}",
                exc_info=True,
            )
            state.log_entry(f"Error: Research Agent failed post-LLM. Reason: {e}")
            raise

        logger.info("--- Finished Research Agent ---")
        return state
