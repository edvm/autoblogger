#!/usr/bin/env python3
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

"""
Test script to demonstrate the enhanced Writing Agent with directive parsing.

This script shows how users can control the Writing Agent's behavior by embedding
directives in their topic strings.

Usage:
    python test_writing_agent.py
"""

import os
from agents.writing_agent import WritingAgent
from core.llm_services import OpenAIService
from core.state import WorkflowState
from configs.config import OPENAI_API_KEY


def test_directive_parsing():
    """Test the directive parsing functionality."""

    # Create a Writing Agent instance
    llm_service = OpenAIService(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    writing_agent = WritingAgent(llm_service)

    # Test cases for directive parsing
    test_topics = [
        # Basic topic without directives
        "Introduction to Machine Learning",
        # Topic with tone directive
        "[tone:casual] Python Programming for Beginners",
        # Topic with multiple directives
        "[tone:technical][style:tutorial][length:detailed] Advanced Docker Container Orchestration",
        # Topic with equals syntax
        "[tone=beginner-friendly][audience=beginners][format=guide] Understanding Blockchain Technology",
        # Topic with mixed syntax
        "[tone:professional][style=analytical][length:comprehensive] Cloud Computing Security Best Practices",
        # Complex topic with all directive types
        "[tone:educational][style:tutorial][length:detailed][audience:developers][format:howto] Building REST APIs with FastAPI and Python",
    ]

    print("🧪 Testing Writing Agent Directive Parsing\n")
    print("=" * 80)

    for i, topic in enumerate(test_topics, 1):
        print(f"\n{i}. Topic: {topic}")
        print("-" * 60)

        # Parse directives
        directives = writing_agent.parse_topic_directives(topic)

        print(f"Clean Topic: {directives['clean_topic']}")
        print(f"Tone: {directives['tone']}")
        print(f"Style: {directives['style']}")
        print(f"Length: {directives['length']}")
        print(f"Audience: {directives['audience']}")
        print(f"Format: {directives['format']}")

        # Show how the system message would be customized
        system_message = writing_agent.build_enhanced_system_message(directives)
        print(f"\nCustomized System Message:")
        print(f"  {system_message[:150]}...")

        print("\n" + "=" * 80)


def test_full_writing_workflow():
    """Test the full writing workflow with a sample topic."""

    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY not found. Skipping full workflow test.")
        return

    print("\n🚀 Testing Full Writing Workflow\n")

    # Create a sample state with research brief
    sample_research = {
        "summary": "FastAPI is a modern, fast web framework for building APIs with Python",
        "key_points": [
            "FastAPI is built on Starlette and Pydantic",
            "Automatic API documentation generation",
            "High performance comparable to NodeJS and Go",
            "Built-in data validation and serialization",
        ],
        "sources_info": "Information gathered from official FastAPI documentation and performance benchmarks",
    }

    # Test with directives
    topic_with_directives = "[tone:beginner-friendly][style:tutorial][length:standard][audience:developers] Getting Started with FastAPI"

    state = WorkflowState(
        initial_topic=topic_with_directives, research_brief=sample_research
    )

    # Create and execute Writing Agent
    llm_service = OpenAIService(api_key=OPENAI_API_KEY)
    writing_agent = WritingAgent(llm_service)

    print(f"Original Topic: {topic_with_directives}")
    print(f"Research Brief: {sample_research}")
    print("\nExecuting Writing Agent...\n")

    try:
        result_state = writing_agent.execute(state)

        print("✅ Writing Agent executed successfully!")
        print(f"Status: {result_state.status}")
        print(
            f"Content Length: {len(result_state.final_content) if result_state.final_content else 0} characters"
        )
        print(f"Run Log Entries: {len(result_state.run_log)}")

        # Show first few lines of generated content
        if result_state.final_content:
            lines = result_state.final_content.split("\n")[:10]
            print("\nFirst 10 lines of generated content:")
            print("-" * 40)
            for line in lines:
                print(line)
            print("-" * 40)

    except Exception as e:
        print(f"❌ Error executing Writing Agent: {e}")


if __name__ == "__main__":
    print("📝 Enhanced Writing Agent Test Suite")
    print("This script demonstrates directive parsing and customization features.\n")

    # Test directive parsing (works without API key)
    test_directive_parsing()

    # Test full workflow (requires API key)
    test_full_writing_workflow()

    print("\n✨ Test completed!")
    print("\nExample usage patterns:")
    print("  • [tone:casual] Your topic here")
    print("  • [style:tutorial][length:brief] Your topic")
    print("  • [audience:beginners][format:guide] Your topic")
    print("  • [tone:technical][style:analytical] Your topic")
