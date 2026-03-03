from . import Agent
from string import Template


class TranslationDraftAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, pre_draft_prompt, draft_prompt, refine_draft_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.pre_draft_prompt = pre_draft_prompt
        self.draft_prompt = draft_prompt
        self.refine_draft_prompt = refine_draft_prompt


    def write_refined_draft(self, summary):
        self.clear_messages()
        pre_draft = self.send_message(Template(self.pre_draft_prompt).substitute(text=summary))
        draft = self.send_message(Template(self.draft_prompt).substitute(text=summary))
        refined_draft = self.send_message(self.refine_draft_prompt)

        return draft, refined_draft