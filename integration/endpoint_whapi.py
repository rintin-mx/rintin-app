import sys
sys.path.append('..')
import requests

def send_post_request_to_api(group_id, message):
    api_url = f'https://gate.whapi.cloud/messages/text'
    body = {
        "to": group_id,
        "body": message,
    }
    headers = { # Note: Adjusted content-type
        'Authorization': 'Bearer 48XTINC05z564RAMEHkfrh8fXKas5xUX'
    }
    try:
        response = requests.post(api_url, headers=headers, json=body)
        response.raise_for_status() 
        print(response.json())# Raise an exception for non-2xx status codes
        return response
    except Exception as e:
        print(e)