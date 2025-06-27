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

"""Tests for BloggerManagerAgent."""

from agents.manager_agent import BloggerManagerAgent
from core.state import WorkflowState


class TestBloggerManagerAgent:
    """Test cases for BloggerManagerAgent."""

    def test_manager_agent_initialization(
        self, mock_research_agent, mock_writing_agent, mock_editor_agent
    ):
        """Test BloggerManagerAgent initialization."""
        manager = BloggerManagerAgent(
            research_agent=mock_research_agent,
            writing_agent=mock_writing_agent,
            editor_agent=mock_editor_agent,
        )

        assert manager.research_agent == mock_research_agent
        assert manager.writing_agent == mock_writing_agent
        assert manager.editor_agent == mock_editor_agent

    def test_successful_workflow_execution(
        self, blogger_manager_agent, basic_workflow_state
    ):
        """Test successful workflow execution through all agents."""
        result_state = blogger_manager_agent.execute(basic_workflow_state)

        # All agents should have been executed
        assert blogger_manager_agent.research_agent.executed
        assert blogger_manager_agent.writing_agent.executed
        assert blogger_manager_agent.editor_agent.executed

        # State should have all required content
        assert result_state.research_brief is not None
        assert result_state.draft_content is not None
        assert result_state.final_content is not None

        # Status should be completed
        assert result_state.status == "COMPLETED"

        # Should have log entries
        assert len(result_state.run_log) > 0
        assert any("Manager Agent" in entry for entry in result_state.run_log)

    def test_research_agent_failure(
        self,
        mock_failing_research_agent,
        mock_writing_agent,
        mock_editor_agent,
        basic_workflow_state,
    ):
        """Test workflow failure when research agent fails."""
        manager = BloggerManagerAgent(
            research_agent=mock_failing_research_agent,
            writing_agent=mock_writing_agent,
            editor_agent=mock_editor_agent,
        )

        result_state = manager.execute(basic_workflow_state)

        # Research agent should have been attempted
        assert mock_failing_research_agent.executed

        # Writing and editor agents should not have been executed
        assert not mock_writing_agent.executed
        assert not mock_editor_agent.executed

        # Status should be failed
        assert result_state.status == "FAILED"

        # Should have error log entry
        assert any("FATAL ERROR" in entry for entry in result_state.run_log)

    def test_research_agent_no_brief(
        self, mock_writing_agent, mock_editor_agent, basic_workflow_state
    ):
        """Test workflow failure when research agent doesn't produce brief."""

        # Create a mock research agent that doesn't set research_brief
        class NoResultResearchAgent:
            def __init__(self):
                self.executed = False

            def execute(self, state):
                self.executed = True
                # Don't set research_brief
                return state

        no_result_agent = NoResultResearchAgent()
        manager = BloggerManagerAgent(
            research_agent=no_result_agent,
            writing_agent=mock_writing_agent,
            editor_agent=mock_editor_agent,
        )

        result_state = manager.execute(basic_workflow_state)

        # Research agent should have been executed
        assert no_result_agent.executed

        # Other agents should not have been executed
        assert not mock_writing_agent.executed
        assert not mock_editor_agent.executed

        # Status should be failed
        assert result_state.status == "FAILED"

        # Should have specific error message
        assert any("Research failed" in entry for entry in result_state.run_log)

    def test_writing_agent_no_draft(
        self, mock_research_agent, mock_editor_agent, basic_workflow_state
    ):
        """Test workflow failure when writing agent doesn't produce draft."""

        class NoResultWritingAgent:
            def __init__(self):
                self.executed = False

            def execute(self, state):
                self.executed = True
                # Don't set draft_content
                return state

        no_result_agent = NoResultWritingAgent()
        manager = BloggerManagerAgent(
            research_agent=mock_research_agent,
            writing_agent=no_result_agent,
            editor_agent=mock_editor_agent,
        )

        result_state = manager.execute(basic_workflow_state)

        # Research and writing agents should have been executed
        assert mock_research_agent.executed
        assert no_result_agent.executed

        # Editor agent should not have been executed
        assert not mock_editor_agent.executed

        # Status should be failed
        assert result_state.status == "FAILED"

        # Should have specific error message
        assert any("Writing failed" in entry for entry in result_state.run_log)

    def test_editor_agent_no_final(
        self, mock_research_agent, mock_writing_agent, basic_workflow_state
    ):
        """Test workflow failure when editor agent doesn't produce final content."""

        class NoResultEditorAgent:
            def __init__(self):
                self.executed = False

            def execute(self, state):
                self.executed = True
                # Don't set final_content
                return state

        no_result_agent = NoResultEditorAgent()
        manager = BloggerManagerAgent(
            research_agent=mock_research_agent,
            writing_agent=mock_writing_agent,
            editor_agent=no_result_agent,
        )

        result_state = manager.execute(basic_workflow_state)

        # All agents should have been executed
        assert mock_research_agent.executed
        assert mock_writing_agent.executed
        assert no_result_agent.executed

        # Status should be failed
        assert result_state.status == "FAILED"

        # Should have specific error message
        assert any("Editing failed" in entry for entry in result_state.run_log)

    def test_workflow_preserves_initial_topic(self, blogger_manager_agent):
        """Test that workflow preserves the initial topic."""
        initial_topic = "Advanced AI Research Trends"
        state = WorkflowState(initial_topic=initial_topic)

        result_state = blogger_manager_agent.execute(state)

        assert result_state.initial_topic == initial_topic

    def test_workflow_adds_manager_log_entries(
        self, blogger_manager_agent, basic_workflow_state
    ):
        """Test that manager adds appropriate log entries."""
        result_state = blogger_manager_agent.execute(basic_workflow_state)

        # Should have initial and completion log entries from manager
        manager_entries = [
            entry for entry in result_state.run_log if "Manager Agent" in entry
        ]
        assert len(manager_entries) >= 2

        # Should have initiating entry
        assert any("Initiating workflow" in entry for entry in manager_entries)

        # Should have completion entry (for successful workflow)
        assert any("completed successfully" in entry for entry in manager_entries)

    def test_workflow_state_progression(
        self, blogger_manager_agent, basic_workflow_state
    ):
        """Test that workflow state progresses correctly through agents."""
        result_state = blogger_manager_agent.execute(basic_workflow_state)

        # Verify each agent received the state and updated it
        research_agent = blogger_manager_agent.research_agent
        writing_agent = blogger_manager_agent.writing_agent
        editor_agent = blogger_manager_agent.editor_agent

        # Research agent should have received initial state
        assert (
            research_agent.received_state.initial_topic
            == basic_workflow_state.initial_topic
        )

        # Writing agent should have received state with research brief
        assert writing_agent.received_state.research_brief is not None

        # Editor agent should have received state with draft content
        assert editor_agent.received_state.draft_content is not None
