import sys
sys.path.append('..')

import aiohttp

from config import USER_WOOCOMMERCE, PASSWORD_WOOCOMMERCE,USER_WOOCOMMERCE_NOTE,PASSWORD_WOOCOMMERCE_NOTE
#para llamar este método se debe de importar el método y llamarlo de la siguiente manera
# result = await endpoint_update_status_by_order_id(order_id, order_status)
async def endpoint_update_status_by_order_id(order_id, order_status):
    url = f"https://rintin.mx/wp-json/wc/v3/orders/{order_id}"
    # Credenciales para la autenticación Basic Auth
    user = USER_WOOCOMMERCE
    password = PASSWORD_WOOCOMMERCE
    data = {
        "status": order_status
    }
    
    async with aiohttp.ClientSession() as session:
        # Utiliza la sesión para realizar una llamada PUT asíncrona
        async with session.put(url, auth=aiohttp.BasicAuth(user, password), json=data) as response:
            if response.status == 200:
                json_response = await response.json()

                return {"success": True, "message": "Éxito en la actualización del pedido", "response": json_response}
            else:
                
                text_response = await response.text()
                return {"success": False, "message": f"Error en la petición: {response.status} {text_response}"}


async def endpoint_write_order_note(order_id, order_notes):
    url = f"https://rintin.mx/wp-json/wc/v3/orders/{order_id}/notes"
    # Credenciales para la autenticación Basic Auth
    user = USER_WOOCOMMERCE_NOTE
    password = PASSWORD_WOOCOMMERCE_NOTE
    data = {"note": order_notes}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, auth=aiohttp.BasicAuth(user, password), json=data) as response:
            if response.status in [200, 201]:
                json_response = await response.json()
                return {"success": True, "message": "Nota añadida con éxito", "response": json_response}
            else:
                text_response = await response.text()
                return {"success": False, "message": f"Error en la petición: {response.status} {text_response}"}


async def endpoint_update_order_meta_data(order_id, meta_data):
    url = f"https://rintin.mx/wp-json/wc/v3/orders/{order_id}"
    # Credenciales para la autenticación Basic Auth
    user = USER_WOOCOMMERCE
    password = PASSWORD_WOOCOMMERCE
    data = {
        "meta_data": meta_data
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, auth=aiohttp.BasicAuth(user, password), json=data) as response:
            json_response = await response.json()
            if response.status == 200:
                json_response = await response.json()
                return {"success": True, "message": "Orden actualizada con éxito", "response": json_response}
            else:
                text_response = await response.text()
                return {"success": False, "message": f"Error en la petición: {response.status} {text_response}"}
