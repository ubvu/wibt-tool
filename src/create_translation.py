import os
import sys
import json
from dotenv import load_dotenv
from string import Template
from operator import itemgetter
from utils.open_webui import OpenWebuiClient
from utils.openai_client import OpenAIClient
from utils.agent import Agent, TranslationAgent, DirectTranslationAgent

load_dotenv() 

default_api = os.environ.get('DEFAULT_API')

if default_api == "open_webui":
    # load in token needed to connect to Nebula
    token = os.environ.get('OPEN_WEBUI_TOKEN')
    url = os.environ.get('OPEN_WEBUI_URL')
    llm_endpoint = OpenWebuiClient(token, url)
elif default_api == "openai":
    # use an OpenAI endpoint instead
    token = os.environ.get('OPEN_AI_TOKEN')
    url = os.environ.get('OPEN_AI_URL')
    llm_endpoint = OpenAIClient(token, url)

draft_model = os.environ.get('DEFAULT_DRAFT_MODEL')
proofread_model = os.environ.get('DEFAULT_PROOFREAD_MODEL')

# load a test paper, stored in markdown
paper_file_path = sys.argv[1]
with open(paper_file_path, "r") as file:
    paper = file.read()


with open("prompts/translation/draft_system.txt", "r") as file:
    draft_system_prompt = file.read()
with open("prompts/translation/pre_draft.txt", "r") as file:
    pre_draft_prompt = file.read()
with open("prompts/translation/draft.txt", "r") as file:
    draft_prompt = file.read()
with open("prompts/translation/refine_draft.txt", "r") as file:
    refine_prompt = file.read()
with open("prompts/translation/proofread_system.txt", "r") as file:
    proofread_system_prompt = file.read()
with open("prompts/translation/proofread.txt", "r") as file:
    proofread_prompt = file.read()


draft_agent = Agent(draft_model, draft_system_prompt, llm_endpoint, temperature=0, history=-1)
proofread_agent = Agent(proofread_model, proofread_system_prompt, llm_endpoint, temperature=0, history=-1)

pre_draft = draft_agent.send_message(Template(pre_draft_prompt).substitute(paper=paper))
draft = draft_agent.send_message(Template(draft_prompt).substitute(paper=paper))
refined_draft = draft_agent.send_message(Template(refine_prompt).substitute(paper=paper))
translation = proofread_agent.send_message(Template(proofread_prompt).substitute(paper=paper, draft=draft, refined_draft=refined_draft))


print("Final translation:")
print(translation)