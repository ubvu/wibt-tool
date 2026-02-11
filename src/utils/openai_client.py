from openai import OpenAI
import json

class OpenAIClient:
    def __init__(self, token, endpoint):
        self.token = token
        self.client = OpenAI(
            base_url=endpoint,
            api_key=token,  
        )

    def send_messages(self, model, messages, temperature):
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature
        )
        return chat_completion.choices[0].message.content