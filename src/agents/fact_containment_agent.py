from . import Agent
from models import KeyFactContainment



class FactContainmentAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )


    def check_containment(self, facts, summary):
        self.clear_messages()
        print(f"Expect {len(facts)}")
        formatted_facts = self._format_facts_for_alignment(facts)
        fact_containment = self.send_messages_structured([f"Statements:\n\n{formatted_facts}", f"Summary:\n\n{summary}"], KeyFactContainment, number=len(facts))

        return fact_containment


    def _format_facts_for_alignment(self, facts):
        """Format facts as numbered list for alignment prompt."""
        formatted = []
        for i, fact in enumerate(facts, 1):
            formatted.append(f"{i}:\n{fact}\n")
        return "\n".join(formatted)