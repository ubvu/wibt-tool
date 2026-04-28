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

from summary_orchestrator import SummaryOrchestrator
from translation_orchestrator import TranslationOrchestrator


parser = argparse.ArgumentParser(
                    prog='summary.py',
                    description='Creates a summary of a scientific article'
                    )


parser.add_argument('-sc', '--summary-context', help='type of prompts to use for summary related agents', required=True)
parser.add_argument('-fc', '--factuality-context', help='type of prompts to use for factuality related agents', required=True)
parser.add_argument('-tc', '--translation-context', help='type of prompts to use for translation related agents', required=True)
parser.add_argument('-it', '--iterations', help='number of iterations to perform', type=int, required=True)
parser.add_argument('-i', '--input-file', help='path of the paper to summarize', required=True)
parser.add_argument('-o', '--output-file', help='path of where the summary is stored', required=True)
parser.add_argument('-st', '--search-type', help='whether to use prompt refinement (refine) or to use a static prompt (static)', required=True)
parser.add_argument('-oes', '--output-english-summary', help='path of where the untranslated summary is stored')
parser.add_argument('-okf', '--output-key-facts', help='path of where the overview of key-facts are stored')
parser.add_argument('-oh', '--output-history', help='path of where the history is stored')
parser.add_argument('-osh', '--output-score-history', help='path of where the score history is stored')

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
paper_file_path = args.input_file
with open(paper_file_path, "r") as file:
    paper = file.read()

number_of_iterations = args.iterations

output_path = args.output_file
output_english_summary_path = args.output_english_summary
output_key_facts_path = args.output_key_facts
output_history_path = args.output_history
output_score_history_path = args.output_score_history

summary_context = args.summary_context
factuality_context = args.factuality_context
translation_context = args.translation_context

search_method = args.search_type

summary_orchestrator = SummaryOrchestrator(agent_factory, prompt_manager, config, search_method)
translation_orchestrator = TranslationOrchestrator(agent_factory, config)


summary_result = summary_orchestrator.run(
    paper=paper, 
    summary_ctx=summary_context, 
    fact_ctx=factuality_context, 
    iterations=args.iterations
)

summary = summary_result['summary']


translation = translation_orchestrator.run(
    summary=summary, 
    translation_ctx=translation_context
)


print(f"Summary:\n{summary}")
print(f"Translation:\n{translation}")


with open(output_path, "w") as file:
    file.write(translation)

if output_english_summary_path:
    with open(output_english_summary_path, "w") as file:
        file.write(summary) 

if output_history_path:
    with open(output_history_path, "w") as file:
        json.dump(summary_orchestrator._history, file)


fieldnames = ["syntactic_clarity", "jargon", "information_density", "structural_cohesion", "faithfulness", "completeness", "total_score", "prompt", "summary"]
scores = []
for entry in summary_orchestrator._history:
    score = {
        "syntactic_clarity": entry["readability_scores"]["syntactic_clarity"],
        "jargon": entry["readability_scores"]["jargon"], 
        "information_density": entry["readability_scores"]["information_density"], 
        "structural_cohesion": entry["readability_scores"]["structural_cohesion"], 
        "faithfulness": entry["factuality_scores"]["faithfulness"], 
        "completeness": entry["factuality_scores"]["completeness"], 
        "total_score": entry["total_score"], 
        "prompt": entry["prompt"], 
        "summary": entry["summary"]
    }
    scores.append(score)

if output_score_history_path:
    with open(output_score_history_path, "w") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  
        writer.writerows(scores)

if output_key_facts_path:
    with open(output_key_facts_path, "w") as file:
        json.dump(summary_orchestrator._validated_facts, file)