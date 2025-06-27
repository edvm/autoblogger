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

"""Tests for the core state management."""

import pytest
from datetime import datetime
from core.state import WorkflowState, WokflowType


class TestWorkflowState:
    """Test cases for WorkflowState."""

    def test_workflow_state_creation(self):
        """Test basic WorkflowState creation."""
        state = WorkflowState(initial_topic="Test Topic")

        assert state.initial_topic == "Test Topic"
        assert state.workflow_type == WokflowType.BLOGGING
        assert state.status == "PENDING"
        assert state.run_log == []
        assert state.research_brief is None
        assert state.sources == []
        assert state.draft_content is None
        assert state.final_content is None
        assert isinstance(state.timestamp, str)

    def test_workflow_state_with_custom_values(self):
        """Test WorkflowState creation with custom values."""
        research_brief = {"main_points": ["Point 1", "Point 2"]}
        sources = ["https://example.com/source1", "https://example.com/source2"]

        state = WorkflowState(
            initial_topic="Custom Topic",
            workflow_type=WokflowType.RESEARCH,
            status="IN_PROGRESS",
            research_brief=research_brief,
            sources=sources,
            draft_content="Draft content",
            final_content="Final content",
        )

        assert state.initial_topic == "Custom Topic"
        assert state.workflow_type == WokflowType.RESEARCH
        assert state.status == "IN_PROGRESS"
        assert state.research_brief == research_brief
        assert state.sources == sources
        assert state.draft_content == "Draft content"
        assert state.final_content == "Final content"

    def test_log_entry(self):
        """Test adding log entries."""
        state = WorkflowState(initial_topic="Test Topic")

        # Initially empty
        assert len(state.run_log) == 0

        # Add log entry
        state.log_entry("Test log entry")

        assert len(state.run_log) == 1
        assert "Test log entry" in state.run_log[0]
        assert "[" in state.run_log[0]  # Should contain timestamp
        assert "]" in state.run_log[0]

        # Add another entry
        state.log_entry("Second log entry")

        assert len(state.run_log) == 2
        assert "Second log entry" in state.run_log[1]

    def test_log_entry_timestamp_format(self):
        """Test log entry timestamp format."""
        state = WorkflowState(initial_topic="Test Topic")
        state.log_entry("Test entry")

        log_entry = state.run_log[0]

        # Should start with timestamp in brackets
        assert log_entry.startswith("[")
        assert "] Test entry" in log_entry

        # Extract timestamp part
        timestamp_part = log_entry.split("] ")[0][
            1:
        ]  # Remove '[' and get everything before ']'

        # Should be parseable as datetime
        try:
            datetime.strptime(timestamp_part, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pytest.fail("Timestamp format is incorrect")

    def test_workflow_type_enum_values(self):
        """Test WorkflowType enum values."""
        assert WokflowType.BLOGGING == "blogging"
        assert WokflowType.RESEARCH == "research"
        assert WokflowType.WRITING == "writing"
        assert WokflowType.EDITING == "editing"

    def test_workflow_state_immutable_lists(self):
        """Test that list fields are properly initialized."""
        state1 = WorkflowState(initial_topic="Topic 1")
        state2 = WorkflowState(initial_topic="Topic 2")

        # Lists should be separate instances
        state1.run_log.append("Entry 1")
        state1.sources.append("Source 1")

        assert len(state1.run_log) == 1
        assert len(state1.sources) == 1
        assert len(state2.run_log) == 0
        assert len(state2.sources) == 0

    def test_workflow_state_pydantic_validation(self):
        """Test Pydantic validation."""
        # Should require initial_topic
        with pytest.raises((TypeError, ValueError)):
            WorkflowState()

        # Should accept valid enum values
        state = WorkflowState(initial_topic="Test", workflow_type=WokflowType.WRITING)
        assert state.workflow_type == WokflowType.WRITING

    def test_timestamp_is_iso_format(self):
        """Test that timestamp is in ISO format."""
        state = WorkflowState(initial_topic="Test Topic")

        # Should be parseable as ISO datetime
        try:
            datetime.fromisoformat(state.timestamp)
        except ValueError:
            pytest.fail("Timestamp is not in ISO format")
