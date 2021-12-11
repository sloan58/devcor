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
        "https://intersight.com/api/v1/network/Elements?$filter=SwitchId eq 'A'", auth=auth
    )
    results = get_request.json()["Results"]
    if not results:
        rprint("[red]No Devices Detected[/red]")
        return

    for result in results:
        oob = result["OutOfBandIpv4Address"]
        sw_id = result["SwitchId"]
        serial = result['Serial']
        model = result['Model']
        rprint(
            f"Switch: [red]{sw_id}[/red]",
            f"Model: [blue]{model}[/blue]",
            f"MGMT IP: [green]{oob}[/green]",
            f"Serial No: [cyan]{serial}[/cyan]",
        )

if __name__ == "__main__":
    main()
