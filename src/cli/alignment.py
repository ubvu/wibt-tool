#!/usr/bin/env python3
"""Test script for fact alignment module."""

import os
import sys
from pathlib import Path

sys.path.insert(0, "src")

from dotenv import load_dotenv
from utils.open_webui import OpenWebuiClient
from utils.openai_client import OpenAIClient
from utils.agent import Agent
from factuality.extraction import extract_and_validate_facts
from factuality.alignment import align_facts_to_summary

load_dotenv()

# Get file paths from command line
if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <paper_file.md> <summary_file.md>")
    sys.exit(1)

paper_file_path = sys.argv[1]
summary_file_path = sys.argv[2]

# Read the paper
with open(paper_file_path, "r") as f:
    paper_content = f.read()

# Read the summary
with open(summary_file_path, "r") as f:
    summary = f.read()

# Initialize LLM client based on DEFAULT_API
default_api = os.getenv("DEFAULT_API")

if default_api == "OpenWebUI":
    token = os.getenv("OPEN_WEBUI_TOKEN")
    url = os.getenv("OPEN_WEBUI_URL")
    client = OpenWebuiClient(token, url)
elif default_api == "OpenAI":
    token = os.getenv("OPEN_AI_TOKEN")
    url = os.getenv("OPEN_AI_URL")
    client = OpenAIClient(token, url)
else:
    raise ValueError(f"Unknown DEFAULT_API: {default_api}")

EXTRACTION_PROMPT_PATH = "prompts/factuality_evaluation/general/key_fact_generation.txt"
SUMMARY_PROMPT_PATH = "prompts/summary/fact_extraction.txt"
VALIDATION_PROMPT_PATH = "prompts/factuality_evaluation/general/key_fact_validation.txt"
ALIGNMENT_PROMPT_PATH = "prompts/factuality_evaluation/general/key_fact_alignment.txt"

# Load prompts
with open(EXTRACTION_PROMPT_PATH, "r") as file:
    extraction_prompt = file.read()

with open(VALIDATION_PROMPT_PATH, "r") as file:
    validation_prompt = file.read()

with open(ALIGNMENT_PROMPT_PATH, "r") as file:
    alignment_prompt = file.read()

# Initialize extraction agent
extraction_agent = Agent(
    model=os.getenv("DEFAULT_FACT_EXTRACTION_MODEL"),
    system_prompt=extraction_prompt,
    llm_endpoint=client,
    temperature=0.1,
    history=-1,
)

# Initialize validation agents
validation_agents = []
for i in range(3):
    agent = Agent(
        model=os.getenv("DEFAULT_FACT_VALIDATION_MODEL").split(",")[i % 3],
        system_prompt=validation_prompt,
        llm_endpoint=client,
        temperature=0.1,
        history=-1,
    )
    validation_agents.append(agent)

# Extract facts from paper
print("Extracting facts from paper...")
facts = extract_and_validate_facts(
    paper_content=paper_content,
    extraction_agent=extraction_agent,
    validation_agents=validation_agents,
)

fact_strings = [fact["fact"] for fact in facts]
print(f"Extracted {len(fact_strings)} facts")

# Initialize alignment agent
alignment_agent = Agent(
    model=os.getenv("DEFAULT_ALIGNMENT_MODEL"),
    system_prompt=open(ALIGNMENT_PROMPT_PATH).read(),
    llm_endpoint=client,
    temperature=0,
    history=-1,
)

print("Aligning facts to summary...")
result = align_facts_to_summary(fact_strings, summary, alignment_agent)

print(f"\nAligned facts: {len(result['aligned_facts'])}")
for fact in result["aligned_facts"]:
    print(f"  ✓ {fact}")

print(f"\nMisaligned facts: {len(result['misaligned_facts'])}")
for fact in result["misaligned_facts"]:
    print(f"  ✗ {fact}")

print(f"\nCompleteness score: {result['completeness_score']}/5")
