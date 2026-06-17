from . import Agent
from string import Template


class TranslationDraftAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, draft_prompt, temperature=0, history=-1, **kwargs):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.draft_prompt = draft_prompt

    async def draft(self, summary, example_translation):
        return await self.send_message(Template(self.draft_prompt).substitute(text=summary, example_translation=example_translation))
