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
               WITH orders AS (
                SELECT
                    wp_posts.id,
                    wp_dokan_orders.seller_id
                FROM
                    wp_posts
                    LEFT JOIN wp_dokan_orders ON wp_dokan_orders.order_id = wp_posts.id
                WHERE
                    post_status = 'wc-recolectar-2'
                ),
                ordermeta AS(
                SELECT
                    post_id AS order_id,
                    max(
                    CASE
                        WHEN `meta_key` = '_dokan_vendor_id' THEN `meta_value`
                        ELSE seller_id
                    END
                    ) AS `dokan_vendor_id`
                FROM
                    wp_postmeta
                    INNER JOIN orders ON orders.id = post_id
                GROUP BY
                    post_id
                ),
                sellers AS (
                SELECT
                    user_id,
                    max(
                    CASE
                        WHEN `meta_key` = '_zone' THEN `meta_value`
                        ELSE NULL
                    END
                    ) AS `zone`,
                    max(
                    CASE
                        WHEN `meta_key` = 'dokan_store_name' THEN `meta_value`
                        ELSE NULL
                    END
                    ) AS `seller_name`,
                    max(
                    CASE
                        WHEN `meta_key` = 'bodega' THEN `meta_value`
                        ELSE NULL
                    END
                    ) AS `bodega`,
                    max(
                    CASE
                        WHEN `meta_key` = 'wa_group_id' THEN `meta_value`
                        ELSE NULL
                    END
                    ) AS `wa_group_id`
                FROM
                    wp_usermeta
                    INNER JOIN ordermeta ON dokan_vendor_id = user_id
                GROUP BY
                    user_id
                HAVING
                    zone = 'centro'
                ),
                order_items as(
					select
					wp_woocommerce_order_items.order_item_id,
					wp_woocommerce_order_items.order_id,
					order_item_name,
					case when cambios_productos.order_item_id is null then 0 else 1 end as reemplazado
					from wp_woocommerce_order_items
					inner join wp_posts on wp_posts.id = order_id
					left join cambios_productos on cambios_productos.order_item_id = wp_woocommerce_order_items.order_item_id
					where order_item_type = 'line_item' and post_status = 'wc-recolectar-2'
				),
                product_order_meta_values AS (
                SELECT
                    `wp_woocommerce_order_itemmeta`.`order_item_id` AS `order_item_id`,
                    max(
                    CASE
                        WHEN `wp_woocommerce_order_itemmeta`.`meta_key` = '_qty' THEN `wp_woocommerce_order_itemmeta`.`meta_value`
                        ELSE NULL
                    END
                    ) AS `order_quantity`
                FROM
                    `wp_woocommerce_order_itemmeta`
                    INNER JOIN order_items ON order_items.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
                GROUP BY
                    `wp_woocommerce_order_itemmeta`.`order_item_id`
                )
                SELECT
                seller_name,
                count(DISTINCT ordermeta.order_id) AS num_pedidos,
                sum(order_quantity) AS num_paquetes,
                sum(reemplazado) as productos_reemplazados,
                wa_group_id
                FROM
                ordermeta
                INNER JOIN sellers ON sellers.user_id = dokan_vendor_id
                INNER JOIN order_items ON order_items.order_id = ordermeta.order_id
                INNER JOIN product_order_meta_values ON product_order_meta_values.order_item_id = order_items.order_item_id
                where bodega IS NULL
                GROUP BY
                seller_name
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
    seller_recolection.columns = ['seller', 'pedidos','paquetes', 'reemplazos', 'wa_group_id']
    total_pedidos = seller_recolection['pedidos'].sum()
    total_paquetes = seller_recolection['paquetes'].sum()
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
        wp_seller_by_name_recolection_sql="""
        with orders as (
                    select
                        wp_posts.id,
                        wp_dokan_orders.seller_id
                    from
                        wp_posts
					LEFT JOIN wp_dokan_orders ON wp_dokan_orders.order_id = wp_posts.id
                    where
                        post_status = 'wc-recolectar-2'
                        
                ),
                ordermeta as(
                    select
                        post_id as order_id,
                        max(
                            case
                                when `meta_key` = '_dokan_vendor_id' then `meta_value`
                                else seller_id
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
					select
					wp_woocommerce_order_items.order_item_id,
					wp_woocommerce_order_items.order_id,
					order_item_name,
					case when cambios_productos.order_item_id is null then 0 else 1 end as reemplazado
					from wp_woocommerce_order_items
					inner join wp_posts on wp_posts.id = order_id
					left join cambios_productos on cambios_productos.order_item_id = wp_woocommerce_order_items.order_item_id
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
                    sum(order_quantity) as num_paquetes,
                    sum(reemplazado) as productos_reemplazados
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

    wp_seller_by_name_recolection_dict = wp_seller_by_name_recolection.to_dict(orient='list')
    return wp_seller_by_name_recolection_dict

def get_substitute_prod(order_id_list, db='repl') -> dict:
    # Registrar el tiempo de inicio
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        substitute_products_from_seller=f"""
        WITH order_item as(
            select
                wp_woocommerce_order_itemmeta.order_item_id AS order_item_id,
                case
                    when wp_woocommerce_order_itemmeta.meta_key = '_product_id' then wp_woocommerce_order_itemmeta.meta_value
                    else NULL
                end AS product_id,
                nuevo_producto_sku
            from
                wp_woocommerce_order_itemmeta
            inner join cambios_productos on cambios_productos.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
        ),
        skus AS (
            select 
                product_id,
                sku
            from
                product_meta_materialized
        ),
        final AS (
        select
            order_item_id,
            sku,
            nuevo_producto_sku
        from
            order_item join skus on skus.product_id = order_item.product_id
        )
        select
            order_id,
            wp_woocommerce_order_items.order_item_id,
            sku,
            nuevo_producto_sku
        from
            final join wp_woocommerce_order_items on wp_woocommerce_order_items.order_item_id = final.order_item_id
        where
            order_id in ({order_id_list})
        """
        # Ejecutar la primera consulta
        cursor.execute(substitute_products_from_seller)

        # Obtener los resultados de la primera consulta
        resultados_substitute_products_from_seller= cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        substitute_products_from_seller = pd.DataFrame(resultados_substitute_products_from_seller)

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

    #substitute_products_from_seller = substitute_products_from_seller.to_dict(orient='list')
    return substitute_products_from_seller
