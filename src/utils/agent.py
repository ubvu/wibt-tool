import json
from string import Template
from utils.json_helper import extract_json


class Agent:
    def __init__(self, model, system_prompt, llm_endpoint, temperature, history=0):
        self.model = model
        self.llm_endpoint = llm_endpoint 
        self.messages = []
        self.set_system_prompt(system_prompt)
        self.temperature = temperature
        self.history = history


    def set_model(self, model):
        self.model = model


    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt
        self.clear_messages()


    def clear_messages(self):
        self.messages = [
          {
            "role": "system",
            "content": self.system_prompt
          }
        ]


    def _send_messages(self, messages):
        return self.llm_endpoint.send_messages(self.model, messages, self.temperature)

    def send_message(self, user_prompt=""):

        self.messages += [
          {
            "role": "user",
            "content": user_prompt
          }
        ]

        response = self.llm_endpoint.send_messages(self.model, self.messages, self.temperature)

        self.messages += [
          {
            "role": "assistant",
            "content": response
          }
        ]

        if self.history != -1: # -1 is infinite memory
            if len(self.messages) > self.history + 1: # + 1 because system prompt does not count
                if self.history == 0: # 0 is keep no history, other than the system prompt
                    self.messages = [self.messages[0]]
                else:
                    self.messages = [self.messages[0]] + self.messages[-self.history:]
                
        print(response)
        return response


    def get_messages(self):
        return self.messages

class SummaryAgent(Agent):
    def generate_summary(self, paper):
        return self._send_message(paper)


class ReadEvalAgent(Agent):
    def evaluate_summary(self, summary):
        return extract_json(self._send_message(summary))

class FactEvalAgent(Agent):
    def evaluate_summary(self, summary, paper):
        return extract_json(self._send_message(f"Paper:\n{paper}\n\nSummary:\n{summary}"))



class RefineAgent(Agent):
    def refine_prompts(self, prompt_results):
        pass
    
    def refine_prompt(self, prompt_overview):
        prompt = prompt_overview['prompt']
        readability = prompt_overview['readability_score']
        factuality = prompt_overview['factuality_score']

        user_prompt = """
Original prompt:
```
$prompt
```

Readability:
$readability_score

Factuality
$factuality_score
        """
        user_prompt = Template(user_prompt).substitute(prompt_overview)
        return extract_json(self._send_message(user_prompt))['prompt']

    

class TranslationAgent(Agent):
    def __init__(self, model, llm_endpoint, temperature, pre_draft_prompt, draft_prompt, refine_draft_prompt, proofread_prompt):
        super().__init__(model, "", llm_endpoint, temperature, history=-1)
        self.pre_draft_prompt = pre_draft_prompt
        self.draft_prompt = draft_prompt
        self.refine_draft_prompt = refine_draft_prompt
        self.proofread_prompt = proofread_prompt


    def _create_pre_draft(self):
        self.pre_draft = self._send_message(Template(self.pre_draft_prompt).substitute(paper=self.paper))


    def _create_draft(self):
        self.draft = self._send_message(Template(self.draft_prompt).substitute(paper=self.paper))


    def _create_refined_draft(self):
        self.refined_draft = self._send_message(self.refine_draft_prompt)


    def _create_proofread_translation(self):
        self.proofread_translation = self._send_message(Template(self.proofread_prompt).substitute(paper=self.paper, draft=self.draft, refined_draft=self.refined_draft))


    def translate(self, paper):
        self.clear_messages()
        self.paper = paper
        self._create_pre_draft()
        self._create_draft()
        self._create_refined_draft()

        self.clear_messages()
        self._create_proofread_translation()
        return self.proofread_translation
    

class DirectTranslationAgent(Agent):
    def __init__(self, model, llm_endpoint, temperature, translation_prompt):
        super().__init__(model, "", llm_endpoint, temperature)
        self.translation_prompt = translation_prompt


    def translate(self, paper):
        return self._send_message(Template(self.translation_prompt).substitute(paper=paper))

# lightllm proxy agents