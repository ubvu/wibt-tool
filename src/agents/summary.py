from .base import Agent
from models import ReadEval, Prompt
from string import Template


class SummaryAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, summarize_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.summarize_prompt = summarize_prompt

    def generate_summary(self, paper, keyfacts=None):
        self.clear_messages()
        if keyfacts:
            prompt = Template(self.summarize_prompt).substitute(paper=paper)
            prompt += "\nHere is a list of the keyfacts in this paper. Make sure all of these are included in the summary.\n\n"
            prompt += str(keyfacts)
            return self.send_message(prompt)
        else:
            return self.send_message(Template(self.summarize_prompt).substitute(paper=paper))


class ReadEvalAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, read_eval_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.read_eval_prompt = read_eval_prompt


    def evaluate_summary(self, summary):
        self.clear_messages()
        result = self.send_messages_structured([Template(self.read_eval_prompt).substitute(summary=summary)], ReadEval)

        return {
            "syntactic_clarity" : int(result['syntactic_clarity']),
            "jargon" : int(result['jargon']),
            "information_density" : int(result['information_density']),
            "structural_cohesion" : int(result['structural_cohesion'])
        }


class RefinementAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, refine_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.refine_prompt = refine_prompt


    def refine(self, prompt, readability_scores, factuality_scores):
        self.clear_messages()

        prompt_information = {
            'prompt' : prompt,
            'clarity' : readability_scores['syntactic_clarity'],
            'jargon' : readability_scores['jargon'],
            'density' : readability_scores['information_density'],
            'cohesion' : readability_scores['structural_cohesion'],
            'faithfulness' : factuality_scores['faithfulness'],
            'completeness' : factuality_scores['completeness']
        }

        result = self.send_messages_structured([Template(self.refine_prompt).substitute(prompt_information)], Prompt)
        return result['prompt']
