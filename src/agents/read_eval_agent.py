from . import Agent
from models import ReadEval
from string import Template


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

        return result