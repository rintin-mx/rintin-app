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
            'database': DATABASE
        }
    else:
        config = {
            'user': USER_REPLICA,
            'password': PASSWORD_REPLICA,
            'host': HOST_REPLICA,
            'database': DATABASE_REPLICA
        }
    return config

def updateOrdenCompra(order_id, orderInfo, products):
    db ='prod'
    config = config_db(db)
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "UPDATE orden_compra SET total_paquetes = %s, orden_compra_padre = %s, bodega_recepcion = %s, total_cost = %s, fecha_edicion = %s where id_orden_compra = %s"
            cursor.execute(sql, (orderInfo['total_paquetes'], orderInfo['orden_padre'], orderInfo['bodega_recepcion'], orderInfo['total_cost'],orderInfo['fecha_edicion'], order_id))
            connection.commit()
            for value in products:
                
                if 'product_id' not in value:
                    sql = "INSERT INTO producto_orden_compra (sku_producto_wp, nombre_producto, tipo_producto, cost_of_goods, units_per_pack, foto, fecha_creacion, fecha_edicion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (value['sku'], value['nombre'], value['tipo_producto'], value['costo'], value['units_per_pack'] , value['img_url'], orderInfo['fecha_edicion'], orderInfo['fecha_edicion']))
                    connection.commit()
                    insertedProductId = cursor.lastrowid
                    sql = "INSERT INTO orden_compra_detalle_producto (id_producto_orden_compra, id_orden_compra, line_paquetes, line_cost, fecha_creacion, fecha_edicion) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (insertedProductId, order_id, value['cantidad_pack'], value['costo'] * value['cantidad_pack'], orderInfo['fecha_edicion'], orderInfo['fecha_edicion']))
                    connection.commit()
                else:
                    sql = "UPDATE orden_compra_detalle_producto SET line_paquetes = %s, line_cost = %s WHERE id_orden_compra = %s and id_producto_orden_compra = %s"
                    # Ejecutar la sentencia SQL
                    cursor.execute(sql, (value['cantidad_pack'], value['costo'] * value['cantidad_pack'], int(order_id) , int(value['product_id'])))
                    connection.commit()
                    sql = "UPDATE producto_orden_compra SET sku_producto_wp = %s, nombre_producto = %s, tipo_producto = %s, cost_of_goods = %s, units_per_pack = %s, foto = %s, fecha_edicion = %s WHERE id_producto_orden_compra = %s"
                    # Ejecutar la sentencia SQL
                    cursor.execute(sql, (value['sku'], value['nombre'], value['tipo_producto'], value['costo'] , value['units_per_pack'] , value['img_url'], time.strftime('%Y-%m-%d %H:%M:%S'), int(value['product_id'])))
                    connection.commit()
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False
    
def insertOrdenCompra(orderInfo, products):
    db ='prod'
    config = config_db(db)
    start_time = time.time()
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "INSERT INTO orden_compra (codigo_seller, orden_compra_padre, seller_name, estado, total_paquetes, total_cost, usuario_creacion, fecha_creacion, fecha_edicion, bodega_recepcion) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s)"
            # Ejecutar la sentencia SQL
            cursor.execute(sql, (orderInfo['codigo_seller'], orderInfo['orden_padre'], orderInfo['seller_name'], 'Solicitado Seller', orderInfo['total_paquetes'], orderInfo['total_cost'],orderInfo['usuario_creacion'], orderInfo['fecha_creacion'], orderInfo['fecha_edicion'], orderInfo['bodega_recepcion']))
            connection.commit()
            insertedId = cursor.lastrowid
            for value in products:
                sql = "INSERT INTO producto_orden_compra (sku_producto_wp, nombre_producto, tipo_producto, cost_of_goods, units_per_pack, foto, fecha_creacion, fecha_edicion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (value['sku'], value['nombre'], value['tipo_producto'], value['costo'], value['units_per_pack'], value['img_url'], orderInfo['fecha_creacion'], orderInfo['fecha_edicion']))
                connection.commit()
                insertedProductId = cursor.lastrowid
                sql = "INSERT INTO orden_compra_detalle_producto (id_producto_orden_compra, id_orden_compra, line_paquetes, line_cost, fecha_creacion, fecha_edicion) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (insertedProductId, insertedId, value['cantidad_pack'], value['costo'] * value['cantidad_pack'], orderInfo['fecha_creacion'], orderInfo['fecha_edicion']))
                connection.commit()

            cursor.close()
            connection.close()
            return insertedId
            
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False

def get_order_info(id, db='repl')->dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_products_ordenes_compra =f"""
            select orden_compra_padre, bodega_recepcion from orden_compra where id_orden_compra = {id}
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
        wp_products.columns = ['orden_compra_padre', 'bodega_recepcion']
        wp_products_general_dict = wp_products.to_dict(orient='list')
        return wp_products_general_dict

def get_parent_orders(db='repl')->dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        ordenes_padre_sql =f"""
            select id_orden_compra from orden_compra where orden_compra_padre = 0
        """
        cursor.execute(ordenes_padre_sql)

        # Obtener los resultados de la primera consulta
        resultados_ordenes_padre_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        ordenes_padre = pd.DataFrame(resultados_ordenes_padre_sql)
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
        if len(ordenes_padre) > 0:
            ordenes_padre.columns = ['id_orden_compra']
            ordenes_padre_general_dict = ordenes_padre.to_dict(orient='list')
            return ordenes_padre_general_dict
        return None

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

def get_ordenes_compra(db='repl') -> dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_ordenes_compra ="""
            SELECT id_orden_compra, codigo_seller, seller_name, estado, fecha_creacion, total_cost FROM orden_compra;
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
        wp_ordenes.columns = ['id_orden_compra', 'codigo_seller', 'seller_name', 'estado', 'fecha_creacion', 'total_cost']
        wp_order_general_dict = wp_ordenes.to_dict(orient='list')
        return wp_order_general_dict

def update_oi_values(order_compra_id, products):
    db ='prod'
    config = config_db(db)
    start_time = time.time()
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            for values in products:
                sql = "UPDATE orden_compra_detalle_producto SET line_paquetes = %s, line_cost = %s WHERE id_orden_compra = %s and id_producto_orden_compra = %s"
                # Ejecutar la sentencia SQL
                cursor.execute(sql, (values['cantidad_pack'], values['costo'] * values['cantidad_pack'], int(order_compra_id) , int(values['product_id'])))
                connection.commit()

            cursor.close()
            connection.close()
            
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False
          
def update_product(product, product_id):
    db ='prod'
    config = config_db(db)
    start_time = time.time()
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "UPDATE producto_orden_compra SET sku_producto_wp = %s, nombre_producto = %s, tipo_producto = %s, cost_of_goods = %s, foto = %s, fecha_edicion = %s WHERE id_producto_orden_compra = %s"
            # Ejecutar la sentencia SQL
            cursor.execute(sql, (product['sku'], product['nombre'], product['tipo_producto'], product['costo'] , product['img_url'], time.strftime('%Y-%m-%d %H:%M:%S'), product_id))
            connection.commit()
            cursor.close()
            connection.close()
            
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False
    
def deleteProducts(products, order_id):
    db ='prod'
    config = config_db(db)
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            for value in products:
                sql = "DELETE from orden_compra_detalle_producto WHERE id_orden_compra = %s and id_producto_orden_compra = %s"
                cursor.execute(sql, (order_id, value))
                connection.commit()
            cursor.close()
            connection.close()
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False
    
def get_live_sellers(db='repl') -> dict:
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_seller_sql ="""
            with a as (select
            user_id,
            max(
                case
                    when `meta_key` = 'wp_capabilities' then `meta_value`
                    else NULL
                end
            ) AS `wp_capabilities`,
            max(
                case
                    when `meta_key` = 'dokan_enable_selling' then `meta_value`
                    else NULL
                end
            ) AS `dokan_enable_selling`,
            max(
                case
                    when `meta_key` = 'dokan_store_name' then `meta_value`
                    else NULL
                end
            ) AS `dokan_store_name`
            from wp_usermeta 
            group by user_id
            having wp_capabilities like '%seller%' and dokan_enable_selling = 'yes')
            select user_id, dokan_store_name from a
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
        wp_seller.columns = ['user_id', 'dokan_store_name']
        wp_seller_general_dict = wp_seller.to_dict(orient='list')
        return wp_seller_general_dict