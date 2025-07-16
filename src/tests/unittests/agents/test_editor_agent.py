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

from unittest.mock import Mock

import pytest

from agents.editor_agent import EditorAgent

"""Tests for EditorAgent."""


class TestEditorAgent:
    """Test cases for EditorAgent."""

    def test_editor_agent_initialization(self, mock_llm_service):
        """Test EditorAgent initialization."""
        agent = EditorAgent(llm_service=mock_llm_service)

        assert agent.llm_service == mock_llm_service
        assert agent.llm_model is not None

    def test_successful_editor_execution(
        self, draft_written_workflow_state, mock_llm_service
    ):
        """Test successful editor execution."""
        agent = EditorAgent(llm_service=mock_llm_service)

        result_state = agent.execute(draft_written_workflow_state)

        # Verify state updates
        assert result_state.status == "EDITING"
        assert result_state.final_content == draft_written_workflow_state.draft_content

        # Verify log entries
        assert any("Editor Agent: Started" in entry for entry in result_state.run_log)
        assert any("Final content produced" in entry for entry in result_state.run_log)

    def test_editor_execution_no_draft_content(
        self, basic_workflow_state, mock_llm_service
    ):
        """Test editor execution without draft content."""
        agent = EditorAgent(llm_service=mock_llm_service)

        result_state = agent.execute(basic_workflow_state)

        # Should handle missing draft gracefully
        assert result_state.draft_content is None
        assert result_state.final_content is None

        # Should have error log entry
        assert any(
            "cannot run without draft content" in entry
            for entry in result_state.run_log
        )

        # LLM should not be called since editing is currently commented out
        mock_llm_service.generate_response.assert_not_called()

    def test_editor_preserves_draft_as_final(
        self, draft_written_workflow_state, mock_llm_service
    ):
        """Test that editor preserves draft content as final content."""
        agent = EditorAgent(llm_service=mock_llm_service)

        original_draft = draft_written_workflow_state.draft_content

        result_state = agent.execute(draft_written_workflow_state)

        # Since editing logic is commented out, should copy draft to final
        assert result_state.final_content == original_draft

    def test_editor_status_progression(
        self, draft_written_workflow_state, mock_llm_service
    ):
        """Test that editor agent properly sets status."""
        agent = EditorAgent(llm_service=mock_llm_service)

        # Initial status
        assert draft_written_workflow_state.status == "WRITING"

        result_state = agent.execute(draft_written_workflow_state)

        # Status should be updated
        assert result_state.status == "EDITING"

    def test_editor_execution_empty_draft_content(
        self, basic_workflow_state, mock_llm_service
    ):
        """Test editor execution with empty string draft content."""
        basic_workflow_state.draft_content = ""

        agent = EditorAgent(llm_service=mock_llm_service)

        result_state = agent.execute(basic_workflow_state)

        # Empty string should be treated as missing content
        assert any(
            "cannot run without draft content" in entry
            for entry in result_state.run_log
        )

    def test_editor_preserves_other_state_fields(
        self, draft_written_workflow_state, mock_llm_service
    ):
        """Test that editor preserves other state fields."""
        agent = EditorAgent(llm_service=mock_llm_service)

        original_topic = draft_written_workflow_state.initial_topic
        original_research = draft_written_workflow_state.research_brief
        original_sources = draft_written_workflow_state.sources
        original_draft = draft_written_workflow_state.draft_content

        result_state = agent.execute(draft_written_workflow_state)

        # Should preserve all other fields
        assert result_state.initial_topic == original_topic
        assert result_state.research_brief == original_research
        assert result_state.sources == original_sources
        assert result_state.draft_content == original_draft

    def test_editor_adds_log_entries(
        self, draft_written_workflow_state, mock_llm_service
    ):
        """Test that editor adds appropriate log entries."""
        agent = EditorAgent(llm_service=mock_llm_service)

        initial_log_count = len(draft_written_workflow_state.run_log)

        result_state = agent.execute(draft_written_workflow_state)

        # Should have added log entries
        assert len(result_state.run_log) > initial_log_count

        # Should have specific log entries
        editor_entries = [
            entry for entry in result_state.run_log if "Editor Agent" in entry
        ]
        assert len(editor_entries) >= 2  # Started and final content produced

    # Note: The following tests would be relevant if the LLM editing logic was enabled

    @pytest.mark.skip(reason="LLM editing logic is currently commented out")
    def test_editor_with_llm_editing(self, draft_written_workflow_state):
        """Test editor execution with LLM editing enabled."""
        mock_llm_service = Mock()
        edited_content = (
            "# Edited Article\n\nThis is the edited and improved version..."
        )
        mock_llm_service.generate_response.return_value.content = edited_content
        mock_llm_service.generate_response.return_value.usage.total_tokens = 150

        agent = EditorAgent(llm_service=mock_llm_service)

        # This test would work if the editing logic was uncommented
        result_state = agent.execute(draft_written_workflow_state)

        assert result_state.final_content == edited_content
        mock_llm_service.generate_response.assert_called_once()

    @pytest.mark.skip(reason="LLM editing logic is currently commented out")
    def test_editor_prompt_construction(self, draft_written_workflow_state):
        """Test that editor prompt is properly constructed."""
        mock_llm_service = Mock()
        mock_llm_service.generate_response.return_value.content = "Edited content"
        mock_llm_service.generate_response.return_value.usage = None

        agent = EditorAgent(llm_service=mock_llm_service)

        # This test would work if the editing logic was uncommented
        agent.execute(draft_written_workflow_state)

        call_args = mock_llm_service.generate_response.call_args
        prompt = call_args[1]["prompt"]
        system_message = call_args[1]["system_message"]

        # Verify prompt contains necessary elements
        assert draft_written_workflow_state.initial_topic in prompt
        assert draft_written_workflow_state.draft_content in prompt
        assert "RESEARCH BRIEF" in prompt
        assert "DRAFT ARTICLE" in prompt

        # Verify system message contains editing instructions
        assert "editor" in system_message.lower()
        assert "improve" in system_message.lower() or "edit" in system_message.lower()
