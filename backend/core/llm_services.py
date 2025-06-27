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

# This module provides services for interacting with Large Language Models (LLMs),
# specifically leveraging the OpenAI API.
# It includes functionality to initialize an OpenAI client and a core function
# `query_llm` for sending prompts to specified LLM models and retrieving their
# responses.

import openai
from abc import ABC, abstractmethod
from .state import WorkflowState
from configs.config import OPENAI_API_KEY
from configs.logging_config import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

ERROR_FLAG = "fucked up"


class LLMServiceException(Exception):
    """Custom exception for LLM service errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"LLMServiceException: {self.message}"


class LLMUsage:
    """A simple class to encapsulate LLM token usage information."""

    __slots__ = ("total_tokens",)

    def __init__(self, total_tokens: int):
        self.total_tokens = total_tokens

    def __str__(self):
        return f"LLMUsage(total_tokens={self.total_tokens})"


class LLMServiceResponse:
    """Class representing a response from an LLM service."""

    __slots__ = ("content", "usage")

    def __init__(self, content: str | None, usage: LLMUsage | None = None):
        self.content = content
        self.usage = usage

    def __str__(self) -> str:
        return f"LLMServiceResponse(content={self.content}, usage={self.usage})"


class LLMService(ABC):
    """Abstract base class for LLM services."""

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_message: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> LLMServiceResponse:
        """Generates a response from the LLM based on the provided parameters.

        Args:
            prompt (str): The user-facing prompt.
            system_message (str): The system message to set the LLM's persona/role.
            model (str): The model to use (e.g., 'gpt-4o', 'gpt-3.5-turbo').
            temperature (float): Sampling temperature to use.
            max_tokens (int): The maximum number of tokens to generate.

        Returns:
            LLMServiceResponse: An object containing the content and token usage.

        Raises:
            LLMServiceException: If an error occurs during the LLM API call.
        """
        pass


class OpenAIService(LLMService):
    def __init__(self, api_key: str):
        """Initializes the OpenAI client with the provided API key."""
        self.client = openai.OpenAI(api_key=api_key)

    def generate_response(
        self,
        prompt: str,
        system_message: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> LLMServiceResponse:
        """Generates a response from the OpenAI LLM.

        Args:
            prompt (str): The user-facing
                prompt.
            system_message (str): The system message to set the LLM's persona/role.
            model (str): The model to use (e.g., 'gpt-4o', 'gpt-3.5-turbo').
            temperature (float): Sampling temperature to use.
            max_tokens (int): The maximum number of tokens to generate.
        Returns:
            LLMServiceResponse: An object containing the content and token usage.
        Raises:
            LLMServiceException: If an error occurs during the LLM API call.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            token_usage = (
                LLMUsage(response.usage.total_tokens) if response.usage else None
            )
            return LLMServiceResponse(content=content, usage=token_usage)
        except Exception as e:
            logger.error(f"An error occurred while querying the OpenAI API: {e}")
            raise LLMServiceException(f"Error querying OpenAI API: {e}")


def query_llm(
    llm_service: LLMService,
    state: WorkflowState,
    prompt: str,
    system_message: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 4000,
) -> str:
    """Queries an LLM with a given prompt and system message.

    Args:
        llm_service (AbstractLLMService): The LLM service to use for querying.
        state (WorkflowState): The current workflow state (used for logging).
        prompt (str): The user-facing prompt.
        system_message (str): The system message to set the LLM's persona/role.
        model (str): The model to use (e.g., 'gpt-4o', 'gpt-3.5-turbo').
        temperature (float): Sampling temperature to use.
        max_tokens (int): The maximum number of tokens to generate.

    Returns:
        str: The content of the LLM's response, stripped of leading/trailing
             whitespace. Returns "error" if the LLM's response content is
             None or an empty string.

    Raises:
        Exception: If an error occurs during the LLM API call.
    """
    logger.info(f"Querying LLM (model: {model}) via injected service...")
    state.log_entry(
        f"Contacting LLM with model: {model} using {llm_service.__class__.__name__}"
    )

    try:
        response: LLMServiceResponse = llm_service.generate_response(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.content
        token_usage = response.usage

        if token_usage:
            logger.info(
                f"LLM response received. Token usage: {token_usage.total_tokens} tokens."
            )
            state.log_entry(
                f"LLM call successful. Used {token_usage.total_tokens} tokens."
            )

        if content is None or content == "":
            logger.warning(f"LLM returned None or empty content for model {model}.")
            state.log_entry(f"Warning: LLM returned no content for model {model}.")
            return ERROR_FLAG
        return content.strip()

    except Exception as e:
        logger.error(
            f"An error occurred while querying the LLM via service: {e}", exc_info=True
        )
        state.log_entry(f"Error: LLM query failed. Reason: {e}")
        raise
