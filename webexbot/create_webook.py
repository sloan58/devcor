import os
from os.path import join, dirname
import requests
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

base_url = 'https://webexapis.com/v1'
bearer_token = os.environ.get('BOT_TOKEN')

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {bearer_token}"
}

webhook = {
    "name": "DEVCOR Webhook",
    "targetUrl": "https://karmatek.ngrok.io/webhook",
    "resource": "messages",
    "event": "created",
}

#read current webhooks and delete them as a cleanup
response = requests.get(f"{base_url}/webhooks", headers=headers, json=webhook)
response.raise_for_status()

#delete them one by one
for item in response.json()["items"]:
    print (f'Deleting webhook \"{item["name"]}\"...')
    delete = requests.delete(f'{base_url}/webhooks/{item["id"]}', headers=headers)
    delete.raise_for_status()
    print (delete.status_code)

#create a new one
response = requests.post(f"{base_url}/webhooks", headers=headers, json=webhook)
response.raise_for_status()

webhook_id = response.json()["id"]
print(f"Webhook for {webhook['targetUrl']} added with ID\n{webhook_id}")