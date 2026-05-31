import argparse
import csv
import json
import sys

sys.path.insert(0, "src")

from utils.openai_client import OpenAIClient

from config import AppConfig
from prompt_manager import PromptManager
from agent_factory import AgentFactory

from summary_orchestrator import SummaryOrchestrator
from translation_orchestrator import TranslationOrchestrator


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        prog='summary.py',
        description='Creates a summary of a scientific article'
    )

    parser.add_argument('-sc', '--summary-context', help='type of prompts to use for summary related agents', required=True)
    parser.add_argument('-fc', '--factuality-context', help='type of prompts to use for factuality related agents', required=True)
    parser.add_argument('-tc', '--translation-context', help='type of prompts to use for translation related agents', required=True)
    parser.add_argument('-it', '--iterations', help='number of iterations to perform', type=int, required=True)
    parser.add_argument('-i', '--input-file', help='path of the paper to summarize', required=True)
    parser.add_argument('-ot', '--output-translated-summary', help='path of where the translated summary is stored')
    parser.add_argument('-st', '--search-type', help='whether to use prompt refinement (refine) or to use a static prompt (static)', required=True)
    parser.add_argument('-pf', '--provide-facts', help='whether to provide the keyfacts to generate the summary', action='store_true')
    parser.add_argument('-oes', '--output-english-summary', help='path of where the untranslated summary is stored')
    parser.add_argument('-okf', '--output-key-facts', help='path of where the overview of key-facts are stored')
    parser.add_argument('-oh', '--output-history', help='path of where the history is stored')
    parser.add_argument('-osh', '--output-score-history', help='path of where the score history is stored')

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
    paper_file_path = args.input_file
    try:
        with open(paper_file_path, "r") as file:
            paper = file.read()
    except FileNotFoundError:
        print(f"Input file not found: {paper_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    # Extract arguments
    number_of_iterations = args.iterations
    output_translated_summary = args.output_translated_summary
    output_english_summary_path = args.output_english_summary
    output_key_facts_path = args.output_key_facts
    output_history_path = args.output_history
    output_score_history_path = args.output_score_history
    summary_context = args.summary_context
    factuality_context = args.factuality_context
    translation_context = args.translation_context
    search_method = args.search_type
    provide_facts = args.provide_facts

    # Run summary
    summary_orchestrator = SummaryOrchestrator(agent_factory, prompt_manager, config, search_method, provide_facts)
    try:
        summary_result = summary_orchestrator.run(
            paper=paper,
            summary_ctx=summary_context,
            fact_ctx=factuality_context,
            iterations=number_of_iterations
        )
    except Exception as e:
        print(f"Summary generation failed: {e}")
        sys.exit(1)

    summary = summary_result['summary']
    print(f"Summary:\n{summary}")

    # Write translated summary
    if output_translated_summary:
        translation_orchestrator = TranslationOrchestrator(agent_factory, config)
        try:
            translation = translation_orchestrator.run(
                summary=summary,
                translation_ctx=translation_context
            )
        except Exception as e:
            print(f"Translation failed: {e}")
            sys.exit(1)

        print(f"Translation:\n{translation}")
        try:
            with open(output_translated_summary, "w") as file:
                file.write(translation)
        except Exception as e:
            print(f"Error writing translated summary: {e}")
            sys.exit(1)

    # Write English summary
    if output_english_summary_path:
        try:
            with open(output_english_summary_path, "w") as file:
                file.write(summary)
        except Exception as e:
            print(f"Error writing English summary: {e}")
            sys.exit(1)

    # Write history
    if output_history_path:
        try:
            with open(output_history_path, "w") as file:
                json.dump(summary_orchestrator._history, file)
        except Exception as e:
            print(f"Error writing history: {e}")
            sys.exit(1)

    # Build score history
    fieldnames = ["syntactic_clarity", "jargon", "information_density", "structural_cohesion", "faithfulness", "completeness", "total_score", "prompt", "summary"]
    scores = []
    for entry in summary_orchestrator._history:
        score = {
            "syntactic_clarity": entry["readability_scores"]["syntactic_clarity"],
            "jargon": entry["readability_scores"]["jargon"],
            "information_density": entry["readability_scores"]["information_density"],
            "structural_cohesion": entry["readability_scores"]["structural_cohesion"],
            "faithfulness": entry["factuality_scores"]["faithfulness"],
            "completeness": entry["factuality_scores"]["completeness"],
            "total_score": entry["total_score"],
            "prompt": entry["prompt"],
            "summary": entry["summary"]
        }
        scores.append(score)

    # Write score history
    if output_score_history_path:
        try:
            with open(output_score_history_path, "w") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(scores)
        except Exception as e:
            print(f"Error writing score history: {e}")
            sys.exit(1)

    # Write key facts
    if output_key_facts_path:
        try:
            with open(output_key_facts_path, "w") as file:
                json.dump(summary_orchestrator._validated_facts, file)
        except Exception as e:
            print(f"Error writing key facts: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
