from . import Agent
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

    def generate_summary(self, paper):
        self.clear_messages()
        return self.send_message(Template(self.summarize_prompt).substitute(paper=paper))