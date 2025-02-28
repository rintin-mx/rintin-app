import sys

from config import WATI_BASE_URL, WATI_TOKEN

sys.path.append('..')
import json

import aiohttp
import requests

def send_post_request_to_api(template, parameters, customer_phone_number):
    api_url = f'{WATI_BASE_URL}/sendTemplateMessage?whatsappNumber={customer_phone_number}'
    body = {
        "parameters": parameters,
        "broadcast_name": template,
        "template_name": template
    }
    headers = {
        'content-type': "text/json",  # Note: Adjusted content-type
        'Authorization': f'Bearer {WATI_TOKEN}',
    }
    try:
        response = requests.post(api_url, headers=headers, json=body)
        response.raise_for_status() 
        print(response.json())# Raise an exception for non-2xx status codes
        return response
    except Exception as e:
        print(e)

    
