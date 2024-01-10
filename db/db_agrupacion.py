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

def get_seller_centro_padre(db='repl') -> dict:
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
                    id,
                    post_parent,
                    post_status
                from wp_posts 
                where post_type = 'shop_order' and post_status NOT IN ('wc-pendientes_ograma','wc-failed', 'wc-caducado','wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial')
            ),
            order_seller as (
                select
                    post_id,
                    meta_value as dokan_vendor_id
                from wp_postmeta
                where meta_key = '_dokan_vendor_id'
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
                group by user_id
                having zone = 'centro'
            ),
            final_helper as(
            select 
                post_parent,
                count(case when post_status not in ('wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end) as ordenes_activas,
                count(case when post_status = 'wc-agrupar-pedidos' then id else null end) as pedidos_auditados
            from 
                orders
                inner join order_seller on id = post_id
                inner join sellers on user_id = dokan_vendor_id
            where post_parent != 0
            group by post_parent
            having pedidos_auditados > 0
            ),
            final_helper2 as(
                select
                    id,
                    case when post_status not in ('wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then 1 else 0 end as ordenes_activas,
                    case when post_status = 'wc-agrupar-pedidos' then 1 else 0 end as pedidos_auditados
                from orders 
                inner join order_seller on id = post_id
                inner join sellers on user_id = dokan_vendor_id
                where post_parent = 0 and id not in (select distinct post_parent from orders)
                having pedidos_auditados > 0
            )
            select post_parent as order_id, 
            ordenes_activas, 
            pedidos_auditados, 
            ordenes_activas - pedidos_auditados as en_proceso,
            CASE 
			    WHEN (ordenes_activas - pedidos_auditados) = 0 THEN 'Agrupar'
			    ELSE 'Faltan Pedidos'
			END AS estado

            
            from final_helper 
            union 
            select id as order_id, ordenes_activas, pedidos_auditados, ordenes_activas - pedidos_auditados as en_proceso,
            CASE 
			    WHEN (ordenes_activas - pedidos_auditados) = 0 THEN 'Agrupar'
			    ELSE 'Faltan Pedidos'
			END AS estado
			from final_helper2 
        """

        # Ejecutar la primera consulta
        cursor.execute(wp_seller_sql)

        # Obtener los resultados de la primera consulta
        resultados_wp_seller_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_seller = pd.DataFrame(resultados_wp_seller_sql)
        print("wp_seller")
        print(wp_seller)

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
        wp_seller_general_dict = wp_seller.to_dict(orient='list')
        return wp_seller_general_dict

def get_order_detalle_agrupacion(id,db='repl') -> dict:
    config = config_db(db)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_pickeo_sql = f"""
           with orders as (
                    select
                        id, post_status
                    from
                        wp_posts
                    where
                        post_parent={id} AND post_status NOT IN ('wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'contracargo-ganad', 'contra-cargo', 'refunded', 'reembolso-parcial')
                        
                        
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
                ),users as (
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
                    ) AS `dokan_store_name`
                from wp_usermeta
                inner join ordermeta on ordermeta.dokan_vendor_id = user_id
                group by user_id
                 having zone = 'centro'
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
                        ) AS `line_qty`
                        
                    from
                        `wp_woocommerce_order_itemmeta`
                        inner join order_items on order_items.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
                    group by
                        `wp_woocommerce_order_itemmeta`.`order_item_id`
                )
                select
                    order_items.order_id,
                    users.dokan_store_name as seller_name,
                    orders.post_status as estado,
                    line_qty as num_paquetes
                from 
                    order_items
                    left join order_item_meta on order_item_meta.order_item_id = order_items.order_item_id
                    left join ordermeta on ordermeta.order_id=order_items.order_id
                    left join users on users.user_id = ordermeta.dokan_vendor_id
                    left join orders on orders.id=  ordermeta.order_id
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
        wp_pickeo = wp_pickeo[['order_id','seller_name','estado','num_paquetes']]
        wp_pickeo_general_dict = wp_pickeo.to_dict(orient='list')
        return wp_pickeo_general_dict
    else:
        return {}


