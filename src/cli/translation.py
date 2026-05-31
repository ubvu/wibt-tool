import argparse
import sys

sys.path.insert(0, "src")

from utils.openai_client import OpenAIClient

from config import AppConfig
from prompt_manager import PromptManager
from agent_factory import AgentFactory

from translation_orchestrator import TranslationOrchestrator


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='translation.py',
        description='Creates a translation of a document'
    )

    parser.add_argument('-tc', '--translation-context', help='type of prompts to use for translation related agents', required=True)
    parser.add_argument('-i', '--input-file', help='path of the source document to translate', required=True)
    parser.add_argument('-o', '--output-file', help='path where the translation is stored', required=True)

    args = parser.parse_args()

    # Load configuration
    try:
        config = AppConfig.from_env()
    except Exception as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    print("Configuration loaded successfully")

    # Initialize dependencies
    llm_endpoint = OpenAIClient(token=config.api_token, endpoint=config.api_url)
    prompt_manager = PromptManager(config=config)
    agent_factory = AgentFactory(config=config, prompt_manager=prompt_manager, llm_endpoint=llm_endpoint)

    # Read input
    input_path = args.input_file
    try:
        with open(input_path, "r") as file:
            source_content = file.read()
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    output_path = args.output_file
    translation_context = args.translation_context

    # Run translation
    translation_orchestrator = TranslationOrchestrator(agent_factory, config)
    try:
        translation = translation_orchestrator.run(
            summary=source_content,
            translation_ctx=translation_context
        )
    except Exception as e:
        print(f"Translation failed: {e}")
        sys.exit(1)

    # Write output
    try:
        with open(output_path, "w") as file:
            file.write(translation)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
