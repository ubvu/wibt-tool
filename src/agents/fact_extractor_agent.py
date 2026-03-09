from . import Agent
from models import KeyFactList



class FactExtractorAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )


    def extract_facts(self, paper):
        self.clear_messages()
        facts = self.send_messages_structured([f"Paper:\n\n{paper}"], KeyFactList)

        return facts