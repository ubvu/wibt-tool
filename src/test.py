import os
import sys
import json
from dotenv import load_dotenv
from string import Template
from operator import itemgetter
from utils.open_webui import OpenWebuiClient
from utils.openai_client import OpenAIClient
from agents import Agent, SummaryAgent, ReadEvalAgent, RefinementAgent, TranslationDraftAgent, TranslationProofreadAgent, FactExtractorAgent, FactValidatorAgent, FactContainmentAgent, ArgumentAgent, AdjudicatorAgent
from utils import get_numbered_sentences


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

summary_model = os.environ.get('DEFAULT_MODEL')
refinement_model = os.environ.get('DEFAULT_MODEL')
draft_model = os.environ.get('DEFAULT_MODEL')
proofread_model = os.environ.get('DEFAULT_MODEL')
fact_extractor_model = os.environ.get('DEFAULT_MODEL')
fact_validator_model = os.environ.get('DEFAULT_MODEL')
fact_containment_model = os.environ.get('DEFAULT_MODEL')
advocate_model = os.environ.get('DEFAULT_MODEL')
skeptic_model = os.environ.get('DEFAULT_MODEL')
adjudicator_model = os.environ.get('DEFAULT_MODEL')


# load a test paper, stored in markdown
paper_file_path = sys.argv[1]
with open(paper_file_path, "r") as file:
    paper = file.read()

# load a test summary, stored in markdown
summary_file_path = sys.argv[2]
with open(summary_file_path, "r") as file:
    summary = file.read()

split_summary = get_numbered_sentences(summary)
numbered_summary = '\n'.join(split_summary)

print(numbered_summary)

with open("prompts/summary/general/summary_system.txt", "r") as file:
    summary_system_prompt = file.read()
with open("prompts/summary/general/summarize.txt", "r") as file:
    summarize_prompt = file.read()

with open("prompts/summary/general/read_eval_system.txt") as file:
    read_eval_system_prompt = file.read()
with open("prompts/summary/general/read_eval.txt") as file:
    read_eval_prompt = file.read()

with open("prompts/summary/general/refine_system.txt") as file:
    refine_system_prompt = file.read()
with open("prompts/summary/general/refine.txt") as file:
    refine_prompt = file.read()

with open("prompts/translation/general/draft_system.txt") as file:
    draft_system_prompt = file.read()
with open("prompts/translation/general/draft.txt") as file:
    draft_prompt = file.read()
with open("prompts/translation/general/pre_draft.txt") as file:
    pre_draft_prompt = file.read()
with open("prompts/translation/general/refine_draft.txt") as file:
    refined_draft_prompt = file.read()

with open("prompts/translation/general/proofread_system.txt") as file:
    proofread_system_prompt = file.read()
with open("prompts/translation/general/proofread.txt") as file:
    proofread_prompt = file.read()
    
with open("prompts/factuality_evaluation/general/key_fact_generation.txt") as file:
    fact_extractor_system_prompt = file.read()
with open("prompts/factuality_evaluation/general/key_fact_validation.txt") as file:
    fact_validator_system_prompt = file.read()
with open("prompts/factuality_evaluation/general/key_fact_alignment.txt") as file:
    fact_containment_system_prompt = file.read()
with open("prompts/factuality_evaluation/general/advocate.txt") as file:
    advocate_system_prompt = file.read()
with open("prompts/factuality_evaluation/general/skeptic.txt") as file:
    skeptic_system_prompt = file.read()
with open("prompts/factuality_evaluation/general/adjudicator.txt") as file:
    adjudicator_system_prompt = file.read()
# with open("") as file:
#     = file.read()


# summary_agent = SummaryAgent(
#     llm_endpoint=llm_endpoint,
#     model=summary_model,
#     system_prompt=summary_system_prompt,
#     summarize_prompt=summarize_prompt,
#     temperature=0,
#     history=-1
# )

# summary = summary_agent.send_message(paper)


# print("Summary:")
# print(summary)


# read_eval_agent = ReadEvalAgent(
#     llm_endpoint=llm_endpoint,
#     model=summary_model,
#     system_prompt=read_eval_system_prompt,
#     read_eval_prompt=read_eval_prompt,
#     temperature=0,
#     history=-1
# )

# read_eval = read_eval_agent.evaluate_summary(summary)

# print(f"Read eval:\n{read_eval}")

# refinement_agent = RefinementAgent(
#     llm_endpoint=llm_endpoint,
#     model=refinement_model,
#     system_prompt=refine_system_prompt,
#     refine_prompt=refine_prompt
# )

# prompt = refinement_agent.refine("Summarize this paper.", {
#     "Syntactic clarities": 3,
#     "Jargon": 3,
#     "Information density": 1,
#     "Structural cohesion": 2
# }, {
#     'faithfulness' : 2,
#     'completeness' : 3
# })

# print(f"Prompt:\n{prompt}")

# draft_agent = TranslationDraftAgent(
#     llm_endpoint=llm_endpoint,
#     model=draft_model,
#     system_prompt=draft_system_prompt,
#     pre_draft_prompt=pre_draft_prompt,
#     draft_prompt=draft_prompt,
#     refine_draft_prompt=refined_draft_prompt
# )

# proofread_agent = TranslationProofreadAgent(
#     llm_endpoint=llm_endpoint,
#     model=proofread_model,
#     system_prompt=proofread_system_prompt,
#     proofread_prompt=proofread_prompt
# )

# draft, refined_draft = draft_agent.write_refined_draft(summary)
# translation = proofread_agent.proofread_draft(summary, draft, refined_draft)

# print(f"Translation:\n{translation}")

# fact_extractor_agent = FactExtractorAgent(
#     llm_endpoint=llm_endpoint,
#     model=fact_extractor_model,
#     system_prompt=fact_extractor_system_prompt
# )

# facts = fact_extractor_agent.extract_facts(paper)
# print(facts)

# fact_validator_agent = FactValidatorAgent(
#     llm_endpoint=llm_endpoint,
#     model=fact_validator_model,
#     system_prompt=fact_validator_system_prompt
# )

# facts_validations = fact_validator_agent.validate_facts(paper, facts)
# print(validated_facts)

# fact_containment_agent = FactContainmentAgent(
#     llm_endpoint=llm_endpoint,
#     model=fact_containment_model,
#     system_prompt=fact_containment_system_prompt
# )

# fact_containment_agent.check_containment(facts, summary) # this is all the facts

advocate_agent = ArgumentAgent(
    llm_endpoint=llm_endpoint,
    model=advocate_model,
    system_prompt=advocate_system_prompt
    )

skeptic_agent = ArgumentAgent(
    llm_endpoint=llm_endpoint,
    model=skeptic_model,
    system_prompt=skeptic_system_prompt
)

adjudicator_agent = AdjudicatorAgent(
    llm_endpoint=llm_endpoint,
    model=adjudicator_model,
    system_prompt=adjudicator_system_prompt
)

advocate_arguments = advocate_agent.argue(paper, summary)
skeptic_arguments = skeptic_agent.argue(paper, summary)

adjudicator_judgements = adjudicator_agent.judge(paper, summary, advocate_arguments, skeptic_arguments)


print(numbered_summary)

# print(adjudicator_judgements)