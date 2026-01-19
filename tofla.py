import requests
from lib.core.enums import PRIORITY

refresh_token = ""
priority = PRIORITY.NORMAL

def dependencies():
    pass

def getNewToken():
    url = ""
    payload = {
        "grant_type": "",
        "client_id": "",
        "client_secret": ""
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            json_response = response.json()
            access_token = json_response.get("access_token", "")
            return access_token
        else:
            print("Failed to get access token, Status Code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None

def tamper(payload, **kwargs):
    done = False
    while not done:
        try:
            access_token = getNewToken()
            if access_token:
                headers = kwargs.get("headers", {})
                headers["Authorization"] = "Bearer " + access_token
                kwargs["headers"] = headers
                done = True
            else:
                done = True
        except Exception as e:
            print("Error:", e)
            done = True
    return payload