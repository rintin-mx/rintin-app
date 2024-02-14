
import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
import pandas as pd
import numpy as np
import time

def config_db(db='repl') -> dict:
    # Registrar el tiempo de inicio
    if db == 'prod':
        config = {
            'user': USER,
            'password': PASSWORD,
            'host': HOST,
            'database': DATABASE,
            'charset': 'latin1'
        }
    else:
        config = {
            'user': USER_REPLICA,
            'password': PASSWORD_REPLICA,
            'host': HOST_REPLICA,
            'database': DATABASE_REPLICA
        }
    return config

def get_ordenes_compra(seller_name, db='repl') -> dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_ordenes_compra =f"""
            SELECT id_orden_compra, seller_name, estado, fecha_creacion, total_cost, total_paquetes FROM orden_compra WHERE seller_name = '{seller_name}' and (estado = 'solicitado_seller' or estado = 'ingresado_bodega_pendientes');
        """
        cursor.execute(wp_ordenes_compra)

        # Obtener los resultados de la primera consulta
        resultados_wp_ordenes_compra = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_ordenes = pd.DataFrame(resultados_wp_ordenes_compra)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
        # Registrar el tiempo de finalización
        end_time = time.time()

        # Calcular la duración
        duration = end_time - start_time

        # Convertir a minutos y segundos
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        # Nueva lista de nombres de columnas
        #wp_seller=wp_seller[['user_id' 'dokan_store_name']]
        if len(wp_ordenes) > 0:
            wp_ordenes.columns = ['id_orden_compra', 'seller_name', 'estado', 'fecha_creacion', 'total_cost', 'total_paquetes']
            wp_order_general_dict = wp_ordenes.to_dict(orient='list')
            return wp_order_general_dict
        return None

def get_live_sellers(db='repl') -> dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_seller_sql ="""
            select distinct seller_name from orden_compra where estado = 'solicitado_seller' or estado = 'ingresado_bodega_pendientes'
        """
        cursor.execute(wp_seller_sql)

        # Obtener los resultados de la primera consulta
        resultados_wp_seller_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_seller = pd.DataFrame(resultados_wp_seller_sql)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
        # Registrar el tiempo de finalización
        end_time = time.time()

        # Calcular la duración
        duration = end_time - start_time

        # Convertir a minutos y segundos
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        # Nueva lista de nombres de columnas
        #wp_seller=wp_seller[['user_id' 'dokan_store_name']]
        if len(wp_seller) > 0:
            wp_seller.columns = ['seller_name']
            wp_seller_general_dict = wp_seller.to_dict(orient='list')
            return wp_seller_general_dict
        return None

def insertOCItems(product_list, order_id, responsable):
    db ='prod'
    config = config_db(db)
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            for value in product_list:
                cursor = connection.cursor(dictionary=True)
                # Consulta SQL para insertar datos
                # Sentencia SQL para insertar datos
                sql = "INSERT INTO ingreso_items_ordenes_compra (id_orden_compra, id_producto_orden_compra, cantidad_ingreso, cantidad_no_ingreso, estado_ingreso, fecha, responsable) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                # Ejecutar la sentencia SQL
                cursor.execute(sql, (order_id, value['product_id'], value['ingreso'], value['no_ingreso'], value['razon'], time.strftime('%Y-%m-%d %H:%M:%S'), responsable))
                connection.commit()
            cursor.close()
            connection.close()
            return True
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False

def get_pending_products(id, db='repl') -> dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_products_ordenes_compra =f"""
with final as (
select 
	producto_orden_compra.id_producto_orden_compra as product_id, 
    cantidad_no_ingreso as line_paquetes, 
    sku_producto_wp, 
    nombre_producto,
    foto,
    units_per_pack,
    fecha
from orden_compra_detalle_producto 
inner join producto_orden_compra 
	on orden_compra_detalle_producto.id_producto_orden_compra = producto_orden_compra.id_producto_orden_compra 
inner join ingreso_items_ordenes_compra 
	on orden_compra_detalle_producto.id_producto_orden_compra = ingreso_items_ordenes_compra.id_producto_orden_compra
where orden_compra_detalle_producto.id_orden_compra = {id}
and estado_ingreso = 'Llegara en otro envio'
)
select
	product_id,
    line_paquetes,
    sku_producto_wp,
    nombre_producto,
    units_per_pack,
    foto,
    max(fecha) as fecha
from final
group by 
product_id,
    line_paquetes,
    sku_producto_wp,
    nombre_producto,
    units_per_pack,
    foto
	
	
        """
        cursor.execute(wp_products_ordenes_compra)

        # Obtener los resultados de la primera consulta
        resultados_wp_products_ordenes_compra = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_products = pd.DataFrame(resultados_wp_products_ordenes_compra)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
        # Registrar el tiempo de finalización
        end_time = time.time()

        # Calcular la duración
        duration = end_time - start_time

        # Convertir a minutos y segundos
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        # Nueva lista de nombres de columnas
        #wp_seller=wp_seller[['user_id' 'dokan_store_name']]
        wp_products.columns = ['product_id', 'line_paquetes', 'sku_producto_wp', 'nombre_producto','units_per_pack', 'foto', 'fecha']
        wp_products_general_dict = wp_products.to_dict(orient='list')
        return wp_products_general_dict

def get_products(id, db='repl') -> dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_products_ordenes_compra =f"""
            select producto_orden_compra.id_producto_orden_compra as product_id, line_paquetes, line_cost, sku_producto_wp, nombre_producto, tipo_producto, cost_of_goods, units_per_pack, foto from orden_compra_detalle_producto inner join producto_orden_compra on orden_compra_detalle_producto.id_producto_orden_compra = producto_orden_compra.id_producto_orden_compra where id_orden_compra = {id}
        """
        cursor.execute(wp_products_ordenes_compra)

        # Obtener los resultados de la primera consulta
        resultados_wp_products_ordenes_compra = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_products = pd.DataFrame(resultados_wp_products_ordenes_compra)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
        # Registrar el tiempo de finalización
        end_time = time.time()

        # Calcular la duración
        duration = end_time - start_time

        # Convertir a minutos y segundos
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        # Nueva lista de nombres de columnas
        #wp_seller=wp_seller[['user_id' 'dokan_store_name']]
        wp_products.columns = ['product_id', 'line_paquetes', 'line_cost', 'sku_producto_wp', 'nombre_producto', 'tipo_producto', 'cost_of_goods', 'units_per_pack', 'foto']
        wp_products_general_dict = wp_products.to_dict(orient='list')
        return wp_products_general_dict

def updateOrdenCompraStatus(status, id):
    db ='prod'
    config = config_db(db)
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "UPDATE orden_compra SET estado = %s WHERE id_orden_compra = %s"
            # Ejecutar la sentencia SQL
            cursor.execute(sql, (status, id))
            connection.commit()
            cursor.close()
            connection.close()
            return True
            
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False