"""
JSON extraction and validation utilities using Pydantic for schema validation.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class KeyFact(BaseModel):
    """Model for key fact extraction."""

    fact: str = Field(..., description="The extracted fact")
    reason: str = Field(..., description="Reason for extracting this fact")
    category: str = Field(..., description="Category of the fact")


def extract_json_block(text: str) -> Optional[str]:
    """
    Extract JSON from markdown code blocks or return the text if it's already JSON.

    Args:
        text: Input text that may contain JSON in markdown code blocks

    Returns:
        Extracted JSON string or None if no JSON block found
    """
    # Try to extract from markdown code blocks first
    json_block_pattern = r"```(?:json)?\s*\n([\s\S]*?)\n```"
    match = re.search(json_block_pattern, text)
    if match:
        return match.group(1).strip()

    # If no markdown block, return the text as-is
    return text


def find_json_markers(text: str) -> List[int]:
    """
    Find all JSON object markers in text (braces that look like JSON objects).

    Args:
        text: Input text to search for JSON markers

    Returns:
        List of starting indices of JSON-like structures
    """
    markers = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            # Try to find a matching closing brace
            brace_count = 0
            j = i
            while j < len(text):
                if text[j] == "{":
                    brace_count += 1
                elif text[j] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        markers.append(i)
                        break
                j += 1
        i += 1
    return markers


def extract_json(text: str, model: Optional[type[BaseModel]] = None) -> Optional[Any]:
    """
    Extract JSON from text with multiple fallback strategies and optional validation.

    Strategy 1: Direct JSON parsing
    Strategy 2: Extract from markdown code blocks
    Strategy 3: Find and parse JSON-like structures

    Args:
        text: Input text that may contain JSON
        model: Optional Pydantic model to validate against

    Returns:
        Parsed JSON dict or validated Pydantic model instance, or None if extraction/validation fails
    """
    # Strategy 1: Try direct parsing
    try:
        data = json.loads(text)
        if model:
            return validate_json(data, model)
        return data
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code blocks
    json_block = extract_json_block(text)
    if json_block:
        try:
            data = json.loads(json_block)
            if model:
                return validate_json(data, model)
            return data
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find JSON markers and try to parse
    markers = find_json_markers(text)
    for marker in markers:
        try:
            candidate = text[marker:]
            data = json.loads(candidate)
            if model:
                return validate_json(data, model)
            return data
        except json.JSONDecodeError:
            continue

    print("Failed to extract JSON from text")
    return None


def validate_json(data: Any, model: type[BaseModel]) -> Optional[BaseModel]:
    """
    Validate JSON data against a Pydantic model.

    Args:
        data: JSON data to validate
        model: Pydantic model to validate against

    Returns:
        Validated Pydantic model instance or None if validation fails
    """
    try:
        return model(**data)
    except Exception:
        print("Failed to validate JSON against schema")
        return None


def extract_and_validate_json(text: str, model: type[BaseModel]) -> Optional[BaseModel]:
    """
    Extract JSON from text and validate against a Pydantic model.

    Args:
        text: Input text containing JSON
        model: Pydantic model to validate against

    Returns:
        Validated Pydantic model instance or None if extraction/validation fails
    """
    json_data = extract_json(text)
    if json_data is None:
        return None

    return validate_json(json_data, model)
