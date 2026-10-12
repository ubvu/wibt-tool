import argparse
import json
from wibt_tool.agents import Agent
from wibt_tool.config import AppConfig
from wibt_tool.logic.factuality.alignment import align_facts_to_summary
from wibt_tool.logic.factuality.extraction import extract_and_validate_facts
from wibt_tool.prompt_manager import PromptManager
from wibt_tool.utils.openai_client import OpenAIClient

parser = argparse.ArgumentParser(
    prog='alignment.py',
    description='Aligns facts to a summary'
)

parser.add_argument('-i', '--input-file', help='path of the paper to align against', required=True)
parser.add_argument('-s', '--summary-file', help='path of the summary to align facts to', required=True)
parser.add_argument('-fc', '--factuality-context', help='type of prompts to use for factuality related agents', required=True)

args = parser.parse_args()

try:
    config = AppConfig.from_env()
    print("Configuration loaded successfully")
except Exception as e:
    print(f"Configuration error: {e}")

llm_endpoint = OpenAIClient(token=config.api_token, endpoint=config.api_url)
prompt_manager = PromptManager(config=config)
agent_factory = AgentFactory(config=config, prompt_manager=prompt_manager, llm_endpoint=llm_endpoint)

# load the paper
with open(args.input_file, "r") as f:
    paper_content = f.read()

# load the summary
with open(args.summary_file, "r") as f:
    summary = f.read()

# Initialize extraction agent
extraction_agent = agent_factory.create_fact_extractor_agent(args.factuality_context)

# Initialize validation agents
validation_agents = agent_factory.create_fact_validator_agents(args.factuality_context)

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
alignment_agent = agent_factory.create_adjudicator_agent(args.factuality_context)

print("Aligning facts to summary...")
result = align_facts_to_summary(fact_strings, summary, alignment_agent)

print(f"\nAligned facts: {len(result['aligned_facts'])}")
for fact in result["aligned_facts"]:
    print(f"  ✓ {fact}")

print(f"\nMisaligned facts: {len(result['misaligned_facts'])}")
for fact in result["misaligned_facts"]:
    print(f"  ✗ {fact}")

print(f"\nCompleteness score: {result['completeness_score']}/5")
