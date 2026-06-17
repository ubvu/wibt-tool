from . import Agent
from string import Template


class TranslationPreDraftAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, pre_draft_prompt, temperature=0, history=-1, **kwargs):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.pre_draft_prompt = pre_draft_prompt

    def pre_draft(self, summary):
        self.clear_messages()
        return self.send_message(Template(self.pre_draft_prompt).substitute(text=summary))
