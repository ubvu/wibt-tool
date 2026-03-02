#!/usr/bin/env python3
"""Test suite for json_helper module."""

import sys

sys.path.insert(0, "src")

import pytest
from pydantic import BaseModel, Field
from utils.json_helper import (
    extract_json_block,
    find_json_markers,
    extract_json,
    validate_json,
    extract_and_validate_json,
    KeyFact,
)


# Test models for validation
class SimpleModel(BaseModel):
    name: str
    value: int


class OptionalFieldModel(BaseModel):
    required_field: str
    optional_field: str = Field(default="default")


class NestedModel(BaseModel):
    id: int
    data: dict


# ============================================================================
# Tests for extract_json_block
# ============================================================================


class TestExtractJsonBlock:
    """Tests for extract_json_block function."""

    def test_extract_json_markdown_block(self):
        """Test extracting JSON from markdown code block with json language tag."""
        text = '```json\n{\n  "key": "value"\n}\n```'
        result = extract_json_block(text)
        assert result == '{\n  "key": "value"\n}'

    def test_extract_json_markdown_block_no_language(self):
        """Test extracting JSON from markdown code block without language tag."""
        text = '```\n{\n  "key": "value"\n}\n```'
        result = extract_json_block(text)
        assert result == '{\n  "key": "value"\n}'

    def test_extract_json_markdown_block_trailing_whitespace(self):
        """Test that trailing whitespace is stripped."""
        text = '```json\n{\n  "key": "value"\n}\n```  '
        result = extract_json_block(text)
        assert result == '{\n  "key": "value"\n}'

    def test_extract_plain_json(self):
        """Test returning plain JSON without markdown block."""
        text = '{"key": "value"}'
        result = extract_json_block(text)
        assert result == '{"key": "value"}'

    def test_extract_json_with_comments_in_block(self):
        """Test extracting JSON from markdown block with surrounding text."""
        text = 'Here is the JSON:\n```json\n{\n  "key": "value"\n}\n```'
        result = extract_json_block(text)
        assert result == '{\n  "key": "value"\n}'

    def test_extract_first_block_only(self):
        """Test that only the first JSON block is extracted."""
        text = """```json
{"first": true}
```
Some text
```json
{"second": true}
```"""
        result = extract_json_block(text)
        assert result == '{"first": true}'

    def test_extract_with_extra_newlines(self):
        """Test extracting JSON with extra newlines in block."""
        text = '```json\n\n\n{\n  "key": "value"\n}\n\n```'
        result = extract_json_block(text)
        assert result == '{\n  "key": "value"\n}'

    def test_no_json_block(self):
        """Test with text that has no JSON block."""
        text = "This is just plain text with no JSON"
        result = extract_json_block(text)
        assert result == "This is just plain text with no JSON"

    def test_empty_string(self):
        """Test with empty string."""
        text = ""
        result = extract_json_block(text)
        assert result == ""

    def test_json_block_with_mixed_case(self):
        """Test that code block tag is case-insensitive."""
        text = '```JSON\n{\n  "key": "value"\n}\n```'
        result = extract_json_block(text)
        assert result == '```JSON\n{\n  "key": "value"\n}\n```'


# ============================================================================
# Tests for find_json_markers
# ============================================================================


class TestFindJsonMarkers:
    """Tests for find_json_markers function."""

    def test_single_json_object(self):
        """Test finding single JSON object."""
        text = '{"key": "value"}'
        result = find_json_markers(text)
        assert result == [0]

    def test_no_json_object(self):
        """Test with no JSON objects."""
        text = "Just plain text"
        result = find_json_markers(text)
        assert result == []

    def test_multiple_json_objects(self):
        """Test finding multiple JSON objects."""
        text = '{"a": 1} {"b": 2}'
        result = find_json_markers(text)
        assert result == [0, 9]

    def test_nested_json_objects(self):
        """Test finding markers with nested objects."""
        text = '{"outer": {"inner": "value"}}'
        result = find_json_markers(text)
        assert result == [0, 10]

    def test_json_in_text(self):
        """Test finding JSON object embedded in text."""
        text = 'Here is some text: {"key": "value"}: more text'
        result = find_json_markers(text)
        assert result == [19]

    def test_unmatched_braces(self):
        """Test with unmatched opening braces."""
        text = '{"key": "value"'
        result = find_json_markers(text)
        assert result == []

    def test_unmatched_closing_braces(self):
        """Test with unmatched closing braces."""
        text = '"key": "value"}'
        result = find_json_markers(text)
        assert result == []

    def test_deeply_nested_json(self):
        """Test with deeply nested JSON objects."""
        text = '{"a": {"b": {"c": {"d": "value"}}}}'
        result = find_json_markers(text)
        assert result == [0, 6, 12, 18]

    def test_json_with_arrays(self):
        """Test JSON objects containing arrays."""
        text = '{"items": [1, 2, 3]}'
        result = find_json_markers(text)
        assert result == [0]

    def test_json_with_strings_containing_braces(self):
        """Test JSON with brace characters in string values."""
        text = '{"key": "{value}"}'
        result = find_json_markers(text)
        assert result == [0, 9]

    def test_empty_json_object(self):
        """Test with empty JSON object."""
        text = "{}"
        result = find_json_markers(text)
        assert result == [0]

    def test_multiple_separate_objects(self):
        """Test with multiple separate JSON objects."""
        text = '{"a": 1} text {"b": 2} more {"c": 3}'
        result = find_json_markers(text)
        assert result == [0, 14, 28]


# ============================================================================
# Tests for extract_json
# ============================================================================


class TestExtractJson:
    """Tests for extract_json function."""

    def test_direct_json_parsing(self):
        """Test direct JSON parsing without markdown."""
        text = '{"key": "value"}'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_direct_json_parsing_with_numbers(self):
        """Test parsing JSON with numeric values."""
        text = '{"count": 42, "price": 19.99}'
        result = extract_json(text)
        assert result == {"count": 42, "price": 19.99}

    def test_direct_json_parsing_with_nested(self):
        """Test parsing nested JSON."""
        text = '{"user": {"name": "John", "age": 30}}'
        result = extract_json(text)
        assert result == {"user": {"name": "John", "age": 30}}

    def test_direct_json_parsing_with_arrays(self):
        """Test parsing JSON with arrays."""
        text = '{"items": [1, 2, 3], "tags": ["a", "b"]}'
        result = extract_json(text)
        assert result == {"items": [1, 2, 3], "tags": ["a", "b"]}

    def test_markdown_block_extraction(self):
        """Test extraction from markdown code block."""
        text = '```json\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_markdown_block_extraction_no_language(self):
        """Test extraction from markdown block without language tag."""
        text = '```\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_json_marker_extraction(self):
        """Test extraction using JSON markers."""
        text = 'Some text before {"key": "value"} after text'
        result = extract_json(text)
        assert result is None

    def test_invalid_json_returns_none(self):
        """Test that invalid JSON returns None."""
        text = '{"key": }'
        result = extract_json(text)
        assert result is None

    def test_empty_string_returns_none(self):
        """Test that empty string returns None."""
        result = extract_json("")
        assert result is None

    def test_plain_text_returns_none(self):
        """Test that plain text returns None."""
        text = "This is just plain text"
        result = extract_json(text)
        assert result is None

    def test_json_parsing_with_boolean_values(self):
        """Test parsing JSON with boolean values."""
        text = '{"active": true, "deleted": false}'
        result = extract_json(text)
        assert result == {"active": True, "deleted": False}

    def test_json_parsing_with_null_values(self):
        """Test parsing JSON with null values."""
        text = '{"value": null}'
        result = extract_json(text)
        assert result == {"value": None}

    def test_json_parsing_with_unicode(self):
        """Test parsing JSON with unicode characters."""
        text = '{"message": "Hello 世界 🌍"}'
        result = extract_json(text)
        assert result == {"message": "Hello 世界 🌍"}

    def test_direct_parsing_preferred_over_markdown(self):
        """Test that direct parsing is tried first."""
        text = '{"key": "direct"} ```json {"key": "markdown"} ```'
        result = extract_json(text)
        assert result is None

    def test_markdown_fallback_when_direct_fails(self):
        """Test markdown extraction when direct parsing fails."""
        text = '```json\n{"key": "value"}\n```'
        result = extract_json(text)
        assert result == {"key": "value"}

    def test_marker_extraction_as_last_fallback(self):
        """Test JSON marker extraction as last fallback."""
        text = 'prefix {"key": "value"}'
        result = extract_json(text)
        assert result == {"key": "value"}


class TestExtractJsonWithValidation:
    """Tests for extract_json with Pydantic model validation."""

    def test_extract_and_validate_valid_data(self):
        """Test successful extraction and validation."""
        text = '{"name": "John", "value": 42}'
        result = extract_json(text, SimpleModel)
        assert result is not None
        assert result.name == "John"
        assert result.value == 42

    def test_extract_and_validate_invalid_data_missing_field(self):
        """Test validation fails when required field is missing."""
        text = '{"name": "John"}'
        result = extract_json(text, SimpleModel)
        assert result is None

    def test_extract_and_validate_invalid_data_wrong_type(self):
        """Test validation fails when field has wrong type."""
        text = '{"name": "John", "value": "not a number"}'
        result = extract_json(text, SimpleModel)
        assert result is None

    def test_extract_markdown_and_validate(self):
        """Test extraction from markdown and validation."""
        text = '```json\n{"name": "Jane", "value": 100}\n```'
        result = extract_json(text, SimpleModel)
        assert result is not None
        assert result.name == "Jane"
        assert result.value == 100

    def test_extract_marker_and_validate(self):
        """Test extraction using markers and validation."""
        text = 'Here is data: {"name": "Bob", "value": 50}'
        result = extract_json(text, SimpleModel)
        assert result is not None
        assert result.name == "Bob"
        assert result.value == 50


# ============================================================================
# Tests for validate_json
# ============================================================================


class TestValidateJson:
    """Tests for validate_json function."""

    def test_validate_valid_data(self):
        """Test validation of valid data."""
        data = {"name": "John", "value": 42}
        result = validate_json(data, SimpleModel)
        assert result is not None
        assert result.name == "John"
        assert result.value == 42

    def test_validate_missing_required_field(self):
        """Test validation fails with missing required field."""
        data = {"name": "John"}
        result = validate_json(data, SimpleModel)
        assert result is None

    def test_validate_wrong_type(self):
        """Test validation fails with wrong field type."""
        data = {"name": "John", "value": "string"}
        result = validate_json(data, SimpleModel)
        assert result is None

    def test_validate_with_optional_field(self):
        """Test validation with optional field."""
        data = {"required_field": "value"}
        result = validate_json(data, OptionalFieldModel)
        assert result is not None
        assert result.required_field == "value"
        assert result.optional_field == "default"

    def test_validate_with_optional_field_provided(self):
        """Test validation when optional field is provided."""
        data = {"required_field": "value", "optional_field": "custom"}
        result = validate_json(data, OptionalFieldModel)
        assert result is not None
        assert result.optional_field == "custom"

    def test_validate_with_nested_data(self):
        """Test validation with nested data."""
        data = {"id": 1, "data": {"key": "value"}}
        result = validate_json(data, NestedModel)
        assert result is not None
        assert result.id == 1
        assert result.data == {"key": "value"}

    def test_validate_with_keyfact_model(self):
        """Test validation with KeyFact model."""
        data = {
            "fact": "Pydantic is great",
            "reason": "It provides validation",
            "category": "tools",
        }
        result = validate_json(data, KeyFact)
        assert result is not None
        assert result.fact == "Pydantic is great"
        assert result.reason == "It provides validation"
        assert result.category == "tools"

    def test_validate_empty_dict(self):
        """Test validation with empty dict."""
        data = {}
        result = validate_json(data, SimpleModel)
        assert result is None

    def test_validate_extra_fields(self):
        """Test validation with extra fields (should pass for Pydantic)."""
        data = {"name": "John", "value": 42, "extra": "field"}
        result = validate_json(data, SimpleModel)
        assert result is not None


# ============================================================================
# Tests for extract_and_validate_json
# ============================================================================


class TestExtractAndValidateJson:
    """Tests for extract_and_validate_json function."""

    def test_successful_extraction_and_validation(self):
        """Test successful extraction and validation."""
        text = '{"name": "John", "value": 42}'
        result = extract_and_validate_json(text, SimpleModel)
        assert result is not None
        assert result.name == "John"
        assert result.value == 42

    def test_extraction_success_validation_failure(self):
        """Test extraction succeeds but validation fails."""
        text = '{"name": "John"}'  # Missing required field
        result = extract_and_validate_json(text, SimpleModel)
        assert result is None

    def test_extraction_failure(self):
        """Test when extraction fails."""
        text = "Not JSON at all"
        result = extract_and_validate_json(text, SimpleModel)
        assert result is None

    def test_markdown_extraction_and_validation(self):
        """Test extraction from markdown and validation."""
        text = '```json\n{"name": "Jane", "value": 100}\n```'
        result = extract_and_validate_json(text, SimpleModel)
        assert result is not None
        assert result.name == "Jane"
        assert result.value == 100

    def test_marker_extraction_and_validation(self):
        """Test extraction using markers and validation."""
        text = 'Data: {"name": "Bob", "value": 50}'
        result = extract_and_validate_json(text, SimpleModel)
        assert result is not None
        assert result.name == "Bob"
        assert result.value == 50

    def test_invalid_json_structure(self):
        """Test with invalid JSON structure."""
        text = '{"name": }'
        result = extract_and_validate_json(text, SimpleModel)
        assert result is None

    def test_with_keyfact_model(self):
        """Test with KeyFact model."""
        text = '{"fact": "Test fact", "reason": "Test reason", "category": "test"}'
        result = extract_and_validate_json(text, KeyFact)
        assert result is not None
        assert result.fact == "Test fact"
        assert result.reason == "Test reason"
        assert result.category == "test"

    def test_with_nested_model(self):
        """Test with nested model."""
        text = '{"id": 123, "data": {"nested": true}}'
        result = extract_and_validate_json(text, NestedModel)
        assert result is not None
        assert result.id == 123
        assert result.data == {"nested": True}


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_very_large_json(self):
        """Test with large JSON object."""
        large_data = '{"' + '", "'.join([f"key{i}" for i in range(100)]) + '": "value"}'
        result = extract_json(large_data)
        assert result is None

    def test_json_with_special_characters(self):
        """Test JSON with special characters."""
        text = '{"escaped": "line\\nbreak", "tab": "col\\tumb"}'
        result = extract_json(text)
        assert result == {"escaped": "line\nbreak", "tab": "col\tumb"}

    def test_json_with_empty_strings(self):
        """Test JSON with empty string values."""
        text = '{"empty": "", "zero": 0, "false": false}'
        result = extract_json(text)
        assert result == {"empty": "", "zero": 0, "false": False}

    def test_json_in_code_block_with_special_chars(self):
        """Test JSON in code block with special characters."""
        text = '```json\n{"special": "<>&"}\n```'
        result = extract_json(text)
        assert result == {"special": "<>&"}

    def test_multiple_opening_braces(self):
        """Test with multiple consecutive opening braces."""
        text = '{{"key": "value"}}'
        result = find_json_markers(text)
        assert result == [0, 1]

    def test_json_with_escaped_quotes(self):
        """Test JSON with escaped quotes in strings."""
        text = '{"quote": "He said \\"hello\\""}'
        result = extract_json(text)
        assert result == {"quote": 'He said "hello"'}

    def test_empty_json_object_in_markdown(self):
        """Test empty JSON object in markdown block."""
        text = "```json\n{}\n```"
        result = extract_json(text)
        assert result == {}

    def test_json_with_only_whitespace(self):
        """Test JSON that is only whitespace."""
        text = "   \n  \t  "
        result = extract_json(text)
        assert result is None

    def test_unicode_in_markdown_json(self):
        """Test Unicode characters in markdown JSON."""
        text = '```json\n{\n  "greeting": "こんにちは",\n  "emoji": "🎉"\n}\n```'
        result = extract_json(text)
        assert result == {"greeting": "こんにちは", "emoji": "🎉"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
