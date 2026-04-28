from . import Agent
from string import Template


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