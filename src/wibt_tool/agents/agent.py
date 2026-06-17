import json
from string import Template
from wibt_tool.utils.json_helper import extract_json


class Agent:
    def __init__(self, llm_endpoint, model, system_prompt, temperature=0, history=0):
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


    def get_system_prompt(self):
        return self.system_prompt

    def clear_messages(self):
        self.messages = [
          {
            "role": "system",
            "content": self.system_prompt
          }
        ]


    async def send_messages(self, user_prompts):
        
        for user_prompt in user_prompts:
            self.messages += [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]

        response = await self.llm_endpoint.send_messages(self.model, self.messages, self.temperature)

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


    async def send_message(self, user_prompt=""):
        return await self.send_messages([user_prompt])

    async def send_messages_structured(self, messages, output_model, number=0):
        _messages = messages
        while True:
            result = extract_json(await self.send_messages(_messages))
            if result != None:
                try:
                    if number == 0:
                        output_model.model_validate(result)
                    else:
                        [output_model.model_validate(result[f"{i}"]) for i in range(1,number+1)] # check if all the facts are in the list
                    print("✓ Structure is valid")
                    return result
                except Exception as e:
                    print(f"✗ Structure validation failed: {e}")
            _output_fix_request = "I could not process your response. Are you sure that you have provided a response exactly like the system prompt states? If you have any special characters, make sure you've escaped them correctly."
            if number != 0:
                _output_fix_request += f" There are {number} entries expected."
            _messages = [_output_fix_request]


    def set_messages(self, messages):
        self.messages = messages

    def get_messages(self):
        return self.messages

