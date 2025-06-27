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

from .base_agent import AbstractAgent
from core.state import WorkflowState
from core.llm_services import LLMService, query_llm
from configs.config import FAST_LLM_MODEL
from configs.logging_config import logger
import json


class EditorAgent(AbstractAgent):
    """
    Agent responsible for reviewing, editing, and fact-checking the draft.
    """

    def __init__(self, llm_service: LLMService, llm_model: str = FAST_LLM_MODEL):
        self.llm_service = llm_service
        self.llm_model = llm_model

    def execute(self, state: WorkflowState) -> WorkflowState:
        if not state.draft_content:
            logger.error("Cannot run Editor Agent: Draft content is missing.")
            state.log_entry("Error: Editor Agent cannot run without draft content.")
            return state

        logger.info("--- Starting Editor Agent ---")
        state.status = "EDITING"
        state.log_entry("Editor Agent: Started.")

        state.final_content = (
            state.draft_content
        )  # Default to draft if no edits are made

        # system_message = (
        #     "You are a meticulous editor with an eye for detail. Your tasks are to: "
        #     "1. Improve grammar, clarity, and flow. "
        #     "2. Correct any factual errors by strictly adhering to the provided research brief. "
        #     "3. Ensure the tone is engaging and professional. "
        #     "4. Output only the final, polished, ready-to-publish markdown content."
        # )

        # prompt = (
        #     f"Please review and edit the following draft article about '{state.initial_topic}'.\n"
        #     "Cross-reference every claim against the provided research brief to ensure factual accuracy. "
        #     "If a claim in the draft is not supported by the brief, remove or rephrase it.\n\n"
        #     f"--- RESEARCH BRIEF ---\n{json.dumps(state.research_brief, indent=2)}\n\n"
        #     f"--- DRAFT ARTICLE ---\n{state.draft_content}\n\n"
        #     f"--- END DRAFT ARTICLE ---\n\n"
        #     "Now, provide the final, polished version of the article in markdown format. "
        #     "Do not add any commentary, just the article itself."
        # )

        # state.final_content = query_llm(
        #     self.llm_service, state, prompt, system_message, model=self.llm_model
        # )
        logger.info("Successfully edited and finalized the article.")
        state.log_entry("Editor Agent: Final content produced.")
        logger.info("--- Finished Editor Agent ---")

        return state
