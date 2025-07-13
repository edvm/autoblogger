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

import os

from agents import EditorAgent, ResearchAgent, WritingAgent
from agents.base_agent import AbstractAgent
from configs import config
from configs.logging_config import logger
from core.decorators import require_env_vars
from core.llm_services import LLMService, create_llm_service
from core.state import WorkflowState
from tools.search import (
    AnswerType,
    ContentType,
    SearchConfig,
    SearchDepth,
    SearchTool,
    SearchTopic,
    TimeRange,
)
from utils.filename import sanitize_filename


class ConfigurableBloggerManagerAgent(AbstractAgent):
    """
    Enhanced BloggerManagerAgent that supports SearchConfig injection.
    """

    def __init__(
        self,
        research_agent: AbstractAgent,
        writing_agent: AbstractAgent,
        editor_agent: AbstractAgent,
    ) -> None:
        self.research_agent = research_agent
        self.writing_agent = writing_agent
        self.editor_agent = editor_agent

    def execute(self, state: WorkflowState) -> WorkflowState:
        """Executes the blog generation workflow with optional search configuration.

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
            state = self.research_agent.execute(state)
            if not state.research_brief:
                raise ValueError("Research failed, stopping workflow.")

            # writing based on previous research brief
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


class BloggerApp:
    """Blogger application that orchestrates the multi-agent workflow for blog generation."""

    def __init__(self, output_dir: str = "outputs") -> None:
        """Initialize the BloggerApp with output directory.

        Args:
            output_dir: Directory where generated blog posts will be saved.
        """
        self.output_dir = output_dir
        self._llm_service: LLMService | None = None
        self._search_tool: SearchTool | None = None
        self._search_config: SearchConfig | None = None
        self._manager: ConfigurableBloggerManagerAgent | None = None

    def with_llm_service(self, llm_service: LLMService) -> "BloggerApp":
        """Set LLM service.

        Args:
            llm_service: The LLM service instance to use.

        Returns:
            Self for method chaining.
        """
        self._llm_service = llm_service
        return self

    def with_search_tool(self, search_tool: SearchTool) -> "BloggerApp":
        """Set the search tool.

        Args:
            search_tool: The search tool instance to use.

        Returns:
            Self for method chaining.
        """
        self._search_tool = search_tool
        return self

    def with_search_config(self, search_config: SearchConfig) -> "BloggerApp":
        """Set the search configuration.

        Args:
            search_config: The search configuration instance to use.

        Returns:
            Self for method chaining.
        """
        self._search_config = search_config
        return self

    def build(self) -> "BloggerApp":
        """Build and initialize blogger manager agent with injected dependencies.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If required dependencies are not set.
        """
        if self._llm_service is None:
            raise ValueError("LLM service must be set using with_llm_service()")
        if self._search_tool is None:
            raise ValueError("Search tool must be set using with_search_tool()")
        if self._search_config is None:
            raise ValueError("Search config must be set using with_search_config()")

        research_agent = ResearchAgent(
            llm_service=self._llm_service,
            search_tool=self._search_tool,
            search_config=self._search_config,
        )
        writing_agent = WritingAgent(
            llm_service=self._llm_service,
        )
        editor_agent = EditorAgent(
            llm_service=self._llm_service,
        )

        self._manager = ConfigurableBloggerManagerAgent(
            research_agent=research_agent,
            writing_agent=writing_agent,
            editor_agent=editor_agent,
        )

        return self

    def sanitize_topic_for_filename(self, topic: str) -> str:
        """Creates a filesystem-safe filename from a topic string.

        Args:
            topic: The topic string to sanitize.

        Returns:
            A string that is safe to use as a filename, truncated to prevent
            "File name too long" errors while preserving readability.
        """
        return sanitize_filename(topic, max_length=240)

    def save_output(self, state: WorkflowState) -> None:
        """Saves the final article and the run log to the specified directory.

        If the workflow did not complete successfully (i.e., state.status is not
        "COMPLETED" or state.final_content is empty), no output files will be saved.
        The article is saved as a markdown file and the full state (including logs)
        is saved as a JSON file.

        Args:
            state: The final state of the blog workflow, containing the article,
                   status, and logs.
        """
        if state.status != "COMPLETED" or not state.final_content:
            logger.warning(
                "Workflow did not complete successfully. No output file will be saved."
            )
            return

        os.makedirs(self.output_dir, exist_ok=True)

        base_filename = self.sanitize_topic_for_filename(state.initial_topic)

        # Save article as a markdown file
        article_path = os.path.join(self.output_dir, f"{base_filename}.md")
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(state.final_content)
        logger.info(f"✅ Final article saved to: {article_path}")

        # Save the full state (including logs) as a JSON file for debugging
        log_path = os.path.join(self.output_dir, f"{base_filename}_log.json")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))
        logger.info(f"✅ Full run log saved to: {log_path}")

    def generate_blog_post(self, state: WorkflowState) -> WorkflowState:
        """Main function to run the autoblogger workflow.

        This function runs the manager agent to generate blog content and saves the output.

        Args:
            state: Initial workflow state with the topic to blog about.

        Returns:
            Final workflow state after processing.

        Raises:
            ValueError: If the app hasn't been built with build() method.
        """
        if self._manager is None:
            raise ValueError(
                "BloggerApp must be built using build() method before generating blog posts"
            )

        logger.info("=" * 50)

        final_state = self._manager.execute(state)

        self.save_output(final_state)

        logger.info(
            f"Blog generation workflow completed for topic: '{final_state.initial_topic}'"
        )
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 50)

        return final_state


@require_env_vars("TAVILY_API_KEY", "CLERK_SECRET_KEY")
def get_blogger_app(
    output_dir: str = "outputs",
    search_depth: str = "basic",
    topic: str = "general",
    time_range: str = "month",
    days: int = 7,
    max_results: int = 5,
    include_domains: list | None = None,
    exclude_domains: list | None = None,
    include_answer: bool = False,
    include_raw_content: bool = False,
    include_images: bool = False,
    timeout: int = 60,
) -> BloggerApp:
    """Factory function to create and return a fully configured BloggerApp instance.

    This function creates a BloggerApp with the configured LLM service (OpenAI or Gemini based
    on LLM_PROVIDER setting) and Tavily search tool, and configures search parameters through SearchConfig.

    Args:
        output_dir: Directory where generated blog posts will be saved.
        search_depth: Depth of search ("basic" or "advanced").
        topic: Search topic category ("general", "news", "finance").
        time_range: Time range for results ("day", "week", "month", "year").
        days: Number of days when time_range is custom.
        max_results: Maximum number of results to return.
        include_domains: Domains to include in search.
        exclude_domains: Domains to exclude from search.
        include_answer: Whether to include direct answers.
        include_raw_content: Whether to include raw content.
        include_images: Whether to include images.
        timeout: Request timeout in seconds.

    Returns:
        A fully configured and built BloggerApp instance ready to use.

    Raises:
        EnvironmentError: If the required API key for the configured LLM provider is not set.
    """
    include_domains = include_domains or []
    exclude_domains = exclude_domains or []

    from core.llm_services import LLMServiceException
    from tools.search import TavilySearch

    try:
        llm_service = create_llm_service()
        logger.info(f"Using LLM provider: {config.LLM_PROVIDER}")
    except LLMServiceException as e:
        logger.error(f"Failed to create LLM service: {e}")
        raise OSError(f"LLM service configuration error: {e}")

    # Create SearchConfig with provided parameters
    search_tool = TavilySearch()
    search_config = SearchConfig(
        search_depth=SearchDepth(search_depth),
        topic=SearchTopic(topic),
        time_range=TimeRange(time_range),
        days=days,
        max_results=max_results,
        include_domains=include_domains,
        exclude_domains=exclude_domains,
        include_answer=AnswerType.BASIC if include_answer else AnswerType.NONE,
        include_raw_content=ContentType.TEXT
        if include_raw_content
        else ContentType.NONE,
        include_images=include_images,
        timeout=timeout,
    )

    return (
        BloggerApp(output_dir=output_dir)
        .with_llm_service(llm_service)
        .with_search_tool(search_tool)
        .with_search_config(search_config)
        .build()
    )
