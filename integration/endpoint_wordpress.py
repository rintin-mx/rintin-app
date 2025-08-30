import sys
import logging
import os
from datetime import datetime

# Configurar logging para update_order_status
log_dir = "/home/ubuntu/rintinApp/logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"order_status_updates_{datetime.now().strftime('%Y%m%d')}.log")

# Configurar el logger
order_logger = logging.getLogger("order_status_updates")
order_logger.setLevel(logging.DEBUG)

# Crear file handler si no existe
if not order_logger.handlers:
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    order_logger.addHandler(file_handler)

sys.path.append('..')

import aiohttp
from config import USER_WOOCOMMERCE, PASSWORD_WOOCOMMERCE,USER_WOOCOMMERCE_NOTE,PASSWORD_WOOCOMMERCE_NOTE, USER_WORDPRESS, PASSWORD_WORDPRESS
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
async def update_order_status(order_id, order_status, order_items=None):
    """
    Llama al endpoint personalizado de Rintin para actualizar el estado de una orden
    
    Args:
        order_id: ID de la orden a actualizar
        order_status: Nuevo estado de la orden (ej: 'wc-stock-2')
        order_items: Lista de items con información de stock (opcional, usado cuando hay faltantes)
            Cada item debe tener:
            - product_id: ID del producto
            - name: Nombre del producto
            - sku: SKU del producto
            - pick_amount: Cantidad confirmada/pickeada
            - original_quantity: Cantidad original ordenada
            - product_code: Código del producto de reemplazo
            - product_price: Precio del producto de reemplazo
            - product_difference: Diferencia/descripción del reemplazo
    
    Returns:
        dict: Respuesta del servidor con success, message y response
    """
    # DEBUG: Logging de parámetros
    order_logger.debug("="*80)
    order_logger.debug(f" update_order_status llamado con:")
    order_logger.debug(f"  - order_id: {order_id}")
    order_logger.debug(f"  - order_status: {order_status}")
    order_logger.debug(f"  - order_items cantidad: {len(order_items) if order_items else 0}")
    if order_items:
        order_logger.debug(f"  - order_items contenido:")
        for idx, item in enumerate(order_items):
            order_logger.debug(f"    Item {idx + 1}:")
            order_logger.debug(f"      - product_id: {item.get('product_id')}")
            order_logger.debug(f"      - name: {item.get('name')}")
            order_logger.debug(f"      - sku: {item.get('sku')}")
            order_logger.debug(f"      - pick_amount: {item.get('pick_amount')}")
            order_logger.debug(f"      - original_quantity: {item.get('original_quantity')}")
            order_logger.debug(f"      - product_code: {item.get('product_code')}")
            order_logger.debug(f"      - product_price: {item.get('product_price')}")
            order_logger.debug(f"      - product_difference: {item.get('product_difference')}")
    else:
        order_logger.debug("  - order_items está vacío o es None")
    order_logger.debug("="*80)
    
    # Construir la URL del endpoint personalizado
    url = f"https://rintin.mx/wp-json/rintin/v1/order/update-status/{order_id}"
    
    # Preparar los datos a enviar
    data = {
        "order_status": order_status
    }
    
    # Si hay items de orden, incluirlos en los datos
    if order_items:
        data["order_items"] = order_items
    
    # Credenciales para la autenticación Basic Auth
    user = USER_WORDPRESS
    password = PASSWORD_WORDPRESS
    
    order_logger.debug(f"Llamando a API: {url}")
    order_logger.debug(f"Datos a enviar: {data}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Realizar la llamada PUT al endpoint personalizado
            async with session.put(url, auth=aiohttp.BasicAuth(user, password), json=data) as response:
                response_text = await response.text()
                order_logger.debug(f"Respuesta status: {response.status}")
                order_logger.debug(f"Respuesta text: {response_text}")
                
                if response.status == 200:
                    try:
                        json_response = await response.json()
                        order_logger.info(f"Orden {order_id} actualizada exitosamente a estado: {order_status}")
                        return {"success": True, "message": "Éxito en la actualización del pedido", "response": json_response}
                    except:
                        # Si no puede parsear JSON, devolver el texto
                        order_logger.info(f"Orden {order_id} actualizada (respuesta no JSON)")
                        return {"success": True, "message": "Éxito en la actualización del pedido", "response": response_text}
                else:
                    order_logger.error(f"Error actualizando orden {order_id}: Status {response.status}, Response: {response_text}")
                    return {"success": False, "message": f"Error en la petición: {response.status} {response_text}"}
    except Exception as e:
        order_logger.error(f"Excepción al actualizar orden {order_id}: {str(e)}")
        return {"success": False, "message": f"Error de conexión: {str(e)}"}

