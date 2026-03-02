"""
Fact extraction and validation module.

This module provides functionality to extract key facts from documents
and validate them using multiple LLM agents with majority voting.
"""

from utils.agent import Agent
from utils.json_helper import extract_json


def extract_and_validate_facts(
    paper_content: str,
    extraction_agent: Agent,
    validation_agents: list[Agent],
) -> list[dict]:
    """
    Extract key facts from a paper and validate them via majority vote.

    Args:
        paper_content: Raw text content of the document
        extraction_agent: Pre-configured Agent for fact extraction
        validation_agents: List of pre-configured Agents for validation

    Returns:
        List of accepted facts, each containing:
        - fact: The key fact string
        - reason: Why it's a key fact
        - category: The category it belongs to

    Raises:
        ValueError: If no validation agents provided or JSON parsing fails
        RuntimeError: If extraction or validation fails
    """
    if not validation_agents:
        raise ValueError("At least one validation agent is required")

    raw_facts = _extract_facts(extraction_agent, paper_content)

    if not raw_facts:
        return []

    formatted_facts = _format_facts_for_validation(raw_facts)

    validation_results = _validate_facts(
        validation_agents, paper_content, formatted_facts
    )

    filtered_facts = _filter_by_majority_vote(raw_facts, validation_results)

    return filtered_facts


def _extract_facts(agent: Agent, paper_content: str) -> list[dict]:
    """Extract facts from paper using extraction agent."""
    response = agent.send_message(paper_content)
    facts = extract_json(response)

    if facts is None:
        raise ValueError("Failed to extract facts: JSON parsing returned None")

    if not isinstance(facts, list):
        raise ValueError(f"Expected list of facts, got {type(facts)}: {facts}")

    return facts


def _format_facts_for_validation(facts: list[dict]) -> str:
    """Format facts as numbered list with fact/reason/category."""
    formatted = []
    for i, fact in enumerate(facts, 1):
        formatted.append(
            f"{i}:\n"
            f"Fact: {fact['fact']}\n"
            f"Reason: {fact['reason']}\n"
            f"Category: {fact['category']}\n"
        )
    return "\n".join(formatted)


def _validate_facts(
    agents: list[Agent],
    paper_content: str,
    formatted_facts: str,
) -> list[dict]:
    """Run validation on all agents."""
    results = []
    for agent in agents:
        response = agent.send_messages(
            [
                f"The paper:\n\n{paper_content}",
                f"The list of keyfacts\n{formatted_facts}",
            ]
        )
        result = extract_json(response)
        results.append(result)
    return results


def _filter_by_majority_vote(
    facts: list[dict],
    validation_results: list[dict],
) -> list[dict]:
    """Keep facts accepted by >50% of validators."""
    filtered = []
    num_validators = len(validation_results)
    threshold = num_validators / 2

    for i, fact in enumerate(facts):
        fact_num = str(i + 1)
        accepted_count = sum(
            1
            for result in validation_results
            if result.get(fact_num, {}).get("response") == "yes"
        )

        if accepted_count > threshold:
            filtered.append(fact)

    return filtered
