import os
import sys
import json
from string import Template
from operator import itemgetter
from dotenv import load_dotenv
from utils.open_webui import OpenWebuiClient
from utils.openai_client import OpenAIClient
from utils.agent import Agent, SummaryAgent, ReadEvalAgent, FactEvalAgent, RefineAgent


def create_summary_prompt_overview(summary_prompt):
    summary_agent.set_system_prompt(summary_prompt)
    summary = summary_agent.generate_summary(paper)

    readability_scores = readability_eval_agent.evaluate_summary(summary)
    clarity = int(readability_scores['Syntactic clarity'])
    jargon = int(readability_scores['Jargon'])
    density = int(readability_scores['Information density'])
    cohesion = int(readability_scores['Structural cohesion'])

    readability_score = int(clarity + jargon + density + cohesion)

    factuality_scores = factuality_eval_agent.evaluate_summary(summary, paper)
    faithfulness = int(factuality_scores['faithfulness'])
    completeness = int(factuality_scores['completeness'])

    factuality_score = int(faithfulness + completeness)
    total_score = readability_score + factuality_score

    return {
        "prompt" : summary_prompt,
        "summary" : summary,
        "readability_score" : readability_score,
        "clarity" : clarity,
        "jargon" : jargon,
        "density" : density,
        "cohesion" : cohesion,
        "factuality_score" : factuality_score,
        "faithfulness" : faithfulness,
        "completeness" : completeness,
        "total_score" : total_score
    }
        

load_dotenv() 

# load in token needed to connect to Nebula
token = os.environ.get('OPEN_WEBUI_TOKEN')
url = os.environ.get('OPEN_WEBUI_URL')
llm_endpoint = OpenWebuiClient(token, url)

# use an OpenAI endpoint instead
# token = os.environ.get('OPEN_AI_TOKEN')
# url = os.environ.get('OPEN_AI_URL')
# llm_endpoint = OpenAIClient(token, url)


# load a test paper, stored in markdown
paper_file_path = sys.argv[1]
with open(paper_file_path, "r") as file:
    paper = file.read()

# load prompt templates for the different agents
with open("prompts/summary/evaluate_readability.txt", "r") as file:
    eval_readability_prompt = file.read()

with open("prompts/summary/evaluate_factuality.txt", "r") as file:
    eval_factuality_prompt = file.read()

with open("prompts/summary/refine_prompt.txt", "r") as file:
    refinement_prompt = file.read()

with open("prompts/summary/summarize.txt", "r") as file:
    summary_prompt = file.read()

default_model = os.environ.get('DEFAULT_MODEL')

# set up the models that are used
eval_model = default_model
summary_model = default_model
refine_model = default_model


# create agents, temperature 0 makes them more deterministic, 1 less
summary_agent = SummaryAgent(summary_model, summary_prompt, llm_endpoint, temperature=0)
readability_eval_agent = ReadEvalAgent(eval_model, eval_readability_prompt, llm_endpoint, temperature=0)
factuality_eval_agent = FactEvalAgent(eval_model, eval_factuality_prompt, llm_endpoint, temperature=0)
refine_agent = RefineAgent(refine_model, refinement_prompt, llm_endpoint, temperature=1)

prompts = [create_summary_prompt_overview(summary_prompt)]

iteration = 0
while True:

    print(f"Starting iteration {iteration}")
    print(f"Number of prompts: {len(prompts)}")

    top_prompt = sorted(prompts, key=itemgetter('total_score'), reverse=True)[0]
    print(f"Top prompt:\n{top_prompt}")

    # break conditions
    if iteration >= 10:
        break
    
    if top_prompt['total_score'] >= 30:
        break


    # generate 3 new prompts from the best prompt, generate the corresponding summaries and evaluations and add them to the prompt list
    for i in range(3):
        new_prompt = refine_agent.refine_prompt(top_prompt)
        prompts += [create_summary_prompt_overview(new_prompt)]
    
    iteration += 1
