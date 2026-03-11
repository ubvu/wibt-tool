import requests
import json
import time

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
      }
      
      while True:
        try:
          response = requests.post(url, headers=headers, json=data)
          response_message_content = response.json()["choices"][0]["message"]["content"]
          return response_message_content
        except Exception as e:
          print(e)
          print("Failed to communicate with the llm endpoint. Retrying in a minute")
          time.sleep(1)

    def get_model_list(self):
      url = self.endpoint + "models"
      headers = {
          'Authorization': f'Bearer {self.token}',
      }
      
      response = requests.get(url, headers=headers)
      ids = []
      for model in response.json()['data']:
          ids += [model['id']]
      return ids