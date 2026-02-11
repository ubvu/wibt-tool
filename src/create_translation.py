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

default_model = os.environ.get('DEFAULT_MODEL')

with open("prompts/translation/pre_draft.txt", "r") as file:
    pre_draft_prompt = file.read()

with open("prompts/translation/draft.txt", "r") as file:
    draft_prompt = file.read()

with open("prompts/translation/refine_draft.txt", "r") as file:
    refine_draft_prompt = file.read()

with open("prompts/translation/proofread.txt", "r") as file:
    proofread_prompt = file.read()


with open("prompts/translation/direct_translation.txt", "r") as file:
    direct_translation_prompt = file.read()


translation_agent = TranslationAgent(default_model, llm_endpoint, 0, pre_draft_prompt, draft_prompt, refine_draft_prompt, proofread_prompt)
translation = translation_agent.translate(paper)


direct_translation_agent = DirectTranslationAgent(default_model, llm_endpoint, 0, direct_translation_prompt)
direct_translation = direct_translation_agent.translate(paper)


print("Direct translation:")
print(direct_translation)

print("Final translation:")
print(translation)