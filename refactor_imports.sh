#!/bin/bash

# Find all .py files in src and apps
find src apps -name "*.py" | while read file; do
    # Use sed to perform replacements
    # We use | as a delimiter because some patterns might contain /

    # 1. Handle "from ... import ..."
    sed -i 's/from agents\./from wibt_tool.agents./g' "$file"
    sed -i 's/from agents import/from wibt_tool.agents import/g' "$file"
    sed -i 's/from models\./from wibt_tool.models./g' "$file"
    sed -i 's/from models import/from wibt_tool.models import/g' "$file"
    sed -i 's/from utils\./from wibt_tool.utils./g' "$file"
    sed -i 's/from utils import/from wibt_tool.utils import/g' "$file"
    sed -i 's/from config import/from wibt_tool.config import/g' "$file"
    sed -i 's/from prompt_manager import/from wibt_tool.prompt_manager import/g' "$file"
    sed -i 's/from agent_factory import/from wibt_tool.agent_factory import/g' "$file"
    
    # 2. Handle special cases for orchestrators and factuality
    sed -i 's/from summary_orchestrator/from wibt_tool.pipelines.summary_pipeline/g' "$file"
    sed -i 's/from translation_orchestrator/from wibt_tool.pipelines.translation_pipeline/g' "$file"
    sed -i 's/from factuality\.extraction/from wibt_tool.logic.factuality.extraction/g' "$file"
    sed -i 's/from factuality\.alignment/from wibt_tool.logic.factuality.alignment/g' "$file"

    # 3. Handle "import X"
    sed -i 's/import agents/import wibt_tool.agents as agents/g' "$file"
    sed -i 's/import models/import wibt_tool.models as models/g' "$file"
    sed -i 's/import utils/import wibt_tool.utils as utils/g' "$file"
    sed -i 's/import config/import wibt_tool.config as config/g' "$file"
    sed -i 's/import prompt_manager/import wibt_tool.prompt_manager as prompt_manager/g' "$file"
    sed -i 's/import agent_factory/import wibt_tool.agent_factory as agent_factory/g' "$file"

    echo "Processed $file"
done
