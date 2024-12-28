import requests
import json

response = requests.get("http://api.open-notify.org/astros")
print(response.status_code)
custom_prompt = "Why the sky is blue?"
url = "http://localhost:11434/api/generate"
payload = {"model": "llama2", "prompt": custom_prompt, "stream": False}
headers = {'Content-type': 'raw'}

json_data = json.dumps(payload)
#response = requests.post(url, headers=headers, json=json_data)
#print(response.status_code)

#data = response.json()
#print(data)
