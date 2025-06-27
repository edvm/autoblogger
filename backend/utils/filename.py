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

"""Filename sanitization utilities."""

import unicodedata
import re


def sanitize_filename(
    filename: str, max_length: int = 240, preserve_extension: bool = False
) -> str:
    """Creates a filesystem-safe filename from a string.

    This function handles:
    - Removing or replacing unsafe characters
    - Truncating long filenames to prevent "File name too long" errors
    - Preserving word boundaries when possible during truncation
    - Handling Unicode characters properly
    - Preventing filenames that end with problematic characters

    Args:
        filename: The string to sanitize for use as a filename.
        max_length: Maximum length for the sanitized filename (default: 240).
        preserve_extension: If True, preserve file extension when truncating.

    Returns:
        A string that is safe to use as a filename on most filesystems.

    Examples:
        >>> sanitize_filename("My Blog Topic")
        'my_blog_topic'

        >>> sanitize_filename("Very Long Topic " * 50)  # Returns truncated version
        'very_long_topic_very_long_topic_...'

        >>> sanitize_filename("document.pdf", preserve_extension=True)
        'document.pdf'
    """
    if not filename or not filename.strip():
        return "untitled"

    # Handle extension preservation
    extension = ""
    name = filename
    if preserve_extension and "." in filename:
        name, extension = filename.rsplit(".", 1)
        extension = f".{extension}"
        # Adjust max_length to account for extension
        max_length = max_length - len(extension)

    # Normalize Unicode characters (NFD normalization followed by filtering)
    name = unicodedata.normalize("NFD", name)

    # Keep only alphanumeric characters, spaces, hyphens, underscores, and basic Unicode
    # This allows international characters while filtering out problematic ones
    safe_chars = []
    for char in name:
        if char.isalnum() or char in (" ", "-", "_"):
            safe_chars.append(char)
        elif not unicodedata.combining(char):  # Skip combining characters
            # Replace other characters with underscores, but avoid consecutive underscores
            if safe_chars and safe_chars[-1] != "_":
                safe_chars.append("_")

    sanitized = "".join(safe_chars).strip()

    # Replace multiple consecutive spaces/underscores with single underscore
    sanitized = re.sub(r"[\s_]+", "_", sanitized)

    # Convert to lowercase for consistency
    sanitized = sanitized.lower()

    # Remove leading/trailing underscores and hyphens
    sanitized = sanitized.strip("_-")

    # Handle empty result
    if not sanitized:
        sanitized = "untitled"

    # Truncate if necessary
    if len(sanitized) > max_length:
        truncated = sanitized[:max_length]

        # Try to find the last underscore (word boundary) in the last portion
        # to avoid cutting in the middle of a word
        search_start = max(0, max_length - 50)  # Look in last 50 chars
        last_underscore = truncated.rfind("_", search_start)

        # Only use the word boundary if it's not too far back
        if last_underscore > max_length - 100:
            truncated = truncated[:last_underscore]

        # Clean up any trailing problematic characters
        sanitized = truncated.rstrip("_-")

    # Final check - ensure we still have something
    if not sanitized:
        sanitized = "untitled"

    return sanitized + extension


def sanitize_filename_for_download(topic: str, usage_id: int) -> str:
    """Sanitize a topic for use in downloadable filenames with usage ID.

    This is specifically designed for the API download endpoint where we need
    to append a usage ID and file extension.

    Args:
        topic: The blog topic to sanitize.
        usage_id: The usage ID to append.

    Returns:
        A safe filename in the format: {sanitized_topic}_{usage_id}.md
    """
    # Reserve space for _{usage_id}.md
    usage_suffix = f"_{usage_id}.md"
    max_topic_length = 240 - len(usage_suffix)

    sanitized_topic = sanitize_filename(topic, max_length=max_topic_length)
    return f"{sanitized_topic}{usage_suffix}"
