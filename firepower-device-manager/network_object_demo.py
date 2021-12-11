import requests
import json
from rich import print

# new_net_object = {
#     "name": "GOOGLE-DNS",
#     "description": "Google public DNS server",
#     "subType": "HOST",
#     "value": "8.8.8.8",
#     "type": "networkobject"
# }

new_net_object = {
    "name": "KarmaTest",
    "description": "DEVCOR Training",
    "subType": "NETWORK",
    "value": "10.175.200.0/24",
    "dnsResolution": "IPV4_ONLY",
    "type": "networkobject"
}

class FDM_API:

    def __init__(self, host, username, password):
        """ Initialize FDM/FTD API object """

        self.base_url = f"https://{host}/api/fdm/latest"
        self.username = username
        self.password = password
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.get_token()

    def do_api_call (self, action, url, fdm_object = None):
        """
        Wrapper for API calls to avoid repeating code. Parameters:
        - action: HTTP verb: GET/POST/DELETE etc.
        - url: API-specific part of URL (prefixed with $base_url)
        - fdm_object: data for the POST calls
        Return: dict with the response results
        """

        api_call = requests.request(
            action,
            f"{self.base_url}/{url}",
            headers = self.headers,
            json = fdm_object,
            verify = False,
            timeout = 3,
        )
        api_call.raise_for_status()

        # debug output
        print (f" >> {action} to {api_call.url} / HTTP {api_call.status_code}")

        # HTTP 204 responses return empty output, .json() would fail with that
        if api_call.text:
            return api_call.json()

    def get_token(self):
        """ Obtain authentication token and use it in future calls """

        # full URL: "https://{host}/api/fdm/latest/fdm/token"
        api_path = "fdm/token"
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        response = self.do_api_call ("POST", api_path, data)
        access_token = response.get("access_token")
        self.headers['Authorization'] = f'Bearer {access_token}'

    def deploy (self):
        """
        Call "https://{host}/api/fdm/latest/operational/deploy"
        to deploy prepared configuration changes
        """

        response = self.do_api_call("POST", "operational/deploy")
        return True

def find_object_by_name (obj_name, obj_list):
    """
    Helper function
    Find if the object with a given "obj_name" exists in the "obj_list" list
    Return: ID of the existing object
    """

    for obj in obj_list:
        if obj_name['name'] == obj['name']:
            return obj['id']
    return None

def main():
    # Disable certificate warnings
    requests.packages.urllib3.disable_warnings()

    # Settings for the "Firepower Threat Defense REST API" DevNet sandbox
    fdm=FDM_API("10.10.20.65", "admin", "Cisco1234")

    # read and print current network objects
    fdm_net_objs = fdm.do_api_call("GET", "object/networks")
    for net_obj in fdm_net_objs['items']:
        # print(net_obj)
        print(f"Existing {net_obj['name']} object, ID:{net_obj['id']}")

    # Check if object with the same name already exists
    # if so, delete it first to avoid errors
    obj_id = find_object_by_name (new_net_object, fdm_net_objs['items'])
    if obj_id:
        print(f"{new_net_object['name']} object already exists, deleting...")
        fdm.do_api_call ("DELETE", f"object/networks/{obj_id}")

    # Create a new network object
    new_object = fdm.do_api_call ("POST", "object/networks", new_net_object)
    print(f"Created {new_object['name']} object, ID:{new_object['id']}")
    print(new_object)

    # Configuration changes need to be deployed to be activated
    # Note it will fail in the DevNet sandbox when it's Read-Only
    # fdm.deploy()

if __name__ == "__main__":
    main()