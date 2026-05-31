from .base import Agent
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

    def draft(self, summary, example_translation):
        return self.send_message(Template(self.draft_prompt).substitute(text=summary, example_translation=example_translation))


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

    def refine(self):
        return self.send_message(self.refine_draft_prompt)


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


class TranslationDirectAgent(Agent):
    def __init__(self, llm_endpoint, model, translate_direct_prompt, temperature=0, history=-1):
        super().__init__(
            llm_endpoint=llm_endpoint, 
            model=model, 
            system_prompt="",
            temperature=temperature, 
            history=history
        )
        self.translate_direct_prompt = translate_direct_prompt


    def translate(self, summary):
        self.clear_messages()
        translation = self.send_message(Template(self.translate_direct_prompt).substitute(text=summary))


        return translation
