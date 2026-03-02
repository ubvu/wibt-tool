#!/usr/bin/env python3
"""Test script to run fact extraction on a paper."""

import os
import sys
from pathlib import Path

sys.path.insert(0, "src")

from dotenv import load_dotenv
from utils.open_webui import OpenWebuiClient
from utils.openai_client import OpenAIClient
from utils.agent import Agent
from factuality.extraction import extract_and_validate_facts

# Load environment variables
load_dotenv()

# Get paper file path from command line
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <paper_file.md>")
    sys.exit(1)

paper_file_path = sys.argv[1]

# Read the paper
with open(paper_file_path, "r") as f:
    paper_content = f.read()

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
    raise ValueError(
        f"Unknown DEFAULT_API: {default_api}. Must be 'OpenWebUI' or 'OpenAI'"
    )

# Load prompts
with open("prompts/factuality_evaluation/general/key_fact_generation.txt", "r") as file:
    extraction_prompt = file.read()

with open("prompts/factuality_evaluation/general/key_fact_validation.txt", "r") as file:
    validation_prompt = file.read()

# Initialize extraction agent
extraction_agent = Agent(
    model=os.getenv("DEFAULT_FACT_EXTRACTION_MODEL"),
    system_prompt=extraction_prompt,
    llm_endpoint=client,
    temperature=0.1,
    history=-1,
)

# Initialize validation agents (3 validators)
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

# Run extraction
print("Extracting facts...")
facts = extract_and_validate_facts(
    paper_content=paper_content,
    extraction_agent=extraction_agent,
    validation_agents=validation_agents,
)

# Print results
print(f"\nExtracted {len(facts)} facts:")
for i, fact in enumerate(facts, 1):
    print(f"\n{i}. {fact['fact']}")
    print(f"   Reason: {fact['reason']}")
    print(f"   Category: {fact['category']}")
