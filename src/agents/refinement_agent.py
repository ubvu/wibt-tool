from . import Agent
from string import Template
from models import Prompt

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
            'clarity' : readability_scores['Syntactic clarity'],
            'jargon' : readability_scores['Jargon'],
            'density' : readability_scores['Information density'],
            'cohesion' : readability_scores['Structural cohesion'],
            'faithfulness' : factuality_scores['faithfulness'],
            'completeness' : factuality_scores['completeness']
        }

        result = self.send_messages_structured([Template(self.refine_prompt).substitute(prompt_information)], Prompt)
        return result
