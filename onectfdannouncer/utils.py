"""
Utility functions for Discord bot operations.
"""

import re


def escape_markdown(text):
    """
    Escape Discord markdown characters to prevent markdown injection.

    Args:
        text (str): The text to escape

    Returns:
        str: The escaped text safe for Discord messages
    """
    if not text:
        return text

    # Discord markdown characters that need escaping
    markdown_chars = [
        "\\",  # Backslash (must be first)
        "*",  # Bold/italic
        "_",  # Italic/underline
        "~",  # Strikethrough
        "`",  # Code
        "|",  # Spoiler
        ">",  # Quote
        "#",  # Header (at start of line)
    ]

    # Escape each character by prefixing with backslash
    escaped_text = text
    for char in markdown_chars:
        escaped_text = escaped_text.replace(char, f"\\{char}")

    return escaped_text


def sanitize_team_name(team_name):
    """
    Sanitize team name for safe display in Discord messages.

    Args:
        team_name (str): The team name to sanitize

    Returns:
        str: The sanitized team name
    """
    if not team_name:
        return "Unknown Team"

    # First escape markdown
    sanitized = escape_markdown(str(team_name))

    # Limit length to prevent message length issues
    max_length = 100
    if len(sanitized) > max_length:
        sanitized = sanitized[: max_length - 3] + "..."

    return sanitized


def sanitize_challenge_name(challenge_name):
    """
    Sanitize challenge name for safe display in Discord messages.

    Args:
        challenge_name (str): The challenge name to sanitize

    Returns:
        str: The sanitized challenge name
    """
    if not challenge_name:
        return "Unknown Challenge"

    # Escape markdown but keep some formatting for challenge names
    sanitized = escape_markdown(str(challenge_name))

    # Limit length
    max_length = 150
    if len(sanitized) > max_length:
        sanitized = sanitized[: max_length - 3] + "..."

    return sanitized
