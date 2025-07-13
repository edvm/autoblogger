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

"""Tests for WritingAgent."""

import pytest

from agents.writing_agent import WritingAgent


class TestWritingAgent:
    """Test cases for WritingAgent."""

    def test_writing_agent_initialization(self, mock_llm_service):
        """Test WritingAgent initialization."""
        agent = WritingAgent(llm_service=mock_llm_service)

        assert agent.llm_service == mock_llm_service
        assert agent.llm_model is not None

    def test_parse_topic_directives_no_directives(self, mocker):
        """Test parsing topic with no directives."""
        agent = WritingAgent(llm_service=mocker.Mock())
        topic = "Machine Learning Trends in 2024"

        directives = agent.parse_topic_directives(topic)

        # Should return default values
        assert directives["tone"] == "professional"
        assert directives["style"] == "informative"
        assert directives["length"] == "comprehensive"
        assert directives["audience"] == "general"
        assert directives["format"] == "article"
        assert directives["clean_topic"] == topic

    def test_parse_topic_directives_with_colon_format(self, mocker):
        """Test parsing topic with colon-formatted directives."""
        agent = WritingAgent(llm_service=mocker.Mock())
        topic = "[tone:casual] [style:tutorial] Machine Learning Basics"

        directives = agent.parse_topic_directives(topic)

        assert directives["tone"] == "casual"
        assert directives["style"] == "tutorial"
        assert directives["clean_topic"] == "Machine Learning Basics"

    def test_parse_topic_directives_with_equals_format(self, mocker):
        """Test parsing topic with equals-formatted directives."""
        agent = WritingAgent(llm_service=mocker.Mock())
        topic = "[audience=beginners] [length=detailed] Python Programming Guide"

        directives = agent.parse_topic_directives(topic)

        assert directives["audience"] == "beginners"
        assert directives["length"] == "detailed"
        assert directives["clean_topic"] == "Python Programming Guide"

    def test_parse_topic_directives_mixed_formats(self, mocker):
        """Test parsing topic with mixed directive formats."""
        agent = WritingAgent(llm_service=mocker.Mock())
        topic = "[tone:professional] [format=tutorial] [audience:experts] Advanced AI Concepts"

        directives = agent.parse_topic_directives(topic)

        assert directives["tone"] == "professional"
        assert directives["format"] == "tutorial"
        assert directives["audience"] == "experts"
        assert directives["clean_topic"] == "Advanced AI Concepts"

    def test_parse_topic_directives_unknown_directive(self, mocker):
        """Test parsing topic with unknown directives."""
        agent = WritingAgent(llm_service=mocker.Mock())
        topic = "[unknown:value] [tone:casual] Valid Topic"

        directives = agent.parse_topic_directives(topic)

        # Unknown directive should be ignored
        assert "unknown" not in directives
        assert directives["tone"] == "casual"
        assert directives["clean_topic"] == "Valid Topic"

    def test_parse_topic_directives_whitespace_cleanup(self, mocker):
        """Test that whitespace is properly cleaned up."""
        agent = WritingAgent(llm_service=mocker.Mock())
        topic = "[tone:casual]    [style:tutorial]    Topic    with    spaces"

        directives = agent.parse_topic_directives(topic)

        # Multiple spaces should be cleaned up
        assert directives["clean_topic"] == "Topic with spaces"

    @pytest.mark.skip(reason="to be fixed")
    def test_build_enhanced_system_message(self, mocker):
        """Test building enhanced system message."""
        agent = WritingAgent(llm_service=mocker.Mock())
        directives = {
            "tone": "casual",
            "style": "tutorial",
            "length": "detailed",
            "audience": "beginners",
            "format": "guide",
        }

        system_message = agent.build_enhanced_system_message(directives)

        # Should contain all directive values
        assert "casual" in system_message
        assert "tutorial" in system_message
        assert "detailed" in system_message
        assert "beginners" in system_message
        assert "guide" in system_message

    def test_writing_execution_no_research_brief(
        self, basic_workflow_state, mock_llm_service
    ):
        """Test writing execution without research brief."""
        agent = WritingAgent(llm_service=mock_llm_service)

        result_state = agent.execute(basic_workflow_state)

        # Should handle missing research brief gracefully
        assert result_state.status == "PENDING"  # Status shouldn't change

        # Should have log entry about missing research
        assert any(
            "cannot run without a research brief" in entry.lower()
            for entry in result_state.run_log
        )

        # LLM should not be called when research is missing
        mock_llm_service.generate_response.assert_not_called()

    def test_writing_execution_llm_exception(self, researched_workflow_state, mocker):
        """Test writing execution when LLM service raises exception."""
        mock_llm_service = mocker.Mock()
        mock_llm_service.generate_response.side_effect = Exception("LLM service error")

        agent = WritingAgent(llm_service=mock_llm_service)

        with pytest.raises(Exception) as exc_info:
            agent.execute(researched_workflow_state)

        assert "LLM service error" in str(exc_info.value)

    def test_writing_status_progression(
        self, researched_workflow_state, mock_llm_service
    ):
        """Test that writing agent properly sets status."""
        mock_llm_service.generate_response.return_value.content = "Content"
        mock_llm_service.generate_response.return_value.usage = None

        agent = WritingAgent(llm_service=mock_llm_service)

        # Initial status
        assert researched_workflow_state.status == "RESEARCHING"

        result_state = agent.execute(researched_workflow_state)

        # Status should be updated
        assert result_state.status == "WRITING"
