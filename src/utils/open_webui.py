import requests
import json

class OpenWebuiClient:
    def __init__(self, token, endpoint):
        self.token = token
        self.endpoint = endpoint

    def send_messages(self, model, messages, temperature):
      url = self.endpoint + "chat/completions"
      headers = {
          'Authorization': f'Bearer {self.token}',
          'Content-Type': 'application/json'
      }
      data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "ctx": "100000" 
      }
      response = requests.post(url, headers=headers, json=data)
      return response.json()["choices"][0]["message"]["content"]

    def get_model_list(self):
      url = self.endpoint + "models"
      headers = {
          'Authorization': f'Bearer {self.token}',
          # 'Content-Type': 'application/json'
      }
      # data = { 
      # }
      response = requests.get(url, headers=headers)
      ids = []
      for model in response.json()['data']:
          ids += [model['id']]
      return ids
      # return response.json()["choices"][0]["message"]["content"]