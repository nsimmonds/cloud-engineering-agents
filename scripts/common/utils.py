"""
Common utility functions for cloud engineering scripts.

Provides helper functions used across multiple scripts.
"""

import json
import sys
from typing import Any, Dict, List, Optional


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Prompt user for confirmation before performing an action.

    Args:
        message: Confirmation message to display
        default: Default response if user just presses Enter

    Returns:
        True if user confirms, False otherwise
    """
    default_text = "Y/n" if default else "y/N"
    response = input(f"{message} [{default_text}]: ").strip().lower()

    if not response:
        return default

    return response in ('y', 'yes')


def format_output(data: Any, output_format: str = 'json') -> str:
    """
    Format data for output in various formats.

    Args:
        data: Data to format (dict, list, or other)
        output_format: Output format ('json', 'table', 'text')

    Returns:
        Formatted string representation
    """
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)

    elif output_format == 'table':
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return format_table(data)
        else:
            return str(data)

    else:  # text
        return str(data)


def format_table(data: List[Dict[str, Any]]) -> str:
    """
    Format list of dictionaries as a table.

    Args:
        data: List of dictionaries with consistent keys

    Returns:
        Formatted table string
    """
    if not data:
        return "No data"

    # Get all unique keys
    keys = list(data[0].keys())

    # Calculate column widths
    widths = {key: len(str(key)) for key in keys}
    for row in data:
        for key in keys:
            value_len = len(str(row.get(key, '')))
            widths[key] = max(widths[key], value_len)

    # Create header
    header = " | ".join(str(key).ljust(widths[key]) for key in keys)
    separator = "-+-".join("-" * widths[key] for key in keys)

    # Create rows
    rows = []
    for row in data:
        row_str = " | ".join(str(row.get(key, '')).ljust(widths[key]) for key in keys)
        rows.append(row_str)

    return "\n".join([header, separator] + rows)


def parse_tags(tag_list: Optional[List[str]]) -> Dict[str, str]:
    """
    Parse list of 'key=value' strings into dictionary.

    Args:
        tag_list: List of strings in 'key=value' format

    Returns:
        Dictionary of tag key-value pairs
    """
    if not tag_list:
        return {}

    tags = {}
    for tag in tag_list:
        if '=' in tag:
            key, value = tag.split('=', 1)
            tags[key.strip()] = value.strip()
        else:
            print(f"Warning: Invalid tag format '{tag}', expected 'key=value'", file=sys.stderr)

    return tags


def handle_error(error: Exception, logger: Any, exit_code: int = 1) -> None:
    """
    Handle error with logging and exit.

    Args:
        error: Exception that occurred
        logger: Logger instance
        exit_code: Exit code to use (default: 1)
    """
    logger.error(f"Error: {str(error)}", exc_info=True)
    sys.exit(exit_code)
