import sys
sys.path.append('..')
import json

import aiohttp
import requests

def send_post_request_to_api(template, parameters, customer_phone_number):
    api_url = f'https://live-server-11723.wati.io/api/v1/sendTemplateMessage?whatsappNumber={customer_phone_number}'
    body = {
        "parameters": parameters,
        "broadcast_name": template,
        "template_name": template
    }
    headers = {
        'content-type': "text/json",  # Note: Adjusted content-type
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3NGNmZjI1OS00Nzk4LTRhNTUtYjNkOS0wYjhiODEwNTgzMmIiLCJ1bmlxdWVfbmFtZSI6ImFkbWluQHJpbnRpbi5jbyIsIm5hbWVpZCI6ImFkbWluQHJpbnRpbi5jbyIsImVtYWlsIjoiYWRtaW5AcmludGluLmNvIiwiYXV0aF90aW1lIjoiMDcvMjUvMjAyMyAxNjo1ODowMyIsImRiX25hbWUiOiIxMTcyMyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFETUlOSVNUUkFUT1IiLCJleHAiOjI1MzQwMjMwMDgwMCwiaXNzIjoiQ2xhcmVfQUkiLCJhdWQiOiJDbGFyZV9BSSJ9.gFGAM_Dc5UfwDrtlruZ649XI2KlGPtE65fGM7nepO7o'
    }
    try:
        response = requests.post(api_url, headers=headers, json=body)
        response.raise_for_status() 
        print(response.json())# Raise an exception for non-2xx status codes
        return response
    except Exception as e:
        print(e)

    
