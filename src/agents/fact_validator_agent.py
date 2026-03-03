from . import Agent
from models import KeyFactValidation



class FactValidatorAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )


    def validate_facts(self, paper, facts):
        self.clear_messages()
        print(f"Expect {len(facts)}")
        formatted_facts = self._format_facts_for_validation(facts)
        fact_validations = self.send_messages_structured([f"Paper:\n\n{paper}", f"Fact list:\n\n{formatted_facts}"], KeyFactValidation, number=len(facts))

        return fact_validations


    def _format_facts_for_validation(self, facts):
        """Format facts as numbered list with fact/reason/category."""
        formatted = []
        for i, fact in enumerate(facts, 1):
            formatted.append(
                f"{i}:\n"
                f"Fact: {fact['fact']}\n"
                f"Reason: {fact['reason']}\n"
                f"Category: {fact['category']}\n"
            )
        return "\n".join(formatted)