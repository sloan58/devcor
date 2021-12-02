import os
from os.path import join, dirname
from flask import Flask, request, json
import requests
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
port = 5010

bearer_token = os.environ.get('BOT_TOKEN')
base_url = 'https://webexapis.com/v1/'
me = 'devnetcor@webex.bot'

class Messenger():
    def __init__(self, base_url=base_url, bearer_token=bearer_token):
        self.base_url = base_url
        self.bearer_token = bearer_token
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }

    def get_message(self, message_id):
        received_message_url = f'{self.base_url}/messages/{message_id}'
        message_text = requests.get(received_message_url,
                                    headers=self.headers).json().get('text')
        return (message_text)

    def post_message(self, room_id, message):
        data = {
            "roomId": room_id,
            "text": message,
            }
        post_message_url = f'{self.base_url}/messages'
        requests.post(post_message_url, headers=self.headers,
                                     data=json.dumps(data))

msg = Messenger()

@app.route('/webhook', methods=['POST'])
def webhook():
    if 'application/json' in request.headers.get('Content-Type'):
        data = request.get_json()
        
        from_email = data.get('data').get('personEmail')

        if from_email == me:
            return ('', 200)
        
        room_id = data.get('data').get('roomId')
        message_id = data.get('data').get('id')
        message = msg.get_message(message_id)

        reply = f'Bot received message "{message}"'
        msg.post_message(room_id, reply)

        return data
            
    else:
        return ('Wrong data format', 400)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)