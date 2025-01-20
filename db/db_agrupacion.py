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
	count(case when post_status not in ('wc-empaquetar', 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end) as ordenes_activas,
	count(case when post_status = 'wc-agrupar-pedidos' then id else null end) as pedidos_auditados,
    group_concat(case when post_status = 'wc-agrupar-pedidos' then id else null end separator ', ') as hijos_auditados,
    group_concat(case when post_status not in ('wc-empaquetar','wc-agrupar-pedidos', 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end separator ', ') as hijos_en_proceso
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
		case when post_status not in ('wc-empaquetar','wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then 1 else 0 end as ordenes_activas,
		case when post_status = 'wc-agrupar-pedidos' then 1 else 0 end as pedidos_auditados,
        'N/A' as hijos_auditados,
        'N/A' as hijos_en_proceso
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
hijos_auditados,
hijos_en_proceso,
CASE 
	WHEN (ordenes_activas - pedidos_auditados) = 0 THEN 'Agrupar'
	ELSE 'Faltan Pedidos'
END AS estado


from final_helper 
union 
select id as order_id, ordenes_activas, pedidos_auditados, ordenes_activas - pedidos_auditados as en_proceso, hijos_auditados, hijos_en_proceso,
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
          WITH orders_helper AS (
    SELECT
        wp_posts.id, 
        wp_posts.post_status, 
        wp_posts.post_parent
    FROM
        wp_posts
    WHERE
        wp_posts.post_status NOT IN ('wc-empaquetar', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'contracargo-ganad', 'contra-cargo', 'refunded', 'reembolso-parcial')
    UNION 
    SELECT
        wp_posts.id, 
        wp_posts.post_status, 
        wp_posts.id AS post_parent
    FROM 
        wp_posts
    WHERE
        wp_posts.post_status NOT IN ('wc-empaquetar', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'contracargo-ganad', 'contra-cargo', 'refunded', 'reembolso-parcial')
        AND wp_posts.id NOT IN (SELECT DISTINCT wp_posts.post_parent FROM wp_posts WHERE wp_posts.post_type = 'shop_order')
        AND wp_posts.post_type = 'shop_order'
),
orders AS (
    SELECT * FROM orders_helper WHERE orders_helper.post_parent = {id}
),
ordermeta AS (
    SELECT
        wp_postmeta.post_id AS order_id,
        MAX(
            CASE
                WHEN wp_postmeta.meta_key = '_dokan_vendor_id' THEN wp_postmeta.meta_value
                ELSE NULL
            END
        ) AS dokan_vendor_id
    FROM
        wp_postmeta 
    INNER JOIN orders ON orders.id = wp_postmeta.post_id
    GROUP BY wp_postmeta.post_id
),
order_items AS (
    SELECT
        wp_woocommerce_order_items.order_item_id, 
        ordermeta.order_id, 
        wp_woocommerce_order_items.order_item_name AS product_name,
        MAX(CASE WHEN wp_woocommerce_order_itemmeta.meta_key = '_product_id' THEN wp_woocommerce_order_itemmeta.meta_value ELSE NULL END) AS product_id
    FROM
        wp_woocommerce_order_items
    INNER JOIN wp_woocommerce_order_itemmeta ON wp_woocommerce_order_items.order_item_id = wp_woocommerce_order_itemmeta.order_item_id
    INNER JOIN ordermeta ON wp_woocommerce_order_items.order_id = ordermeta.order_id
    WHERE
        wp_woocommerce_order_items.order_item_type = 'line_item'
    GROUP BY wp_woocommerce_order_items.order_item_id, ordermeta.order_id, wp_woocommerce_order_items.order_item_name
),
order_item_meta AS (
    SELECT
        wp_woocommerce_order_itemmeta.order_item_id,
        MAX(
            CASE
                WHEN wp_woocommerce_order_itemmeta.meta_key = '_qty' THEN wp_woocommerce_order_itemmeta.meta_value
                ELSE NULL
            END
        ) AS line_qty
    FROM
        wp_woocommerce_order_itemmeta
    GROUP BY wp_woocommerce_order_itemmeta.order_item_id
),
product_meta AS (
    SELECT
        wp_postmeta.post_id AS product_id,
        MAX(
            CASE
                WHEN wp_postmeta.meta_key = '_units_per_pack' THEN wp_postmeta.meta_value
                ELSE NULL
            END
        ) AS units_per_pack,
        MAX(
            CASE
                WHEN wp_postmeta.meta_key = '_sku' THEN wp_postmeta.meta_value
                ELSE NULL
            END
        ) AS sku
    FROM
        wp_postmeta
    GROUP BY wp_postmeta.post_id
),
final AS (
    SELECT
        order_items.order_id,
        order_items.product_name,
        product_meta.sku,
        product_meta.units_per_pack,
        CAST(order_item_meta.line_qty AS UNSIGNED) AS num_paquetes
    FROM 
        order_items
    INNER JOIN order_item_meta ON order_item_meta.order_item_id = order_items.order_item_id
    INNER JOIN product_meta ON product_meta.product_id = order_items.product_id
)
SELECT 
    final.order_id,
    final.product_name,
    final.sku,
    final.units_per_pack,
    SUM(final.num_paquetes) AS num_paquetes
FROM final
GROUP BY final.order_id, final.product_name, final.sku, final.units_per_pack;

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
        wp_pickeo = wp_pickeo[['order_id','product_name','sku','units_per_pack','num_paquetes']]
        wp_pickeo_general_dict = wp_pickeo.to_dict(orient='list')
        return wp_pickeo_general_dict
    else:
        return {}