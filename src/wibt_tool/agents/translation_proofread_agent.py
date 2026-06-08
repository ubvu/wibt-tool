from . import Agent
from string import Template


class TranslationProofreadAgent(Agent):
    def __init__(self, llm_endpoint, model, system_prompt, proofread_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt=system_prompt, 
            temperature=temperature, 
            history=history
        )
        self.proofread_prompt = proofread_prompt


    def proofread_draft(self, summary, draft, refined_draft):
        self.clear_messages()

        documents = {
            'text' : summary,
            'draft' : draft,
            'refined_draft' : refined_draft
        }
        translation = self.send_message(Template(self.proofread_prompt).substitute(documents))


        return translation