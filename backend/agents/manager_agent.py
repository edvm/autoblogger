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

# The master agent that orchestrates the entire blog generation workflow.

# This agent manages the sequence of operations, calling specialized agents
# for research, writing, and editing to produce a final blog post.

# Attributes:
#     research_agent (AbstractAgent): An agent responsible for conducting research.
#     writing_agent (AbstractAgent): An agent responsible for drafting the blog content.
#     editor_agent (AbstractAgent): An agent responsible for editing and finalizing the content.

#     Initializes the BloggerManagerAgent with its constituent agents.

#         research_agent: An instance of an agent that conforms to AbstractAgent,
#                         tasked with research.
#         writing_agent: An instance of an agent that conforms to AbstractAgent,
#                        tasked with content generation.
#         editor_agent: An instance of an agent that conforms to AbstractAgent,
#                       tasked with content editing.

#     Executes the blog generation workflow from research to finalization.

#     by invoking the respective agents in sequence. It updates the workflow
#     state at each step and handles potential failures.

#         state: The initial WorkflowState object, typically containing the
#                initial topic for the blog post.

#         The WorkflowState object updated with the results of the entire
#         workflow, including research brief, draft content, final content,
#         and status.

#         ValueError: If any of the critical steps (research, writing, or editing)
#                     fail to produce their expected output (e.g., research_brief,
#                     draft_content, final_content are not populated).
from .base_agent import AbstractAgent
from core.state import WorkflowState
from configs.logging_config import logger


class BloggerManagerAgent(AbstractAgent):
    """
    The master agent that orchestrates the entire workflow by calling other agents in sequence.
    """

    def __init__(
        self,
        research_agent: AbstractAgent,
        writing_agent: AbstractAgent,
        editor_agent: AbstractAgent,
    ) -> None:
        self.research_agent: AbstractAgent = research_agent
        self.writing_agent: AbstractAgent = writing_agent
        self.editor_agent: AbstractAgent = editor_agent

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Executes the blog generation workflow.

        This method orchestrates the research, writing, and editing phases
        by calling the respective agents.

        Args:
            state: The current state of the blog workflow.

        Returns:
            The updated state of the blog workflow after execution.

        Raises:
            ValueError: If any of the research, writing, or editing steps fail
                        to produce the required output.
        """
        logger.info(
            f"--- Starting Autoblogger Workflow for Topic: '{state.initial_topic}' ---"
        )
        state.log_entry(
            f"Manager Agent: Initiating workflow for '{state.initial_topic}'."
        )

        try:
            # research phase
            state = self.research_agent.execute(state)

            if not state.research_brief:
                raise ValueError("Research failed, stopping workflow.")

            # writing based on the research brief
            state = self.writing_agent.execute(state)
            if not state.draft_content:
                raise ValueError("Writing failed, stopping workflow.")

            # edit the draft content
            state = self.editor_agent.execute(state)
            if not state.final_content:
                raise ValueError("Editing failed, stopping workflow.")

            state.status = "COMPLETED"
            logger.info(
                f"--- Autoblogger Workflow for '{state.initial_topic}' COMPLETED SUCCESSFULLY ---"
            )
            state.log_entry("Manager Agent: Workflow completed successfully.")

        except Exception as e:
            logger.error(f"Workflow failed at step {state.status}: {e}", exc_info=True)
            state.status = "FAILED"
            state.log_entry(
                f"FATAL ERROR: Workflow failed during {state.status} phase. Reason: {e}"
            )

        return state
