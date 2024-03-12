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
                    post_status in ('wc-prepara_pedido', 'wc-recolectar-2', 'wc-stock-2')
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
            with orders_grouped_by_parent as (
	select 
		post_parent,
        sum(
			case
				when post_status = 'wc-agrupar-pedidos' then 1 
                else 0
			end
        ) as num_agrupados,
        count(
            case
                when post_status not in ('wc-pendientes_ograma','wc-failed', 'wc-caducado','wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id
                else null
            end
        ) as childs
	from wp_posts 
    where post_parent != 0 and post_type = 'shop_order'
    group by post_parent, post_type
),
final as(
select 
	id, num_agrupados, childs, wp_posts.post_parent
from wp_posts 
inner join orders_grouped_by_parent on wp_posts.post_parent = orders_grouped_by_parent.post_parent
union
	select
		id,
        case 
			when post_status = 'wc-agrupar-pedidos' then 1
            else 0
		end as num_agrupados,
        1 as childs,
        id as post_parent
	from wp_posts
    where 
		post_type = 'shop_order'
        and post_parent = 0
        and id not in (select distinct post_parent from wp_posts)
)
select * from final where id = {orderId}

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
        wp_check_statusses = wp_check_statusses[['id','num_agrupados','childs', 'post_parent']]
        # Nueva lista de nombres de columnas
        wp_check_statusses.columns = ['id','num_agrupados','childs', 'post_parent']
        wp_check_statusses_general_dict = wp_check_statusses.to_dict(orient='list')
        return wp_check_statusses_general_dict
    
def get_seller_en_bodega(seller_id, db='Repl'):

    # Get sellers that are in a bodega

    # Parameters:
    # None

    # Returns:
    # Dataframe: A Dataframe containing the query results
    # A list of Seller_id that are in a bodega

    # Registrar el tiempo de inicio
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        sellers_in_bodega=f"""
        select
            user_id,
            max(
                case
                    when `meta_key` = 'wp_capabilities' then `meta_value`
                    else NULL
                end
            ) AS `wp_capabilities`,
            max(
                case
                    when `meta_key` = 'bodega' then `meta_value`
                    else NULL
                end
            ) AS `bodega`
            from wp_usermeta 
            group by user_id
            having wp_capabilities like '%seller%' and user_id = {seller_id}
        """
        # Ejecutar la primera consulta
        cursor.execute(sellers_in_bodega)

        # Obtener los resultados de la primera consulta
        resultados_sellers_in_bodega= cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        sellers_in_bodega = pd.DataFrame(resultados_sellers_in_bodega)

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
    return sellers_in_bodega