import asyncio
import sys
import os

# Simulate the environment
sys.path.append(os.path.abspath("src"))

try:
    from wibt_tool.prompt_manager import PromptManager
    from wibt_tool.config import AppConfig
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class MockConfig:
    def __init__(self):
        self.default_context = "general"

async def main():
    config = MockConfig()
    pm = PromptManager(config)

    try:
        # Prompts are not async, but the rest of the workflow will be.
        prompts = pm.get_summary_agent_prompts("general")
        print("Successfully loaded summary prompts:", prompts)
    except Exception as e:
        print(f"Failed to load prompts: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
