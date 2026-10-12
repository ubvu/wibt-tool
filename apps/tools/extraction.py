import argparse
import json
from wibt_tool.agent_factory import AgentFactory
from wibt_tool.config import AppConfig
from wibt_tool.logic.factuality.extraction import extract_and_validate_facts
from wibt_tool.prompt_manager import PromptManager
from wibt_tool.utils.openai_client import OpenAIClient

parser = argparse.ArgumentParser(
    prog='extraction.py',
    description='Extracts and validates facts from a document'
)

parser.add_argument('-i', '--input-file', help='path of the paper to extract facts from', required=True)
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

# Initialize extraction agent
extraction_agent = agent_factory.create_fact_extractor_agent(args.factuality_context)

# Initialize validation agents
validation_agents = agent_factory.create_fact_validator_agents(args.factuality_context)

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
