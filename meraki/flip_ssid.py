import requests
import json
from rich import print

MY_ORG_NAME = "ACME, INC"
MY_NET_NAME = "Client_1"
MY_SSID_NAME = "Client_1 - wireless WiFi"

unknown_ssid = 255

base_url = "https://api.meraki.com/api/v0"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Cisco-Meraki-API-Key": "e0c80c7212c8af4ef964f7e8841fe56ad011a220",
}

def do_API_call(api_url, action = "GET", json = None):
    """
    Basic wrapper for API calls. Parameters:
    - resource: API-specific part of URL (prefixed with $base_url)
    - action: HTTP verb: GET/POST/DELETE etc.
    - json: data for PUT/POST calls
    Return: API response results
    """

    api_call = requests.request(
        method = action,
        url = f"{base_url}/{api_url}",
        headers = headers,
        json = json,
        timeout = 3,
    )

    # debug output
    print (f" >>> {action} to {api_call.url} / HTTP {api_call.status_code}")

    api_call.raise_for_status()
    if api_call.text:
        return api_call.json()

def find_networkId(org_name, net_name):
    """
    Parameters:
    - org_name: text organization name, may be partial as soon as unique
    - net_name: text network name, may be partial as soon as unique
    Return: ID of the network for API calls, or None if not found
    """

    # get a list of all organizations under account
    orgs = do_API_call("organizations")

    #loop through them to find org_name and its ID
    organizationId = 0
    for org in orgs:
        if org_name.lower() in org["name"].lower():
            print (f"Found a match for the {org['name']} org")
            organizationId = org["id"]
            break

    # if found, get a list of the networks and
    if organizationId:
        nets = do_API_call(f"organizations/{organizationId}/networks")

        # loop through them to find net_name and its ID
        for net in nets:
            print (f"Found a match for the {net['name']} network")
            if net_name.lower() in net["name"].lower():
                return net["id"]

    # by default (not found) return None
    return None

def find_ssid_nr(networkId, ssid_name):
    """
    Return target SSID's ID in the network or "unknown_ssid" if not found
    """

    # get a list of all SSIDs for the network
    ssids = do_API_call(f"networks/{networkId}/ssids")

    # loop through them to find SSID and its ID
    for ssid in ssids:
        if ssid_name.lower() in ssid["name"].lower():
            print (
                f"Found a match for the {ssid['name']} network, "
                f"SSID# {ssid['number']}"
            )
            return ssid["number"]

    # Use SSID value of 255 to indicate "not found"
    return unknown_ssid

def state_name(state):
    """ Return printable SSID state name """
    return "enabled" if state else "disabled"

def main():

    # obtain networkId from the network name
    my_network = find_networkId(MY_ORG_NAME, MY_NET_NAME)
    if not my_network:
        print (f"Network {MY_NET_NAME} not found in the {MY_ORG_NAME} org")
        exit ()

    # obtain SSID # from the SSID name
    my_ssid_nr = find_ssid_nr (my_network, MY_SSID_NAME)
    if my_ssid_nr == unknown_ssid:
        print (f"SSID {MY_SSID_NAME} not found in the network {MY_NET_NAME}")
        exit ()

    #Read the current state
    ssid_state = do_API_call(f"networks/{my_network}/ssids/{my_ssid_nr}")
    print (f'Current state is {state_name(ssid_state["enabled"])}')

    #Print SSID data structure
    print (json.dumps(ssid_state, indent=4))

    # toggle SSID's "enabled" value
    new_ssid_state = not ssid_state["enabled"]

    #Update SSID state
    update_req = do_API_call(
        api_url = f"networks/{my_network}/ssids/{my_ssid_nr}",
        action = "PUT",
        json = {"enabled": new_ssid_state},
    )

    # print a returned new state to confirm
    print (f'New state is {state_name(update_req["enabled"])}')

if __name__ == "__main__":
    main()