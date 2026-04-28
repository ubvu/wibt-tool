import os
import sys
from pathlib import Path
import csv
import argparse
import json

sys.path.insert(0, "src")

from utils.openai_client import OpenAIClient

from config import AppConfig
from prompt_manager import PromptManager
from agent_factory import AgentFactory

from translation_orchestrator import TranslationOrchestrator


parser = argparse.ArgumentParser(
                    prog='summary.py',
                    description='Creates a summary of a scientific article'
                    )


parser.add_argument('-tc', '--translation-context', help='type of prompts to use for translation related agents', required=True)
parser.add_argument('-i', '--input-file', help='path of the paper to summarize', required=True)
parser.add_argument('-o', '--output-file', help='path of where the summary is stored', required=True)


args = parser.parse_args()

try:
    config = AppConfig.from_env()
    print("Configuration loaded successfully")
except Exception as e:
    print(f"Configuration error: {e}")

llm_endpoint = OpenAIClient(token=config.api_token, endpoint=config.api_url)

prompt_manager = PromptManager(config=config)

agent_factory = AgentFactory(config=config, prompt_manager=prompt_manager, llm_endpoint=llm_endpoint)

# load a test paper, stored in markdown
summary_file_path = args.input_file
with open(summary_file_path, "r") as file:
    summary = file.read()

output_path = args.output_file

translation_context = args.translation_context


translation_orchestrator = TranslationOrchestrator(agent_factory, config)





translation = translation_orchestrator.run(
    summary=summary, 
    translation_ctx=translation_context
)


# print(f"Summary:\n{summary}")
# print(f"Translation:\n{translation}")


with open(output_path, "w") as file:
    file.write(translation)
