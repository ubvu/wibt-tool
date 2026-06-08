import os
import re

def refactor_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content
    
    # Mapping of old import patterns to new ones
    replacements = [
        (r'from agents import', 'from wibt_tool.agents import'),
        (r'from models import', 'from wibt_tool.models import'),
        (r'from utils import', 'from wibt_tool.utils import'),
        (r'from config import', 'from wibt_tool.config import'),
        (r'from prompt_manager import', 'from wibt_tool.prompt_manager import'),
        (r'from agent_factory import', 'from wibt_tool.agent_factory import'),
        (r'from summary_orchestrator', 'from wibt_tool.pipelines.summary_pipeline'),
        (r'from translation_orchestrator', 'from wibt_tool.pipelines.translation_pipeline'),
        (r'from factuality.extraction', 'from wibt_tool.logic.factuality.extraction'),
        (r'from factuality.alignment', 'from wibt_tool.logic.factuality.alignment'),
        # Also handle cases where it might be 'import agents' etc.
        (r'import agents', 'import wibt_tool.agents as agents'),
        (r'import models', 'import wibt_tool.models as models'),
        (r'import utils', 'import wibt_tool.utils as utils'),
        (r'import config', 'import wibt_tool.config as config'),
        (r'import prompt_manager', 'import wibt_tool.prompt_manager as prompt_manager'),
    ]

    for old, new in replacements:
        content = re.sub(old, new, content)

    # Special case for relative imports if they exist in the old structure
    # e.g. 'from . import Agent' in agents/adjudicator_agent.py
    # Since we are still keeping the same relative structure within wibt_tool, these might be fine.
    # But let's check if we need to change anything else.

    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Updated: {file_path}")
    else:
        print(f"No change: {file_path}")

# Files to process
files_to_process = []

# All files in src and apps
for root, dirs, files in os.walk('.'):
    if 'venv' in root or '.git' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            files_to_process.append(os.path.join(root, file))

for file in files_to_process:
    refactor_file(file)
