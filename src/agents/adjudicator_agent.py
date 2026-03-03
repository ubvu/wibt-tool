from . import Agent
from models import Judgement



class AdjudicatorAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )


    def judge(self, paper, summary, advocate_arguments, skeptic_arguments):
        self.clear_messages()
        numbered_paper = paper
        numbered_summary = summary # TODO: fix me
        number_of_summary_lines = 1 # TODO: fix me
        formatted_arguments = "" # TODO: fix me
        judgements = self.send_messages_structured([f"Paper:\n\n{numbered_paper}", f"Summary:\n\n{numbered_summary}", f"Arguments:\n\n{formatted_arguments}"], Judgement, number=number_of_summary_lines)

        return judgements