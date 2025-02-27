# db/script_db.py
import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
from mysql.connector import Error
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

def get_seller_centro(db='repl') -> dict:
    # Registrar el tiempo de inicio
    config = config_db(db)
    start_time = time.time()
    
    try:
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor(dictionary=True)

        wp_seller_sql = """
            WITH filtered_orders AS (
                SELECT o.id AS order_id
                FROM wp_posts o
                LEFT JOIN wp_posts child ON child.post_parent = o.id
                WHERE o.post_status IN ('wc-auditoria-2', 'wc-rec_ped_aud', 'wc-pedidos_auditar')
                AND child.id IS NULL
            ),
            vendor_info AS (
                SELECT
                    pm.post_id AS order_id,
                    pm.meta_value AS vendor_id
                FROM wp_postmeta pm
                INNER JOIN filtered_orders fo ON fo.order_id = pm.post_id
                WHERE pm.meta_key = '_dokan_vendor_id'
            ),
            vendors_in_centro AS (
                SELECT DISTINCT um.user_id
                FROM wp_usermeta um
                WHERE um.meta_key = '_zone' AND um.meta_value = 'centro'
            ),
            seller_names AS (
                SELECT
                    um.user_id,
                    um.meta_value AS seller_name
                FROM wp_usermeta um
                WHERE um.meta_key = 'dokan_store_name'
            ),
            order_info AS (
                SELECT
                    vi.order_id,
                    sn.seller_name
                FROM vendor_info vi
                INNER JOIN vendors_in_centro vic ON vi.vendor_id = vic.user_id
                INNER JOIN seller_names sn ON vi.vendor_id = sn.user_id
            )
            SELECT 
                oi.order_id,
                oi.seller_name,
                COALESCE(GROUP_CONCAT(DISTINCT rapi.incidencia SEPARATOR '; '), '-') AS incidencias
            FROM order_info oi
            LEFT JOIN wordpress.rintin_auditoria_productos_incidencias rapi 
                ON oi.order_id = rapi.order_id
            GROUP BY oi.order_id, oi.seller_name;
        """
        
        cursor.execute(wp_seller_sql)
        resultados_wp_seller_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_seller = pd.DataFrame(resultados_wp_seller_sql)

    finally:
        cursor.close()
        conexion.close()
        end_time = time.time()
        duration = end_time - start_time

        if len(wp_seller) > 0:
            wp_seller.columns = ['ID', 'Seller', 'Incidencias'] 
            return wp_seller.to_dict(orient='list')
        else:
            return {}

def product_confirm_change(order_item_id, nuevo_producto_sku, cantidad_reemplazada, fecha):
    db ='prod'
    config = config_db(db)
    start_time = time.time()

    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "INSERT INTO cambios_productos (order_item_id, nuevo_producto_sku, cantidad_reemplazada, fecha) VALUES (%s, %s, %s, %s)"
            # Ejecutar la sentencia SQL
            cursor.execute(sql, (order_item_id, nuevo_producto_sku, cantidad_reemplazada, fecha))
            connection.commit()

            print("Cambio insertado con éxito.")
            

    except Error as e:
        print("Error al conectar a la base de datos:", e)

    finally:
        # Cerrar la conexión y el cursor
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")

def get_order_status(id, db='repl') -> str:
    config = config_db(db)

    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        # id = {id}
        status = f"""
            select
                post_status
            from
                wp_posts
            where
                id={id}
        """
    
        # Ejecutar la primera consulta
        cursor.execute(status)

        # Obtener los resultados de la primera consulta
        resultados_status = cursor.fetchall()
        # Convertir los resultados a un DataFrame de pandas
        status = pd.DataFrame(resultados_status)

    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

    return status['post_status'][0]

def get_product_changes(id, db='repl') -> str:
    config = config_db(db)

    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        # id = {id}
        cambios = f"""
            select 
                order_item_id,
                nuevo_producto_sku 
            from 
                cambios_productos 
            where 
                order_item_id in ({id})
        """
    
        # Ejecutar la primera consulta
        cursor.execute(cambios)

        # Obtener los resultados de la primera consulta
        resultados_cambios = cursor.fetchall()
        # Convertir los resultados a un DataFrame de pandas
        cambios = pd.DataFrame(resultados_cambios)

    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

    return cambios

def get_order_auditoria(id,db='repl') -> dict:
    config = config_db(db)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        #and id={id}
        wp_pickeo_sql = f"""
            with orders as (
                    select
                        id
                    from
                        wp_posts
                    where
                        id={id}
                    and post_status IN  ('wc-auditoria-2', 'wc-rec_ped_aud', 'wc-pedidos_auditar')
                        
                ),
                ordermeta as(
                    select
                        post_id as order_id,
                        max(
                            case
                                when `meta_key` = '_dokan_vendor_id' then `meta_value`
                                else NULL
                            end
                        ) AS `dokan_vendor_id`
                    from
                        wp_postmeta inner join orders on orders.id = post_id
                    group by post_id
                ),
                order_items as(
                    select order_item_id, ordermeta.order_id, order_item_name,dokan_vendor_id
                    from wp_woocommerce_order_items
                    inner join ordermeta on wp_woocommerce_order_items.order_id = ordermeta.order_id
                    where order_item_type = 'line_item'
                ),
                order_item_meta as (
                    select
                        `wp_woocommerce_order_itemmeta`.`order_item_id` AS `order_item_id`,
                        max(
                            case
                                when `wp_woocommerce_order_itemmeta`.`meta_key` = '_qty' then `wp_woocommerce_order_itemmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `line_qty`,
                        max(
                            case
                                when `wp_woocommerce_order_itemmeta`.`meta_key` = '_product_id' then `wp_woocommerce_order_itemmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `product_id`
                        
                    from
                        `wp_woocommerce_order_itemmeta`
                        inner join order_items on order_items.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
                    group by
                        `wp_woocommerce_order_itemmeta`.`order_item_id`
                ),
                product_meta as(
                    select
                        post_id as product_id, 
                        max(
                            case
                                when `wp_postmeta`.`meta_key` = '_sku' then `wp_postmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `sku`,
                        max(
                            case
                                when `wp_postmeta`.`meta_key` = '_thumbnail_id' then `wp_postmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `image_id`,
                        max(
                            case
                                when `wp_postmeta`.`meta_key` = '_units_per_pack' then `wp_postmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `units_per_pack`
                    from wp_postmeta
                    inner join order_item_meta on order_item_meta.product_id = post_id
                    group by post_id
                ),
                seller_meta as(
                select
                user_id,
                max(
					case
						when `wp_usermeta`.`meta_key` = 'bodega' then `wp_usermeta`.`meta_value`
						else NULL
					end
				) AS `bodega`
                
                from
                wp_usermeta
                group by user_id
                )
                select
                    order_items.order_id,
                    product_meta.product_id,
                    order_items.dokan_vendor_id as seller_id,
                    order_items.order_item_name,
                    line_qty,
                    sku,
                    units_per_pack,
                    replace(wp_posts.guid, 'http://dev.', 'https://') as img_url,
                    bodega,
                    order_items.order_item_id
                from 
                    order_items
                    left join order_item_meta on order_item_meta.order_item_id = order_items.order_item_id
                    left join product_meta on order_item_meta.product_id = product_meta.product_id
                    left join wp_posts on wp_posts.id = product_meta.image_id  
                    left join seller_meta on seller_meta.user_id = order_items.dokan_vendor_id
        """
                
        # Ejecutar la primera consulta
        cursor.execute(wp_pickeo_sql)

        # Obtener los resultados de la primera consulta
        resultados_wp_pickeo_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_pickeo = pd.DataFrame(resultados_wp_pickeo_sql)
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
   #order_id,order_item_name,line_qty,sku,img_url, estado
    if len(wp_pickeo) > 0:
        wp_pickeo = wp_pickeo[['order_id','order_item_name','line_qty','sku','img_url','units_per_pack','product_id','seller_id', 'bodega', 'order_item_id']]
        # Nueva lista de nombres de columnas
        wp_pickeo.columns = ['order_id', 'Producto','Cantidad','SKU','Imagen','units_per_pack','product_id','seller_id', 'bodega', 'order_item_id']
        #print(f"El script se ejecutó en {minutes} minutos y {seconds} segundos.")
        wp_pickeo_general_dict = wp_pickeo.to_dict(orient='list')
        return wp_pickeo

def valido_bodega_CDMX(id,db='repl') -> dict:
    config = config_db(db)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        #and id={id}
        wp_pickeo_sql = f"""
            WITH orders AS (
            SELECT
                wp_posts.id,
                wp_posts.post_status,
                wp_dokan_orders.seller_id
            FROM
                wp_posts
                left join wp_dokan_orders ON wp_dokan_orders.order_id = wp_posts.id
            WHERE
                post_status = 'wc-recolectar-2'
            ),
            ordermeta AS(
            SELECT
                post_id AS order_id,
                post_status,
                max(
                CASE
                    WHEN `meta_key` = '_dokan_vendor_id' THEN `meta_value`
                    ELSE orders.seller_id
                END
                ) AS `dokan_vendor_id`
            FROM
                wp_postmeta
                INNER JOIN orders ON orders.id = post_id
            GROUP BY
                post_id,
                post_status
            ),
            users AS (
            SELECT
                user_id,
                max(
                CASE
                    WHEN `meta_key` = 'dokan_store_name' THEN `meta_value`
                    ELSE NULL
                END
                ) AS `dokan_store_name`,
                max(
                CASE
                    WHEN `meta_key` = 'bodega' THEN `meta_value`
                    ELSE NULL
                END
                ) AS `bodega`
            FROM
                wp_usermeta
                INNER JOIN ordermeta ON ordermeta.dokan_vendor_id = user_id
            GROUP BY
                user_id
            )
            SELECT
             CASE
		        WHEN count(order_id) = 1 THEN 'CDMX'
		        ELSE 'NoCDMX'
		    END AS es_cdmx
            FROM
            ordermeta
            INNER JOIN users ON users.user_id = ordermeta.dokan_vendor_id
                WHERE  order_id={id} and 
                bodega IN ('centro_cdmx', 'aj_cdmx')
            ORDER BY
            order_id ASC
        """
                
        # Ejecutar la primera consulta
        cursor.execute(wp_pickeo_sql)

        # Obtener los resultados de la primera consulta
        resultados_wp_pickeo_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_es_bodega = pd.DataFrame(resultados_wp_pickeo_sql)
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
   #order_id,order_item_name,line_qty,sku,img_url, estado
    if len(wp_es_bodega) > 0:
        return wp_es_bodega
    else:
        return {}

def checkForChildStatusses(orderId, db='repl'):
    config = config_db(db)
    try:
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor(dictionary=True)
        check_statusses = f"""
          WITH orders_grouped_by_parent AS (
                SELECT 
                    post_parent,
                    SUM(
                        CASE
                            WHEN post_status = 'wc-agrupar-pedidos' THEN 1 
                            ELSE 0
                        END
                    ) AS num_agrupados,
                    COUNT(
                        CASE
                            WHEN post_status NOT IN (
                                'wc-pendientes_ograma',
                                'wc-failed',
                                'wc-caducado',
                                'wc-cancelled',
                                'wc-devuelto',
                                'wc-devolucion_proces',
                                'wc-delivered',
                                'wc-contracargo-ganad',
                                'wc-contra-cargo',
                                'wc-refunded',
                                'wc-reembolso-parcial'
                            ) THEN id
                            ELSE NULL
                        END
                    ) AS childs
                FROM wp_posts 
                WHERE post_parent != 0 
                AND post_type = 'shop_order'
                GROUP BY post_parent
            ),
            final AS (
                SELECT 
                    wp_posts.id, 
                    orders_grouped_by_parent.num_agrupados, 
                    orders_grouped_by_parent.childs, 
                    wp_posts.post_parent,
                    wp_posts.post_date
                FROM wp_posts 
                INNER JOIN orders_grouped_by_parent 
                    ON wp_posts.post_parent = orders_grouped_by_parent.post_parent
                    
                UNION
                
                SELECT
                    id,
                    CASE 
                        WHEN post_status = 'wc-agrupar-pedidos' THEN 1
                        ELSE 0
                    END AS num_agrupados,
                    1 AS childs,
                    id AS post_parent,
                    wp_posts.post_date
                FROM wp_posts
                WHERE post_type = 'shop_order'
                AND post_parent = 0
                AND id NOT IN (SELECT DISTINCT post_parent FROM wp_posts)
            )
            SELECT 
                f.*,
                pm.name
            FROM final f
            LEFT JOIN (
                SELECT 
                post_id, 
                meta_value AS name
                FROM wp_postmeta
                WHERE meta_key = '_billing_first_name'
            ) pm ON pm.post_id = f.id
            WHERE f.id =  {orderId};


        """
        # Ejecutar la primera consulta
        cursor.execute(check_statusses)

        # Obtener los resultados de la primera consulta
        resultados_check_statusses = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_check_statusses = pd.DataFrame(resultados_check_statusses)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
    if len(wp_check_statusses) > 0:
        wp_check_statusses = wp_check_statusses[['id','num_agrupados','childs', 'post_parent','post_date','name']]
        # Nueva lista de nombres de columnas
        wp_check_statusses.columns = ['id','num_agrupados','childs', 'post_parent','post_date','name']
        wp_check_statusses_general_dict = wp_check_statusses.to_dict(orient='list')
        return wp_check_statusses_general_dict


def insert_producto_problema(producto, db='repl'):
    db = 'prod'
    config = config_db(db)
    start_time = time.time()

    # Determinar la incidencia y su detalle
    incidencia = "Sin incidencia"
    piezas_faltantes = int(producto['piezas_faltantes']) if 'piezas_faltantes' in producto else 0
    defectuoso = producto['defectuoso'] if 'defectuoso' in producto and producto['defectuoso'] else None

    if producto['cantidad_nueva'] < producto['cantidad_sistema']:
        incidencia = "No llegó el producto (paquetes)"
    if piezas_faltantes > 0:
        incidencia = "Llegó producto (paquetes) con piezas faltantes"
    if producto['razon'] == "Defectuoso":
        incidencia = "Llegó defectuoso"

    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            insert_query = """
            INSERT INTO rintin_auditoria_productos_incidencias 
            (order_id, product_id, nombre_producto, sku, cantidad_sistema, cantidad_nueva, piezas_faltantes, defectuoso, incidencia, estado, seller_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Datos a insertar
            event_data = (
                int(producto['order_id']), 
                int(producto['producto_id']), 
                producto['nombre_producto'], 
                producto['sku'], 
                int(producto['cantidad_sistema']),
                int(producto['cantidad_nueva']), 
                piezas_faltantes, 
                defectuoso, 
                incidencia, 
                "pending",
                producto.get('seller_id', None)  # Puede ser NULL si no hay seller_id
            )

            # Ejecutar la consulta
            cursor.execute(insert_query, event_data)
            connection.commit()
            print("Evento insertado correctamente")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

def guardar_productos_extra(productos, idPedido, sellerId, db='repl'):
    """
    Guarda los productos extra en la base de datos.

    :param db_config: Configuración de conexión a la base de datos.
    :param productos_extra: Lista de productos extra a guardar.
    """
    db = 'prod'
    config = config_db(db)
    start_time = time.time()
    
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Consulta SQL para insertar productos extra
            insert_query = """
            INSERT INTO rintin_auditorio_productos_extra (order_id, codigo_producto, seller_id, unidad, cantidad) 
            VALUES (%s, %s, %s, %s, %s)
            """

            # Insertar cada producto extra en la base de datos
            for producto in productos:
                event_data = (
                    idPedido,
                    producto["codigo_extra_producto"],
                    sellerId,
                    producto["unidad_extra_producto"],
                    producto["cantidad_extra_producto"]
                )
                cursor.execute(insert_query, event_data)

            # Confirmar cambios en la base de datos
            connection.commit()
            print(f"✅ {len(productos)} productos extra guardados correctamente en la base de datos.")
    
    except mysql.connector.Error as err:
        print(f"❌ Error al guardar productos extra: {err}")
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Conexión cerrada con la base de datos.")

def get_order_issues(order_id, db='repl') -> dict:
    config = config_db(db)
    start_time = time.time()

    try:
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor(dictionary=True)

        # Query con los campos correctos
        order_issues_sql = """
            SELECT 
                id,
                order_id,
                product_id,
                nombre_producto AS order_item_name,
                sku,
                cantidad_sistema,
                cantidad_nueva,
                piezas_faltantes,
                defectuoso,
                incidencia,
                estado,
                seller_id,
                created_at,
                updated_at
            FROM wordpress.rintin_auditoria_productos_incidencias
            WHERE order_id = %s;
        """

        # Ejecutar la consulta con parámetro seguro
        cursor.execute(order_issues_sql, (order_id,))
        resultados_order_issues_sql = cursor.fetchall()

        # Convertir los resultados en un DataFrame de Pandas
        wp_pickeo = pd.DataFrame(resultados_order_issues_sql)

    except Exception as e:
        print(f"Error en get_order_issues: {e}")
        return {}

    finally:
        cursor.close()
        conexion.close()

    end_time = time.time()
    duration = end_time - start_time

    # Validación: Si hay datos, ajustamos nombres de columnas
    if not wp_pickeo.empty:
        wp_pickeo.columns = ['ID', 'order_id', 'product_id', 'Producto', 'SKU', 'Cantidad Sistema', 
                             'Cantidad Nueva', 'Piezas Faltantes', 'Defectuoso', 'Incidencia', 
                             'Estado', 'Seller ID', 'Creado', 'Actualizado']
        return wp_pickeo.to_dict(orient='list')  # 🔹 Retorna diccionario con listas

    return {}


def get_wa_group_id(seller_id, db='repl'):
	config = config_db(db)
	try:
		connection = mysql.connector.connect(**config)
		cursor = connection.cursor(dictionary=True)
		sql = f"select meta_value  from wp_usermeta wu where user_id = '{seller_id}' and meta_key = 'wa_group_id';"
		cursor.execute(sql)
		results = cursor.fetchone()
		cursor.close()
	finally:

		connection.close()
		if results is None:
			return 0
		else:
			return results['meta_value']