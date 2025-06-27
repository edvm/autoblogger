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
from typing import Any, Dict
import json
import re


class WritingAgent(AbstractAgent):
    """
    Enhanced Writing Agent responsible for creating high-quality blog posts based on research brief.
    Now supports directive parsing from topics to customize content generation behavior.
    """

    def __init__(self, llm_service: LLMService, llm_model: str = FAST_LLM_MODEL):
        self.llm_service = llm_service
        self.llm_model = llm_model

    def parse_topic_directives(self, topic: str) -> Dict[str, Any]:
        """
        Parse directives from the topic to customize writing behavior.
        Directives can be embedded in the topic using formats like:
        - [tone:professional] or [tone=professional]
        - [length:detailed] or [length=detailed]
        - [style:technical] or [style=technical]
        - [audience:beginners] or [audience=beginners]
        - [format:tutorial] or [format=tutorial]
        """
        directives = {
            "tone": "professional",
            "style": "informative",
            "length": "comprehensive",
            "audience": "general",
            "format": "article",
            "clean_topic": topic,
        }

        # Pattern to match directives like [key:value] or [key=value]
        directive_pattern = r"\[(\w+)[=:]([^\]]+)\]"
        matches = re.findall(directive_pattern, topic)

        if matches:
            logger.info(f"Found {len(matches)} directive(s) in topic")
            for key, value in matches:
                if key.lower() in directives:
                    directives[key.lower()] = value.strip()
                    logger.info(f"Applied directive: {key}={value}")

            # Remove directives from topic to get clean topic
            clean_topic = re.sub(directive_pattern, "", topic).strip()
            # Clean up extra spaces
            clean_topic = re.sub(r"\s+", " ", clean_topic)
            directives["clean_topic"] = clean_topic

        return directives

    def build_enhanced_system_message(self, directives: Dict[str, str]) -> str:
        """Build a customized system message based on parsed directives."""

        # Base persona
        base_message = "You are an expert content creator and blogger"

        # Tone customization
        tone_map = {
            "professional": "with a professional, authoritative voice",
            "casual": "with a friendly, conversational tone",
            "technical": "with deep technical expertise and precision",
            "beginner-friendly": "who excels at explaining complex topics simply",
            "persuasive": "with strong persuasive writing skills",
            "educational": "focused on teaching and knowledge transfer",
            "entertaining": "who writes in an engaging, entertaining style",
        }

        # Style customization
        style_map = {
            "informative": "clear, well-structured, and informative",
            "tutorial": "step-by-step, practical, and actionable",
            "analytical": "analytical, data-driven, and thorough",
            "narrative": "story-driven and engaging",
            "listicle": "organized in clear, digestible points",
            "comparison": "focused on comparisons and evaluations",
            "guide": "comprehensive and reference-worthy",
        }

        # Audience customization
        audience_map = {
            "beginners": "Write for complete beginners, avoiding jargon and explaining concepts clearly.",
            "intermediate": "Write for readers with some background knowledge.",
            "advanced": "Write for experienced practitioners who appreciate technical depth.",
            "business": "Write for business professionals focusing on practical applications.",
            "developers": "Write for software developers with technical expertise.",
            "general": "Write for a general audience with varied backgrounds.",
        }

        tone_desc = tone_map.get(directives["tone"], tone_map["professional"])
        style_desc = style_map.get(directives["style"], style_map["informative"])
        audience_desc = audience_map.get(
            directives["audience"], audience_map["general"]
        )

        system_message = f"{base_message} {tone_desc}. Your writing style is {style_desc}. {audience_desc}"

        # Add formatting instructions
        system_message += " Use markdown for formatting (e.g., # for titles, ## for headings, * for lists, `code` for inline code)."

        return system_message

    def build_enhanced_prompt(
        self, state: WorkflowState, directives: Dict[str, str]
    ) -> str:
        """Build a customized prompt based on directives and research."""

        clean_topic = directives["clean_topic"]
        content_format = directives["format"]
        length = directives["length"]

        # Length guidelines
        length_map = {
            "brief": "Write a concise article (500-800 words) that covers the key points.",
            "standard": "Write a standard-length article (800-1500 words) with good coverage.",
            "comprehensive": "Write a comprehensive article (1500-3000 words) with thorough coverage.",
            "detailed": "Write a detailed, in-depth article (2000+ words) covering all aspects.",
        }

        # Format guidelines
        format_map = {
            "article": "Structure as a traditional article with introduction, main sections, and conclusion.",
            "tutorial": "Structure as a step-by-step tutorial with clear instructions and examples.",
            "guide": "Structure as a comprehensive guide with sections covering different aspects.",
            "listicle": "Structure as a numbered or bulleted list with explanations for each point.",
            "comparison": "Structure as a comparison piece, analyzing different options or approaches.",
            "review": "Structure as a review, evaluating features, pros, cons, and recommendations.",
            "howto": "Structure as a how-to guide with actionable steps and practical advice.",
        }

        length_instruction = length_map.get(length, length_map["comprehensive"])
        format_instruction = format_map.get(content_format, format_map["article"])

        prompt = f"""Write a high-quality blog post on the topic: '{clean_topic}'

CONTENT GUIDELINES:
- {length_instruction}
- {format_instruction}
- Base your content on the provided research brief
- Ensure accuracy and cite key insights from the research
- Create engaging, valuable content for the target audience

RESEARCH BRIEF:
{json.dumps(state.research_brief, indent=2)}

ADDITIONAL REQUIREMENTS:
- Use proper markdown formatting
- Include relevant headings and subheadings
- Make the content scannable with bullet points and lists where appropriate
- Ensure the content flows logically from introduction to conclusion
- Focus on providing value and actionable insights

Now write the complete blog post in markdown format:"""

        return prompt

    def execute(self, state: WorkflowState) -> WorkflowState:
        if not state.research_brief:
            logger.error("Cannot run Writing Agent: Research brief is missing.")
            state.log_entry("Error: Writing Agent cannot run without a research brief.")
            return state

        logger.info("--- Starting Enhanced Writing Agent ---")
        state.status = "WRITING"
        state.log_entry("Writing Agent: Started with directive parsing.")

        # Parse directives from topic
        directives = self.parse_topic_directives(state.initial_topic)
        logger.info(f"Parsed directives: {directives}")
        state.log_entry(
            f"Writing Agent: Parsed directives - tone: {directives['tone']}, style: {directives['style']}, length: {directives['length']}"
        )

        # Build enhanced system message and prompt
        system_message = self.build_enhanced_system_message(directives)
        prompt = self.build_enhanced_prompt(state, directives)

        # Generate content
        content = query_llm(
            self.llm_service, state, prompt, system_message, model=self.llm_model
        )

        # Since Editor Agent is disabled, we'll produce final content directly
        state.draft_content = content
        state.final_content = content  # Set final content since no editor

        logger.info("Successfully created blog post with enhanced directives.")
        state.log_entry("Writing Agent: Final content created (Editor Agent disabled).")
        logger.info("--- Finished Enhanced Writing Agent ---")

        return state
