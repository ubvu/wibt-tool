import os
import sys
from pathlib import Path

sys.path.insert(0, "src")

import json
from string import Template
from operator import itemgetter
from dotenv import load_dotenv
from utils.open_webui import OpenWebuiClient
from utils.openai_client import OpenAIClient
from agents import Agent, SummaryAgent, ReadEvalAgent, RefinementAgent, TranslationDraftAgent, TranslationProofreadAgent, FactExtractorAgent, FactValidatorAgent, FactAlignmentAgent, ArgumentAgent, AdjudicatorAgent
from utils.json_helper import extract_json
import math
import argparse


def filter_by_majority_vote(
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
            if result.get(fact_num, {}).get("response")
        )

        if accepted_count > threshold:
            filtered.append(fact)

    # return [fact['fact'] for fact in filtered]
    return filtered

def format_facts(facts_overview):
    # Initialize an empty dictionary to store the results
    result = {}

    # Iterate through the list of dictionaries
    for fact_overview in facts_overview:
        category = fact_overview["category"]
        fact = fact_overview["fact"]
        
        # If the category is not in the result dictionary, add it with an empty list
        if category not in result:
            result[category] = []
        
        # Append the fact to the list for the appropriate category
        result[category].append(fact)
    text = ""
    for key in result.keys():
        text += f"{key}:\n-"
        text += "\n-".join(result[key])
        text += "\n\n"
    return text

def calculate_completeness(summary, facts):
    fact_alignment = fact_alignment_agent.check_alignment(facts, summary)
    total = len(fact_alignment.values())
    contained = sum(1 if fact['contained'] else 0 for fact in fact_alignment.values())

    return math.floor(contained/total * 5)

def calculate_faithfulness(summary, paper):
    advocate_arguments = advocate_agent.argue(paper, summary)
    skeptic_arguments = skeptic_agent.argue(paper, summary)

    adjudicator_judgements = adjudicator_agent.judge(paper, summary, advocate_arguments, skeptic_arguments)

    total = len(adjudicator_judgements.values())
    contained = sum(1 if sentence['faithful'] else 0 for sentence in adjudicator_judgements.values())

    return math.floor(contained/total * 5)

def create_summary_prompt_overview(summary_prompt):
    summary_agent.set_system_prompt(summary_prompt)
    summary = summary_agent.generate_summary(paper)

    readability_scores = read_eval_agent.evaluate_summary(summary)
    readability_total_score = sum(int(score) for score in readability_scores.values())


    factuality_scores = {
        "faithfulness" : calculate_faithfulness(summary, paper),
        "completeness" : calculate_completeness(summary, facts)
    }

    factuality_total_score = sum(int(score) for score in factuality_scores.values())
    total_score = readability_total_score + factuality_total_score

    return {
        "prompt" : summary_prompt,
        "summary" : summary,
        "readability_scores" : readability_scores,
        "factuality_scores" : factuality_scores,
        "total_score" : total_score
    }

load_dotenv() 

default_api = os.environ.get('DEFAULT_API')

if default_api == "OpenWebUI":
    # load in token needed to connect to Nebula
    token = os.environ.get('OPEN_WEBUI_TOKEN')
    url = os.environ.get('OPEN_WEBUI_URL')
    llm_endpoint = OpenWebuiClient(token, url)
elif default_api == "OpenAI":
    # use an OpenAI endpoint instead
    token = os.environ.get('OPEN_AI_TOKEN')
    url = os.environ.get('OPEN_AI_URL')
    llm_endpoint = OpenAIClient(token, url)


summary_model = os.environ.get('DEFAULT_SUMMARY_MODEL')
refinement_model = os.environ.get('DEFAULT_REFINEMENT_MODEL')
read_eval_model = os.environ.get('DEFAULT_READ_EVAL_MODEL')
draft_model = os.environ.get('DEFAULT_DRAFT_MODEL')
proofread_model = os.environ.get('DEFAULT_PROOFREAD_MODEL')
fact_extractor_model = os.environ.get('DEFAULT_FACT_EXTRACTION_MODEL')
fact_validator_models = os.environ.get('DEFAULT_FACT_VALIDATION_MODEL').split(',')
fact_alignment_model = os.environ.get('DEFAULT_ALIGNMENT_MODEL')
advocate_model = os.environ.get('DEFAULT_ADVOCATE_MODEL')
skeptic_model = os.environ.get('DEFAULT_SKEPTIC_MODEL')
adjudicator_model = os.environ.get('DEFAULT_ADJUDICATOR_MODEL')

summary_model_temp = int(os.environ.get('DEFAULT_SUMMARY_MODEL_TEMP'))
refinement_model_temp = int(os.environ.get('DEFAULT_REFINEMENT_MODEL_TEMP'))
read_eval_model_temp = int(os.environ.get('DEFAULT_READ_EVAL_MODEL_TEMP'))
draft_model_temp = int(os.environ.get('DEFAULT_DRAFT_MODEL_TEMP'))
proofread_model_temp = int(os.environ.get('DEFAULT_PROOFREAD_MODEL_TEMP'))
fact_extractor_model_temp = int(os.environ.get('DEFAULT_FACT_EXTRACTION_MODEL_TEMP'))
fact_validator_models_temps = [int(temp) for temp in os.environ.get('DEFAULT_FACT_VALIDATION_MODEL_TEMP').split(',')]
fact_alignment_model_temp = int(os.environ.get('DEFAULT_ALIGNMENT_MODEL_TEMP'))
advocate_model_temp = int(os.environ.get('DEFAULT_ADVOCATE_MODEL_TEMP'))
skeptic_model_temp = int(os.environ.get('DEFAULT_SKEPTIC_MODEL_TEMP'))
adjudicator_model_temp = int(os.environ.get('DEFAULT_ADJUDICATOR_MODEL_TEMP'))


# Get paper file path from command line
parser = argparse.ArgumentParser(
                    prog='summary.py',
                    description='Creates a summary of a given scientific article'
                    )


parser.add_argument('-sc', '--summary-context', help='type of prompts to use for summary related agents', required=True)
parser.add_argument('-fc', '--factuality-context', help='type of prompts to use for factuality related agents', required=True)
parser.add_argument('-tc', '--translation-context', help='type of prompts to use for translation related agents', required=True)
parser.add_argument('-it', '--iterations', help='number of iterations to perform', type=int, required=True)
parser.add_argument('-i', '--input-file', help='path of the paper to summarize', required=True)
parser.add_argument('-o', '--output-file', help='path of where the summary is stored', required=True)
parser.add_argument('-oes', '--output-english-summary', help='path of where the untranslated summary is stored')
parser.add_argument('-okf', '--output-key-facts', help='path of where the overview of key-facts are stored')

args = parser.parse_args()


# load a test paper, stored in markdown
paper_file_path = args.input_file
with open(paper_file_path, "r") as file:
    paper = file.read()

number_of_iterations = args.iterations

output_path = args.output_file
output_english_summary_path = args.output_english_summary
output_key_facts_path = args.output_key_facts

summary_context = args.summary_context
factuality_context = args.factuality_context
translation_context = args.translation_context


# load prompt templates for the different agents
with open(f"prompts/summary/{summary_context}/summary_system.txt", "r") as file:
    summary_system_prompt = file.read()
with open(f"prompts/summary/{summary_context}/summarize.txt", "r") as file:
    summarize_prompt = file.read()

with open(f"prompts/summary/{summary_context}/read_eval_system.txt") as file:
    read_eval_system_prompt = file.read()
with open(f"prompts/summary/{summary_context}/read_eval.txt") as file:
    read_eval_prompt = file.read()

with open(f"prompts/summary/{summary_context}/refine_system.txt") as file:
    refine_system_prompt = file.read()
with open(f"prompts/summary/{summary_context}/refine.txt") as file:
    refine_prompt = file.read()

with open(f"prompts/translation/{translation_context}/draft_system.txt") as file:
    draft_system_prompt = file.read()
with open(f"prompts/translation/{translation_context}/draft.txt") as file:
    draft_prompt = file.read()
with open(f"prompts/translation/{translation_context}/pre_draft.txt") as file:
    pre_draft_prompt = file.read()
with open(f"prompts/translation/{translation_context}/refine_draft.txt") as file:
    refined_draft_prompt = file.read()

with open(f"prompts/translation/{translation_context}/proofread_system.txt") as file:
    proofread_system_prompt = file.read()
with open(f"prompts/translation/{translation_context}/proofread.txt") as file:
    proofread_prompt = file.read()
    
with open(f"prompts/factuality_evaluation/{factuality_context}/key_fact_generation.txt") as file:
    fact_extractor_system_prompt = file.read()
with open(f"prompts/factuality_evaluation/{factuality_context}/key_fact_validation.txt") as file:
    fact_validator_system_prompt = file.read()
with open(f"prompts/factuality_evaluation/{factuality_context}/key_fact_alignment.txt") as file:
    fact_alignment_system_prompt = file.read()
with open(f"prompts/factuality_evaluation/{factuality_context}/advocate.txt") as file:
    advocate_system_prompt = file.read()
with open(f"prompts/factuality_evaluation/{factuality_context}/skeptic.txt") as file:
    skeptic_system_prompt = file.read()
with open(f"prompts/factuality_evaluation/{factuality_context}/adjudicator.txt") as file:
    adjudicator_system_prompt = file.read()


# create agents, temperature 0 makes them more deterministic, 1 less
summary_agent = SummaryAgent(
    llm_endpoint=llm_endpoint,
    model=summary_model,
    system_prompt=summary_system_prompt,
    summarize_prompt=summarize_prompt,
    temperature=summary_model_temp,
    history=-1
)

read_eval_agent = ReadEvalAgent(
    llm_endpoint=llm_endpoint,
    model=read_eval_model,
    system_prompt=read_eval_system_prompt,
    read_eval_prompt=read_eval_prompt,
    temperature=read_eval_model_temp,
    history=-1
)

refinement_agent = RefinementAgent(
    llm_endpoint=llm_endpoint,
    model=refinement_model,
    system_prompt=refine_system_prompt,
    refine_prompt=refine_prompt,
    temperature=refinement_model_temp
)

draft_agent = TranslationDraftAgent(
    llm_endpoint=llm_endpoint,
    model=draft_model,
    system_prompt=draft_system_prompt,
    pre_draft_prompt=pre_draft_prompt,
    draft_prompt=draft_prompt,
    refine_draft_prompt=refined_draft_prompt,
    temperature=draft_model_temp
)

proofread_agent = TranslationProofreadAgent(
    llm_endpoint=llm_endpoint,
    model=proofread_model,
    system_prompt=proofread_system_prompt,
    proofread_prompt=proofread_prompt,
    temperature=proofread_model_temp
)

fact_extractor_agent = FactExtractorAgent(
    llm_endpoint=llm_endpoint,
    model=fact_extractor_model,
    system_prompt=fact_extractor_system_prompt,
    temperature=fact_extractor_model_temp
)

fact_validator_agents = [FactValidatorAgent(
    llm_endpoint=llm_endpoint,
    model=fact_validator_models[i],
    system_prompt=fact_validator_system_prompt,
    temperature=fact_validator_models_temps[i]
) for i in range(len(fact_validator_models))]

fact_alignment_agent = FactAlignmentAgent(
    llm_endpoint=llm_endpoint,
    model=fact_alignment_model,
    system_prompt=fact_alignment_system_prompt,
    temperature=fact_alignment_model_temp
)

advocate_agent = ArgumentAgent(
    llm_endpoint=llm_endpoint,
    model=advocate_model,
    system_prompt=advocate_system_prompt,
    temperature=advocate_model_temp
    )

skeptic_agent = ArgumentAgent(
    llm_endpoint=llm_endpoint,
    model=skeptic_model,
    system_prompt=skeptic_system_prompt,
    temperature=skeptic_model_temp
)

adjudicator_agent = AdjudicatorAgent(
    llm_endpoint=llm_endpoint,
    model=adjudicator_model,
    system_prompt=adjudicator_system_prompt,
    temperature=adjudicator_model_temp
)




draft_facts = fact_extractor_agent.extract_facts(paper)

draft_facts_validations = [fact_validator_agent.validate_facts(paper, draft_facts) for fact_validator_agent in fact_validator_agents]

filtered_facts = filter_by_majority_vote(draft_facts, draft_facts_validations)
formated_facts = format_facts(filtered_facts)

facts = [fact['fact'] for fact in filtered_facts]

print("Formated facts")
print(formated_facts)



prompts = [create_summary_prompt_overview(summarize_prompt)]

iteration = 0
while True:

    print(f"Starting iteration {iteration}")
    print(f"Number of prompts: {len(prompts)}")

    top_prompt = sorted(prompts, key=itemgetter('total_score'), reverse=True)[0]
    print(f"Top prompt:\n{top_prompt}")

    # break conditions
    if iteration >= number_of_iterations:
        break
    
    if top_prompt['total_score'] >= 30:
        break


    # generate new prompts from the best prompt, generate the corresponding summaries and evaluations and add them to the prompt list
    for i in range(1):
        new_prompt = refinement_agent.refine(top_prompt['prompt'], top_prompt['readability_scores'], top_prompt['factuality_scores'])
        prompts += [create_summary_prompt_overview(new_prompt['prompt'])]
    
    iteration += 1


summary = sorted(prompts, key=itemgetter('total_score'), reverse=True)[0]['summary']


draft, refined_draft = draft_agent.write_refined_draft(summary)
translation = proofread_agent.proofread_draft(summary, draft, refined_draft)

print(f"Summary:\n{summary}")
print(f"Translation:\n{translation}")

with open(output_path, "w") as file:
    file.write(translation)

if output_english_summary_path:
    with open(output_english_summary_path, "w") as file:
        file.write(summary) 

if output_key_facts_path:
    with open(output_key_facts_path, "w") as file:
        file.write(formated_facts)