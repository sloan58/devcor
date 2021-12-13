import requests
import json
import sys

# default values for the Cisco DevNet sandbox
SANDBOX = "sandboxdnac2.cisco.com"
USERNAME = "devnetuser"
PASSWORD = "Cisco123!"

class DNAC_API:

    def __init__(self, host, username, password):
        self.system_url = f"https://{host}/dna/system/api/v1"
        self.intent_url = f"https://{host}/dna/intent/api/v1"

        self.username = username
        self.password = password
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Obtain Authentication Token and
        # add it to "headers" for the future API calls
        self.headers["X-Auth-Token"] = self.get_token()

    def get_token(self):
        """ Perform Basic Authentication and obtain API Token """

        auth = (self.username, self.password)
        auth_resp = requests.post(
            f"{self.system_url}/auth/token",
            auth=auth,
            headers=self.headers,
            verify=False
        )
        auth_resp.raise_for_status()
        return auth_resp.json()["Token"]

    def api_read (self, api_url):
        """ Perform "GET" DNA Center API call """

        response = requests.get(
            f"{self.intent_url}/{api_url}",
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        return response.json()

def main():

    requests.packages.urllib3.disable_warnings()
    dnac = DNAC_API(SANDBOX, USERNAME, PASSWORD)

    print ("*** Network Wireless Health status ***")
    site_health = dnac.api_read("site-health")['response']
    
    for site in site_health:
        if site['wirelessDeviceTotalCount']:        # skip empty sites
            print(f"Site: {site['siteName']}: \n"
                f"  Wireless Network Health: {site['networkHealthWireless']}% "
                f"({site['wirelessDeviceGoodCount']}/"
                f"{site['wirelessDeviceTotalCount']} OK) \n"
                f"  Wireless Client Health: {site['clientHealthWireless']}% "
                f"for {site['numberOfWirelessClients']} clients"
            )

    print ("\n*** Client Wireless Health status ***")
    client_health = dnac.api_read("client-health")['response'][0]
    for score in client_health["scoreDetail"]:
        print(
            f"Health score for {score['scoreCategory']['value']}: "
            f"{score['scoreValue']}% for {score['clientCount']} clients"
        )
        # drill down into score categories
        scorelist = score.get('scoreList',{})
        for scoreitem in scorelist:
            if scoreitem['clientCount'] > 0:        # skip empty ones
                print(
                    f"  {scoreitem['scoreCategory']['value']}"
                    f": {scoreitem['clientCount']} clients"
                )

if __name__ == "__main__":
    main()