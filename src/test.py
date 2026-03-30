import os
import sys
import json
from dotenv import load_dotenv
from string import Template
from operator import itemgetter
from utils.open_webui import OpenWebuiClient
from utils.openai_client import OpenAIClient
from utils.willma_client import WillmaClient
from agents import Agent, SummaryAgent, ReadEvalAgent, RefinementAgent, TranslationDraftAgent, TranslationProofreadAgent, FactExtractorAgent, FactValidatorAgent, FactAlignmentAgent, ArgumentAgent, AdjudicatorAgent
from utils import get_numbered_sentences


load_dotenv() 

default_api = os.environ.get('DEFAULT_API')

# if default_api == "OpenWebUI":
#     # load in token needed to connect to Nebula
#     token = os.environ.get('OPEN_WEBUI_TOKEN')
#     url = os.environ.get('OPEN_WEBUI_URL')
#     llm_endpoint = OpenWebuiClient(token, url)
# elif default_api == "OpenAI":
#     # use an OpenAI endpoint instead
#     token = os.environ.get('OPEN_AI_TOKEN')
#     url = os.environ.get('OPEN_AI_URL')
#     llm_endpoint = OpenAIClient(token, url)
token = os.environ.get('WILLMA_TOKEN')
url = os.environ.get('WILLMA_URL')
llm_endpoint = WillmaClient(token, url)


agent = Agent(llm_endpoint, 'openai/gpt-oss-120b', "You are a helpful assistant.")

print(agent.send_messages(["Can you speak like a pirate?", "hey"]))

print(llm_endpoint.get_model_list())