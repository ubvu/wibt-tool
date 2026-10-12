from . import Agent


class TranslationRefineDraftAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, refine_draft_prompt, temperature=0, history=-1, **kwargs):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.refine_draft_prompt = refine_draft_prompt

    async def refine(self):
        return await self.send_message(self.refine_draft_prompt)
