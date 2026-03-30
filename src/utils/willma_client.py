import json
import requests
class WillmaClient:
    def __init__(self, token, endpoint):
        self.token = token
        self.endpoint = endpoint
        self.headers = {"X-API-KEY": self.token, "Content-Type": "application/json"}

    def send_messages(self, model, messages, temperature):
        response = requests.post(
        f"{self.endpoint}/chat/completions", data=json.dumps(
            {
            "model": model,
            "messages": messages,
            }
        ), headers=self.headers
        ).json()
        print(response)
        return response['choices'][0]['message']['content']

    def get_model_list(self):
        models = requests.get(f"{self.endpoint}/sequences", headers=self.headers).json()
        return [model['name'] for model in models]