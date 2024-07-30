import requests
from requests.auth import HTTPBasicAuth

from config import USER_WORDPRESS, PASSWORD_WORDPRESS

def update_stock_by_sku(sku, qty, source):

    '''
    Update product stock and state

    params:
    sku (str): products sku
    qty (str): new qty stock of the product
    source (str): reason code of the stock change

    returns: nothing
    '''

    url = f"https://rintin.mx/wp-json/rintin/v1/product/stock"
    # Credenciales para la autenticación Basic Auth
    user = USER_WORDPRESS
    password = PASSWORD_WORDPRESS
    data = {
        "sku": sku,
        "quantity": qty,
        "source": source
    }
    # requests authentication
    basic = HTTPBasicAuth(user, password)
    response = requests.put(url, json=data, auth=basic)
    print(response.content)