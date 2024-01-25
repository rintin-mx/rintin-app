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

def get_seller_recollection(db='repl') -> dict:
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_seller_recolection_sql =  """
               with orders as (
                    select
                        id
                    from
                        wp_posts
                    where
                        post_status = 'wc-recolectar-2'
                        
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
                    where meta_value not in ('centro_cdmx', 'aj_cdmx')
                    group by user_id
                    having zone = 'centro'
                ),
                order_items as(
                    select order_item_id, wp_woocommerce_order_items.order_id, order_item_name
                    from wp_woocommerce_order_items
                    inner join wp_posts on wp_posts.id = order_id
                    where order_item_type = 'line_item' and post_status = 'wc-recolectar-2'
                ),
                product_order_meta_values as (
                    select
                        `wp_woocommerce_order_itemmeta`.`order_item_id` AS `order_item_id`,
                        max(
                            case
                                when `wp_woocommerce_order_itemmeta`.`meta_key` = '_qty' then `wp_woocommerce_order_itemmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `order_quantity`
                    from
                        `wp_woocommerce_order_itemmeta`
                        inner join order_items on order_items.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
                    group by
                        `wp_woocommerce_order_itemmeta`.`order_item_id`
                )
                select
                    seller_name,
                    count(distinct ordermeta.order_id) as num_pedidos,
                    sum(order_quantity) as num_paquetes
                from ordermeta
                    inner join sellers on sellers.user_id = dokan_vendor_id
                    inner join order_items on order_items.order_id = ordermeta.order_id
                    inner join product_order_meta_values on product_order_meta_values.order_item_id = order_items.order_item_id
                group by seller_name
        """
        # Ejecutar la primera consulta
        cursor.execute(wp_seller_recolection_sql)

        # Obtener los resultados de la primera consulta
        resultados_wp_seller_recolection_sql= cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        seller_recolection = pd.DataFrame(resultados_wp_seller_recolection_sql)
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
    print(f"El script se ejecutó en {minutes} minutos y {seconds} segundos.")
    seller_recolection.columns = ['Seller', '#Pedidos','#Paquetes']
    total_pedidos = seller_recolection['#Pedidos'].sum()
    total_paquetes = seller_recolection['#Paquetes'].sum()
    total_registros = len(seller_recolection)
    seller_recolection_dict = seller_recolection.to_dict(orient='list')
    return int(total_pedidos),int(total_paquetes),int(total_registros),seller_recolection_dict

def get_data_seller_by_name(name,db='repl') -> dict:
    # Registrar el tiempo de inicio
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_seller_by_name_recolection_sql_temp ="""
           with orders as (
                    select
                        id
                    from
                        wp_posts
                    where
                        post_status = 'wc-recolectar-2'
                        
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
                    #having dokan_vendor_id not in ('3587', '998', '1352', '2636', '3759', '2751', '2166', '1663', '7180', '7201', '7202', '6927')
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
                    where meta_value not in ('centro_cdmx', 'aj_cdmx')
                    group by user_id
                    having zone = 'centro'
                ),
                order_items as(
                    select order_item_id, wp_woocommerce_order_items.order_id, order_item_name
                    from wp_woocommerce_order_items
                    inner join wp_posts on wp_posts.id = order_id
                    where order_item_type = 'line_item' and post_status = 'wc-recolectar-2'
                ),
                product_order_meta_values as (
                    select
                        `wp_woocommerce_order_itemmeta`.`order_item_id` AS `order_item_id`,
                        max(
                            case
                                when `wp_woocommerce_order_itemmeta`.`meta_key` = '_qty' then `wp_woocommerce_order_itemmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `order_quantity`
                    from
                        `wp_woocommerce_order_itemmeta`
                        inner join order_items on order_items.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
                    group by
                        `wp_woocommerce_order_itemmeta`.`order_item_id`
                )
                select
                    seller_name,
                    ordermeta.order_id as order_id,
                    sum(order_quantity) as num_paquetes
                from ordermeta
                    inner join sellers on sellers.user_id = dokan_vendor_id
                    inner join order_items on order_items.order_id = ordermeta.order_id
                    inner join product_order_meta_values on product_order_meta_values.order_item_id = order_items.order_item_id
                WHERE seller_name = %s
                group by seller_name, ordermeta.order_id

        """
        wp_seller_by_name_recolection_sql="""
        with orders as (
                    select
                        id
                    from
                        wp_posts
                    where
                        post_status = 'wc-recolectar-2'
                        
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
                          
                    #having dokan_vendor_id not in ('3587', '998', '1352', '2636', '3759', '2751', '2166', '1663', '7180', '7201', '7202', '6927')
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
                    where meta_value not in ('centro_cdmx', 'aj_cdmx')
                    group by user_id
                    having zone = 'centro'
                ),
                order_items as(
                    select order_item_id, wp_woocommerce_order_items.order_id, order_item_name
                    from wp_woocommerce_order_items
                    inner join wp_posts on wp_posts.id = order_id
                    where order_item_type = 'line_item' and post_status = 'wc-recolectar-2'
                ),
                product_order_meta_values as (
                    select
                        `wp_woocommerce_order_itemmeta`.`order_item_id` AS `order_item_id`,
                        max(
                            case
                                when `wp_woocommerce_order_itemmeta`.`meta_key` = '_qty' then `wp_woocommerce_order_itemmeta`.`meta_value`
                                else NULL
                            end
                        ) AS `order_quantity`
                    from
                        `wp_woocommerce_order_itemmeta`
                        inner join order_items on order_items.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
                    
                    group by
                        `wp_woocommerce_order_itemmeta`.`order_item_id`
                )
                select
                    seller_name,
                    ordermeta.order_id as order_id,
                    count(distinct ordermeta.order_id) as num_pedidos,
                    sum(order_quantity) as num_paquetes
                from ordermeta
                    inner join sellers on sellers.user_id = dokan_vendor_id
                    inner join order_items on order_items.order_id = ordermeta.order_id
                    inner join product_order_meta_values on product_order_meta_values.order_item_id = order_items.order_item_id
                WHERE seller_name = %s
                group by seller_name, ordermeta.order_id
        """
        # Ejecutar la primera consulta
        cursor.execute(wp_seller_by_name_recolection_sql,(name,))

        # Obtener los resultados de la primera consulta
        resultados_wp_seller_by_name_recolection_sql= cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_seller_by_name_recolection = pd.DataFrame(resultados_wp_seller_by_name_recolection_sql)

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
    wp_seller_by_name_recolection['recolectado'] = False
    print(f"El script se ejecutó en {minutes} minutos y {seconds} segundos.")

    wp_seller_by_name_recolection_dict = wp_seller_by_name_recolection.to_dict(orient='list')
    return wp_seller_by_name_recolection_dict



