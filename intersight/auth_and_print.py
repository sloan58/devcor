import os
from os.path import join, dirname
import requests
from intersight_auth import IntersightAuth
from rich import print as rprint
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def main():
    api_key = os.environ.get('INTERSIGHT_KEY')
    privatekey = os.environ.get('INTERSIGHT_SECRET_FILE')
    auth = IntersightAuth(secret_key_filename=privatekey, api_key_id=api_key)
    get_request = requests.get(
        "https://intersight.com/api/v1/network/Elements", auth=auth
    )
    results = get_request.json()["Results"]
    rprint(results)
    import ipdb

    ipdb.set_trace()

if __name__ == "__main__":
    main()
