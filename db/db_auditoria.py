# db/script_db.py
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

def get_seller_centro(db='repl') -> dict:
    # Registrar el tiempo de inicio
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)

        wp_seller_sql = """
        with orders as (
                select
                    id
                from
                    wp_posts
                where
                    post_status = 'wc-auditoria-2'
                    and id not in (select distinct post_parent from wp_posts)
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
            sellers as (
                select
                    user_id,
                    max(
                        case
                            when `meta_key` = '_zone' then `meta_value`
                            else NULL
                        end
                    ) AS `zone`,
                    max(
                        case
                            when `meta_key` = 'dokan_store_name' then `meta_value`
                            else NULL
                        end
                    ) AS `seller_name`
                from
                    wp_usermeta
                    inner join ordermeta on dokan_vendor_id = user_id
                group by user_id
                having zone = 'centro'
            )
            select
                ordermeta.order_id,
                seller_name
            from ordermeta
                inner join sellers on sellers.user_id = dokan_vendor_id
        """
        
        # Ejecutar la primera consulta
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
        #wp_seller['estado']='wc-recolectar-2'
        #wp_seller=wp_seller[['order_id','seller_id','seller_name', 'num_paquetes','estado']]
        #wp_seller.columns = ['id','Seller', 'num_paquetes','estado','seller_id']
        wp_seller.columns = ['ID', 'Seller']
        wp_seller_general_dict = wp_seller.to_dict(orient='list')
        return wp_seller

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
                    #having dokan_vendor_id in ('3587', '998', '1352', '2636', '3759', '2751', '2166', '1663', '2705', '7180', '7201', '7202', '3465', '5894')
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
                )
                select
                    order_items.order_id,
                    product_meta.product_id,
                    order_items.dokan_vendor_id as seller_id,
                    order_items.order_item_name,
                    line_qty,
                    sku,
                    units_per_pack,
                    replace(wp_posts.guid, 'http://dev.', 'https://') as img_url
                from 
                    order_items
                    left join order_item_meta on order_item_meta.order_item_id = order_items.order_item_id
                    left join product_meta on order_item_meta.product_id = product_meta.product_id
                    left join wp_posts on wp_posts.id = product_meta.image_id  
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
        wp_pickeo = wp_pickeo[['order_id','order_item_name','line_qty','sku','img_url','units_per_pack','product_id','seller_id']]
        # Nueva lista de nombres de columnas
        wp_pickeo.columns = ['order_id', 'Producto','Cantidad','SKU','Imagen','units_per_pack','product_id','seller_id']
        #print(f"El script se ejecutó en {minutes} minutos y {seconds} segundos.")
        wp_pickeo_general_dict = wp_pickeo.to_dict(orient='list')
        return wp_pickeo
    else:
        return {}


