import asyncio
import argparse
import json
import math
import sys
import traceback
from pathlib import Path

from wibt_tool.utils.openai_client import OpenAIClient
from wibt_tool.config import AppConfig
from wibt_tool.prompt_manager import PromptManager
from wibt_tool.agent_factory import AgentFactory

def log(message):
    print(message, file=sys.stderr)

async def calculate_faithfulness(paper, summary, advocate, skeptic, adjudicator) -> int:
    adv_args, ske_args = await asyncio.gather(
        advocate.argue(paper, summary),
        skeptic.argue(paper, summary)
    )

    judgements = await adjudicator.judge(paper, summary, adv_args, ske_args)
    
    if not isinstance(judgements, dict):
        raise TypeError(f"Expected judgements to be a dict, got {type(judgements)}")

    total = len(judgements.values())
    contained = 0
    for i, (key, j) in enumerate(judgements.items(), 1):
        if isinstance(j, dict):
            if j.get('faithful'):
                contained += 1
        elif hasattr(j, 'faithful'): # If it's a Pydantic model
            if j.faithful:
                contained += 1
        else:
            raise AttributeError(f"Item {key} in judgements is a {type(j)}, expected dict or model. Content: {j}")
            
    return math.floor((contained / total) * 5) if total > 0 else 0

async def calculate_completeness(summary, alignment_agent, validated_facts) -> int:
    alignment_results = await alignment_agent.check_alignment(validated_facts, summary)
    total = len(alignment_results.values())
    contained = sum(1 for r in alignment_results.values() if r.get('contained'))
    return math.floor((contained / total) * 5) if total > 0 else 0

async def main():
    parser = argparse.ArgumentParser(description='Evaluates a single summary against a paper.')
    parser.add_argument('-sc', '--summary-context', required=True, help='summary context')
    parser.add_argument('-fc', '--factuality-context', required=True, help='factuality context')
    parser.add_argument('-i', '--input-paper', required=True, help='path to paper.md')
    parser.add_argument('-s', '--input-summary', required=True, help='path to summary.md')
    parser.add_argument('-j', '--json', action='store_true', help='output results as JSON to stdout')
    parser.add_argument('-oj', '--output-json', help='path to save evaluation scores as a JSON file')

    args = parser.parse_args()

    try:
        config = AppConfig.from_env()
    except Exception as e:
        print(f"Configuration error: {e}")
        return

    llm_endpoint = OpenAIClient(token=config.api_token, endpoint=config.api_url)
    prompt_manager = PromptManager(config=config)
    agent_factory = AgentFactory(config=config, prompt_manager=prompt_manager, llm_endpoint=llm_endpoint)

    try:
        with open(args.input_paper, "r", encoding="utf-8") as f:
            paper = f.read()
        with open(args.input_summary, "r", encoding="utf-8") as f:
            summary = f.read()
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Initialize agents
    read_eval_agent = agent_factory.create_read_eval_agent(args.summary_context)
    extractor_agent = agent_factory.create_fact_extractor_agent(args.factuality_context)
    validator_agents = agent_factory.create_fact_validator_agents(args.factuality_context)
    advocate_agent = agent_factory.create_advocate_agent(args.factuality_context)
    skeptic_agent = agent_factory.create_skeptic_agent(args.factuality_context)
    adjudicator_agent = agent_factory.create_adjudicator_agent(args.factuality_context)
    alignment_agent = agent_factory.create_fact_alignment_agent(args.factuality_context)

    # 1. Extract and validate facts
    log("Extracting and validating facts from paper...")
    try:
        draft_facts = await extractor_agent.extract_facts(paper)
        validation_results = await asyncio.gather(*(v.validate_facts(paper, draft_facts) for v in validator_agents))
        
        validated_facts = []
        for i, fact in enumerate(draft_facts):
            fact_num = str(i + 1)
            veto_count = sum(1 for result in validation_results if not result.get(fact_num, {}).get("response"))
            if veto_count == 0:
                validated_facts.append(fact)
        log(f"Found {len(validated_facts)} validated facts.")
    except Exception as e:
        log(f"Error during fact extraction/validation: {e}")
        traceback.print_exc()
        return

    # 2. Evaluate
    log("Running evaluation...")
    try:
        readability_scores = await read_eval_agent.evaluate_summary(summary)
        faithfulness = await calculate_faithfulness(paper, summary, advocate_agent, skeptic_agent, adjudicator_agent)
        completeness = await calculate_completeness(summary, alignment_agent, validated_facts)

        readability_total = sum(int(score) for score in readability_scores.values())
        factuality_scores = {"faithfulness": faithfulness, "completeness": completeness}
        factuality_total = sum(int(score) for score in factuality_scores.values())
        total_score = readability_total + factuality_total

        results = {
            "total_score": total_score,
            "readability_scores": readability_scores,
            "faithfulness": faithfulness,
            "completeness": completeness
        }

        if args.output_json:
            try:
                with open(args.output_json, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4)
                log(f"Results saved to {args.output_json}")
            except Exception as e:
                log(f"Error saving JSON file: {e}")

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("\n" + "="*30)
            print("EVALUATION RESULTS")
            print("="*30)
            print(f"Total Score: {total_score}")
            print("-" * 30)
            print("Readability Scores:")
            for k, v in readability_scores.items():
                print(f"  {k}: {v}")
            print("-" * 30)
            print(f"Faithfulness:  {faithfulness} / 5")
            print(f"Completeness:  {completeness} / 5")
            print("="*30 + "\n")

    except Exception as e:
        log(f"Error during evaluation: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
