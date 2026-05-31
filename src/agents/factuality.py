from .base import Agent
from models import KeyFactList, KeyFactValidation, KeyFactContainment


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
        formatted_facts = self._format_facts_for_validation(facts)
        fact_validations = self.send_messages_structured([f"Paper:\n\n{paper}", f"Fact list:\n\n{formatted_facts}\n\nPlease make sure to include an evaluation for all {len(facts)} facts."], KeyFactValidation, number=len(facts))

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


class FactAlignmentAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )


    def check_alignment(self, facts, summary):
        self.clear_messages()
        formatted_facts = self._format_facts_for_alignment(facts)
        fact_containment = self.send_messages_structured([f"Statements:\n\n{formatted_facts}", f"Summary:\n\n{summary}\n\nPlease make sure to include an evaluation for all the {len(facts)} statements."], KeyFactContainment, number=len(facts))

        return fact_containment


    def _format_facts_for_alignment(self, facts):
        """Format facts as numbered list for alignment prompt."""
        formatted = []
        for i, fact in enumerate(facts, 1):
            formatted.append(f"{i}:\n{fact}\n")
        return "\n".join(formatted)
