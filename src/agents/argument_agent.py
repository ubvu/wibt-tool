from . import Agent
from models import Argument
from utils import get_numbered_sentences



class ArgumentAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )


    def argue(self, paper, summary):
        self.clear_messages()
        split_paper = get_numbered_sentences(paper)
        numbered_paper = '\n'.join(split_paper)
        split_summary = get_numbered_sentences(summary)
        numbered_summary = '\n'.join(split_summary)
        print(numbered_summary)
        number_of_summary_lines = len(split_summary)
        arguments = self.send_messages_structured([f"Paper:\n\n{numbered_paper}", f"Summary:\n\n{numbered_summary}\n\nPlease make sure to include an argument for all {number_of_summary_lines}lines."], Argument, number=number_of_summary_lines)

        return arguments