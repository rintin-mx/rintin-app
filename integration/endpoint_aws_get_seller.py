import requests
import sys
sys.path.append('..')
from config import aws_endpoint_getSeller_url
import json
def get_seller():

    url = aws_endpoint_getSeller_url

    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", url, headers=headers)

    return json.dumps(response)