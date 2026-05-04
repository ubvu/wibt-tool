import math
from operator import itemgetter
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

class SummaryOrchestrator:
    def __init__(self, factory, prompt_manager, config, search_method, provide_facts):
        self.factory = factory
        self.pm = prompt_manager
        self.config = config
        self.search_method = search_method
        self.provide_facts = provide_facts
        
        self._history: List[Dict[str, Any]] = []
        self._iteration: int = 0
        self._paper: Optional[str] = None
        self._contexts: Dict[str, str] = {}
        self._is_initialized: bool = False
        self._validated_facts: List[Dict[str, Any]] = []

    def run(self, paper: str, summary_ctx: str, fact_ctx: str, iterations: int, score_threshold: int = 30) -> Dict[str, Any]:

        summary_agent = self.factory.create_summary_agent(summary_ctx)
        read_eval_agent = self.factory.create_read_eval_agent(summary_ctx)
        refinement_agent = self.factory.create_refinement_agent(summary_ctx)
        extractor_agent = self.factory.create_fact_extractor_agent(fact_ctx)
        validator_agents = self.factory.create_fact_validator_agents(fact_ctx)
        advocate_agent = self.factory.create_advocate_agent(fact_ctx)
        skeptic_agent = self.factory.create_skeptic_agent(fact_ctx)
        adjudicator_agent = self.factory.create_adjudicator_agent(fact_ctx)
        alignment_agent = self.factory.create_fact_alignment_agent(fact_ctx)

        if not self._is_initialized or self._paper != paper:
            print("Starting a new session")
            print(f"Provide facts:{self.provide_facts}")
            if self.provide_facts:
                self._extract_facts(paper, extractor_agent, validator_agents)
                summary = summary_agent.generate_summary(paper, self._validated_facts)
            else:
                with ThreadPoolExecutor() as executor:
                    summary_future = executor.submit(summary_agent.generate_summary, paper)
                    extracted_facts_done_future = executor.submit(self._extract_facts, paper, extractor_agent, validator_agents)
                    summary = summary_future.result()
                    extracted_facts_done_future.result()



            eval_data = self._initialize_session(
                paper, summary, summary_agent.get_system_prompt(), summary_ctx, fact_ctx, summary_agent, read_eval_agent, 
                advocate_agent, skeptic_agent, adjudicator_agent, alignment_agent
            )
            
            eval_data['messages'] = {
                'summary_agent': summary_agent.messages,
                'read_eval_agent': read_eval_agent.messages,
                'advocate': advocate_agent.messages,
                'skeptic': skeptic_agent.messages,
                'adjudicator': adjudicator_agent.messages,
                'alignment': alignment_agent.messages,
                'extractor': extractor_agent.messages,
                'validator-0': validator_agents[0].messages,
                'validator-1': validator_agents[1].messages,
                'validator-2': validator_agents[2].messages
            }
            self._history.append(eval_data)
        else:
            print(f"Continuing existing session. Current iteration: {self._iteration}")

        for _ in range(iterations):
            top_prompt = sorted(self._history, key=itemgetter('total_score'), reverse=True)[0]
            
            if top_prompt['total_score'] >= score_threshold:
                print(f"Threshold {score_threshold} reached. Exiting early")
                break

            print(f"Iteration {self._iteration + 1} (Best Score: {top_prompt['total_score']})")
            if self.search_method == "refine":
                new_prompt = refinement_agent.refine(
                    top_prompt['prompt'], 
                    top_prompt['readability_scores'], 
                    top_prompt['factuality_scores']
                )
                summary_agent.set_system_prompt(new_prompt)

            elif self.search_method == "static":
                new_prompt = summary_agent.get_system_prompt()

            else:
                raise ValueError("The search type must be either 'refine' or 'static'")

            if self.provide_facts:
                summary = summary_agent.generate_summary(paper, self._validated_facts)
            else:
                summary = summary_agent.generate_summary(paper)

            eval_data = self._evaluate_prompt(
                self._paper,
                summary,
                new_prompt,
                read_eval_agent,
                advocate_agent,
                skeptic_agent,
                adjudicator_agent,
                alignment_agent
            )

            eval_data['messages'] = {
                'summary_agent': summary_agent.messages,
                'read_eval_agent': read_eval_agent.messages,
                'advocate': advocate_agent.messages,
                'skeptic': skeptic_agent.messages,
                'adjudicator': adjudicator_agent.messages,
                'alignment': alignment_agent.messages,
                'refinement_agent': refinement_agent.messages
            }
            
            self._history.append(eval_data)
            self._iteration += 1

        return self.get_best_result()

    def get_best_result(self) -> Dict[str, Any]:
        if not self._history:
            raise ValueError("No optimization has been run yet.")
        best_result = sorted(self._history, key=itemgetter('total_score'), reverse=True)[0]
        return {
            "summary": best_result['summary'],
            "total_score": best_result['total_score'],
            "iteration_count": self._iteration,
            "history_length": len(self._history)
        }
    
    def _extract_facts(self, paper, extractor_agent, validator_agents):
        draft_facts = extractor_agent.extract_facts(paper)
        validation_results = []
        with ThreadPoolExecutor() as executor:
            validation_result_futures = [] 
            for validator_agent in validator_agents:
                validation_result_futures.append(executor.submit(validator_agent.validate_facts, paper, draft_facts))
            
            for validation_result_future in validation_result_futures:
                validation_results.append(validation_result_future.result())

            
        self._validated_facts = self._filter_by_majority_vote(draft_facts, validation_results)

    def _initialize_session(self, paper, summary, summary_prompt, summary_ctx, fact_ctx, summary_agent, read_eval_agent, advocate_agent, skeptic_agent, adjudicator_agent, alignment_agent):
        self._paper = paper
        self._contexts = {"summary": summary_ctx, "factuality": fact_ctx}
        self._iteration = 0
        self._history = []
        

        print("Phase 2: Seeding optimization with initial prompt...")
        eval_data = self._evaluate_prompt(
            paper, summary, summary_prompt, read_eval_agent, advocate_agent, skeptic_agent, adjudicator_agent, alignment_agent
        )

        self._is_initialized = True
        return eval_data

    def _evaluate_prompt(self, paper, summary, summary_prompt, read_eval_agent, advocate_agent, skeptic_agent, adjudicator_agent, alignment_agent) -> Dict[str, Any]:
        """Purely calculates the scores and returns data. Does not handle messages."""

        with ThreadPoolExecutor() as executor:
            readability_scores_future = executor.submit(read_eval_agent.evaluate_summary, summary)
            faithfulness_future = executor.submit(self._calculate_faithfulness, paper, summary, advocate_agent, skeptic_agent, adjudicator_agent)
            completeness_future = executor.submit(self._calculate_completeness, summary, alignment_agent)

            faithfulness = faithfulness_future.result()
            readability_scores = readability_scores_future.result()
            completeness = completeness_future.result()

        readability_total = sum(int(score) for score in readability_scores.values())
        factuality_scores = {"faithfulness": faithfulness, "completeness": completeness}
        factuality_total = sum(int(score) for score in factuality_scores.values())

        return {
            "prompt": summary_prompt,
            "summary": summary,
            "readability_scores": readability_scores,
            "factuality_scores": factuality_scores,
            "total_score": readability_total + factuality_total
        }

    def _calculate_faithfulness(self, paper, summary, advocate, skeptic, adjudicator) -> int:
        with ThreadPoolExecutor() as executor:
            adv_args_future = executor.submit(advocate.argue, paper, summary)
            ske_args_future = executor.submit(skeptic.argue, paper, summary)

            adv_args = adv_args_future.result()
            ske_args = ske_args_future.result()

        judgements = adjudicator.judge(paper, summary, adv_args, ske_args)
        total = len(judgements.values())
        contained = sum(1 for j in judgements.values() if j.get('faithful'))
        return math.floor((contained / total) * 5) if total > 0 else 0

    def _calculate_completeness(self, summary, aligner) -> int:
        alignment_results = aligner.check_alignment(self._validated_facts, summary)
        total = len(alignment_results.values())
        contained = sum(1 for r in alignment_results.values() if r.get('contained'))
        return math.floor((contained / total) * 5) if total > 0 else 0

    def _filter_by_majority_vote(self, facts: list[dict], validation_results: list[dict]) -> list[dict]:
        filtered = []
        num_validators = len(validation_results)
        threshold = num_validators / 2
        for i, fact in enumerate(facts):
            fact_num = str(i + 1)
            accepted_count = sum(1 for result in validation_results if result.get(fact_num, {}).get("response"))
            if accepted_count > threshold:
                filtered.append(fact)
        return filtered
