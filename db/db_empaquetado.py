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
	count(case when post_status not in ('wc-generar_guia','wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end) as ordenes_activas,
	count(case when post_status = 'wc-empaquetar' then id else null end) as pedidos_agrupados,
    group_concat(case when post_status = 'wc-empaquetar' then id else null end separator ', ') as hijos_agrupados,
    group_concat(case when post_status not in ('wc-generar_guia','wc-empaquetar', 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end separator ', ') as hijos_en_proceso
from 
	orders
	inner join order_seller on id = post_id
	inner join sellers on user_id = dokan_vendor_id
where post_parent != 0
group by post_parent
having pedidos_agrupados > 0
),
final_helper2 as(
	select
		id,
		case when post_status not in ('wc-generar_guia','wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then 1 else 0 end as ordenes_activas,
		case when post_status = 'wc-empaquetar' then 1 else 0 end as pedidos_agrupados,
        'N/A' as hijos_agrupados,
        'N/A' as hijos_en_proceso
	from orders 
	inner join order_seller on id = post_id
	inner join sellers on user_id = dokan_vendor_id
	where post_parent = 0 and id not in (select distinct post_parent from orders)
	having pedidos_agrupados > 0
)
select post_parent as order_id, 
ordenes_activas, 
pedidos_agrupados, 
ordenes_activas - pedidos_agrupados as en_proceso,
hijos_agrupados,
hijos_en_proceso,
CASE 
	WHEN (ordenes_activas - pedidos_agrupados) = 0 THEN 'Empaquetar'
	ELSE 'Faltan Pedidos'
END AS estado


from final_helper 
union 
select id as order_id, ordenes_activas, pedidos_agrupados, ordenes_activas - pedidos_agrupados as en_proceso, hijos_agrupados, hijos_en_proceso,
CASE 
	WHEN (ordenes_activas - pedidos_agrupados) = 0 THEN 'Empaquetar'
	ELSE 'Faltan Pedidos'
END AS estado
from final_helper2 
order by
	order_id ASC
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

def get_order_detalle_empaquetado(id,db='repl') -> dict:
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
        id,
        post_status,
        post_parent
    FROM wp_posts
    WHERE post_status NOT IN (
        'wc-generar_guia',
        'wc-cancelled',
        'wc-devuelto',
        'wc-devolucion_proces',
        'wc-delivered',
        'contracargo-ganad',
        'contra-cargo',
        'refunded',
        'reembolso-parcial'
    )

    UNION

    SELECT 
        id,
        post_status,
        id AS post_parent
    FROM wp_posts
    WHERE
        post_status NOT IN (
            'wc-generar_guia',
            'wc-cancelled',
            'wc-devuelto',
            'wc-devolucion_proces',
            'wc-delivered',
            'contracargo-ganad',
            'contra-cargo',
            'refunded',
            'reembolso-parcial'
        )
        AND id NOT IN (
            SELECT DISTINCT post_parent
            FROM wp_posts
            WHERE post_type = 'shop_order'
        )
        AND post_type = 'shop_order'
),
orders AS (
    SELECT *
    FROM orders_helper
    WHERE post_parent = {id}  -- Manteniendo el mismo filtro dinámico
),
ordermeta AS (
    SELECT
        post_id AS order_id,
        MAX(
            CASE
                WHEN meta_key = '_dokan_vendor_id'
                     THEN meta_value
                ELSE NULL
            END
        ) AS dokan_vendor_id
    FROM wp_postmeta
    INNER JOIN orders ON orders.id = post_id
    GROUP BY post_id
),
/* 
   Mantienes el filtro de los vendedores 
   con zona = 'centro'
*/
users AS (
    SELECT
        user_id,
        MAX(CASE WHEN meta_key = '_zone' THEN meta_value END) AS zone,
        MAX(CASE WHEN meta_key = 'dokan_store_name' THEN meta_value END) AS dokan_store_name
    FROM wp_usermeta
    INNER JOIN ordermeta ON ordermeta.dokan_vendor_id = user_id
    GROUP BY user_id
    HAVING zone = 'centro'
),
/* 
   Aquí modificamos `order_items`: 
   1) Unimos con `wp_woocommerce_order_itemmeta` para extraer el `product_id` 
      (similares a la lógica del Query 1).
   2) Agrupamos por item_id para consolidar la info (product_id).
*/
order_items AS (
    SELECT
        woi.order_item_id,
        om.order_id,
        woi.order_item_name AS product_name,
        om.dokan_vendor_id,
        /* 
           Obtenemos el product_id usando MAX + CASE igual que en Query 1
        */
        MAX(
            CASE 
                WHEN woim.meta_key = '_product_id'
                     THEN woim.meta_value
                ELSE NULL
            END
        ) AS product_id
    FROM wp_woocommerce_order_items AS woi
    INNER JOIN wp_woocommerce_order_itemmeta AS woim
        ON woi.order_item_id = woim.order_item_id
    INNER JOIN ordermeta AS om
        ON woi.order_id = om.order_id
    WHERE woi.order_item_type = 'line_item'
    GROUP BY
        woi.order_item_id,
        om.order_id,
        woi.order_item_name,
        om.dokan_vendor_id
),
/*
   CTE para extraer la cantidad de cada item (line_qty)
   Filtramos solo los item_ids que existen en order_items
*/
order_item_meta AS (
    SELECT
        woim.order_item_id,
        MAX(
            CASE
                WHEN woim.meta_key = '_qty'
                     THEN woim.meta_value
                ELSE NULL
            END
        ) AS line_qty
    FROM wp_woocommerce_order_itemmeta AS woim
    INNER JOIN order_items oi
        ON oi.order_item_id = woim.order_item_id
    GROUP BY woim.order_item_id
),
/* 
   Igual que en Query 1, creamos un CTE para la meta de los productos, 
   de donde sacamos `_sku` y `_units_per_pack`
*/
product_meta AS (
    SELECT
        wp_postmeta.post_id AS product_id,
        MAX(
            CASE
                WHEN wp_postmeta.meta_key = '_units_per_pack'
                     THEN wp_postmeta.meta_value
                ELSE NULL
            END
        ) AS units_per_pack,
        MAX(
            CASE
                WHEN wp_postmeta.meta_key = '_sku'
                     THEN wp_postmeta.meta_value
                ELSE NULL
            END
        ) AS sku
    FROM wp_postmeta
    GROUP BY wp_postmeta.post_id
),
/*
   CTE final: unimos todo 
   (order_items, order_item_meta, product_meta, users, orders)
*/
final AS (
    SELECT
        oi.order_id,
        oi.product_name,
        pm.sku,
        pm.units_per_pack,
        CAST(oim.line_qty AS UNSIGNED) AS num_paquetes
    FROM order_items AS oi
    INNER JOIN order_item_meta AS oim
        ON oim.order_item_id = oi.order_item_id
    INNER JOIN product_meta AS pm
        ON pm.product_id = oi.product_id
    /* 
       Importante: 
       El join con `users` se mantiene para asegurar 
       que sólo vengan vendedores de zona = 'centro'
    */
    INNER JOIN users
        ON users.user_id = oi.dokan_vendor_id
    /* 
       Se puede volver a enlazar con `orders` 
       para respetar la relación con el {id} 
       (aunque muchas veces no sea crítico si 
        ya está filtrado en steps previos).
    */
    INNER JOIN orders
        ON orders.id = oi.order_id
)
/* 
   SELECT final que se asemeja al Query 1: 
   agrupar por order_id, product_name, sku, units_per_pack, 
   y sumar la cantidad (num_paquetes).
*/
SELECT 
    final.order_id,
    final.product_name,
    final.sku,
    final.units_per_pack,
    SUM(final.num_paquetes) AS num_paquetes
FROM final
GROUP BY
    final.order_id,
    final.product_name,
    final.sku,
    final.units_per_pack;

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