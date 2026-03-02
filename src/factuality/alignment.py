"""
Fact-to-summary alignment module.

This module provides functionality to check if extracted facts are
contained in a summary using LLM-based evaluation.
"""

from utils.agent import Agent
from utils.json_helper import extract_json


def align_facts_to_summary(
    facts: list[str],
    summary: str,
    alignment_agent: Agent,
) -> dict:
    """
    Align extracted facts to a summary and evaluate containment.

    Args:
        facts: List of fact strings to evaluate
        summary: The summary text to compare against
        alignment_agent: Pre-configured Agent for alignment evaluation

    Returns:
        Dictionary containing:
        - aligned_facts: List of facts marked as contained
        - misaligned_facts: List of facts marked as not contained
        - alignment_report: Raw JSON report from LLM
        - completeness_score: Integer score from 0-5

    Raises:
        ValueError: If facts list is empty or JSON parsing fails
        RuntimeError: If alignment evaluation fails
    """
    if not facts:
        raise ValueError("Facts list cannot be empty")

    formatted_facts = _format_facts_for_alignment(facts)

    alignment_report = _perform_alignment(alignment_agent, formatted_facts, summary)

    result = _parse_alignment_report(alignment_report, facts)

    return result


def _format_facts_for_alignment(facts: list[str]) -> str:
    """Format facts as numbered list for alignment prompt."""
    formatted = []
    for i, fact in enumerate(facts, 1):
        formatted.append(f"{i}:\n{fact}\n")
    return "\n".join(formatted)


def _perform_alignment(agent: Agent, formatted_facts: str, summary: str) -> dict:
    """Send alignment request to agent and parse response."""
    response = agent.send_messages(
        [
            f"The list of statements:\n\n{formatted_facts}",
            f"The summary\n{summary}",
        ]
    )
    report = extract_json(response)

    if report is None:
        raise ValueError("Failed to parse alignment report: JSON parsing returned None")

    if not isinstance(report, dict):
        raise ValueError(
            f"Expected dict alignment report, got {type(report)}: {report}"
        )

    return report


def _parse_alignment_report(report: dict, facts: list[str]) -> dict:
    """Parse alignment report and categorize facts."""
    aligned_facts = []
    misaligned_facts = []

    for i, fact in enumerate(facts, 1):
        fact_key = str(i)
        if fact_key not in report:
            raise ValueError(f"Missing alignment result for fact {i}")

        fact_result = report[fact_key]
        contained = fact_result.get("contained", "").lower()

        if contained == "yes":
            aligned_facts.append(fact)
        elif contained == "no":
            misaligned_facts.append(fact)
        else:
            raise ValueError(
                f"Invalid 'contained' value for fact {i}: {contained}. "
                "Expected 'yes' or 'no'."
            )

    return {
        "aligned_facts": aligned_facts,
        "misaligned_facts": misaligned_facts,
        "alignment_report": report,
        "completeness_score": _calculate_completeness(report),
    }


def _calculate_completeness(report: dict) -> int:
    """Calculate completeness score from 0-5."""
    total = len(report)
    if total == 0:
        return 0

    count_yes = sum(1 for value in report.values() if value.get("contained") == "yes")

    return int(5 * (count_yes / total))
