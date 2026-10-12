from openai import AsyncOpenAI
import json

class OpenAIClient:
    def __init__(self, token, endpoint):
        self.client = AsyncOpenAI(
            base_url=endpoint,
            api_key=token,
            timeout=600.0
        )

    async def send_messages(self, model, messages, temperature):
        chat_completion = await self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature
        )
        return chat_completion.choices[0].message.content

    async def get_model_list(self):
        models = await self.client.models.list()
        ids = []
        for model in models:
            ids += [model.id]
        return ids