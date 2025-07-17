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

def get_proveedores(db='repl'):
    config = config_db(db)
    try:
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor(dictionary=True)
        sql = """
            with proveedores as (
select distinct meta_value  as proveedores
from wp_postmeta 
where meta_key = '_proveedor'
),
sellers as(
	select user_id, meta_value
    from wp_usermeta
    where meta_key = 'dokan_store_name'
)
select meta_value as proveedor from proveedores inner join sellers on user_id = proveedores
        """
    # Ejecutar la primera consulta
        cursor.execute(sql)

        # Obtener los resultados de la primera consulta
        results = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_proveedores = pd.DataFrame(results)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
        wp_proveedores.columns = ['proveedor']
        results_dict = wp_proveedores.to_dict(orient='list')
        return results_dict

def get_seller(db='repl') -> dict:
    # Registrar el tiempo de inicio
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_seller_sql ="""
        
with orders AS (
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
proveedores as (
select distinct meta_value  as proveedores
from wp_postmeta 
where meta_key = '_proveedor'
),
order_comments as(
	select
		id,
        case
			when comment_content like '%a Recolec c/problema%' or comment_content like '%a Preparando tu pedido - recp%' then 1 else 0
		end as recoleccion_c_problemas,
        case
			when comment_content like '%Validacion stock%' or comment_content like '%Preparando tu pedido - vs%' then 1 else 0
		end as validacion_stock
	from wp_comments
    inner join orders on comment_post_id = id
),
order_comments_grouped as(
	select
		id,
		sum(recoleccion_c_problemas) as recoleccion_c_problemas,
        sum(validacion_stock) as validacion_stock
	from order_comments
    group by id
),
ordermeta as (
	select
		post_id,
        post_status,
        max(
			CASE
		WHEN `meta_key` = '_dokan_vendor_id' THEN `meta_value`
		ELSE NULL
	END
        ) as seller_id
        from wp_postmeta inner join orders on id = post_id
        group by post_id, post_status
),
order_items as(
	select
		wp_woocommerce_order_items.order_item_id,
        om.meta_value as product_id,
        order_id
	from wp_woocommerce_order_items
    inner join wp_woocommerce_order_itemmeta om on om.order_item_id = wp_woocommerce_order_items.order_item_id
    inner join orders on id = order_id
    where om.meta_key = '_product_id'
),
proveedoresmeta as(
	select
    user_id,
	max(
	CASE
		WHEN `meta_key` = 'dokan_store_name' THEN `meta_value`
		ELSE NULL
	END
	) AS `dokan_store_name`
    FROM
	wp_usermeta
	INNER JOIN proveedores ON proveedores = user_id
GROUP BY
	user_id
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
	INNER JOIN orders ON orders.seller_id = user_id
GROUP BY
	user_id
),
product_meta_helper as(
	select
		order_id,
        meta_value,
        case when u1.dokan_store_name is null then 'Sin proveedor' else u1.dokan_store_name end as proveedor
	from wp_postmeta
    inner join order_items on product_id = post_id
    inner join wp_posts on id = post_id
    left join proveedoresmeta u1 on meta_value = u1.user_id
    where meta_key = '_proveedor'
),
product_meta as(
	select
		order_id,
        group_concat(distinct proveedor) as proveedor
	from product_meta_helper
    group by order_id
)
SELECT
ordermeta.post_id as order_id,
dokan_store_name as seller_name,
proveedor AS proveedor,
post_status AS estado,
recoleccion_c_problemas,
validacion_stock
FROM
ordermeta
inner join product_meta on product_meta.order_id = ordermeta.post_id
inner join order_comments_grouped on order_comments_grouped.id = ordermeta.post_id
inner join users on users.user_id = seller_id
WHERE
	users.bodega IN ('centro_cdmx', 'aj_cdmx', 'oaxaca')
ORDER BY
ordermeta.post_id ASC
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
        wp_seller=wp_seller[['order_id', 'seller_name','proveedor','estado', 'recoleccion_c_problemas', 'validacion_stock']]
        wp_seller.columns = ['order_id', 'Seller', 'proveedor','estado', 'recoleccion_c_problemas', 'validacion_stock']
        wp_seller_general_dict = wp_seller.to_dict(orient='list')
        return wp_seller_general_dict


def get_order(id,db='repl') -> dict:
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
		id
	from
		wp_posts
	where
		post_status = 'wc-recolectar-2' and id={id}
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
	select order_item_id, ordermeta.order_id, order_item_name
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
				when `wp_postmeta`.`meta_key` = '_proveedor' then `wp_postmeta`.`meta_value`
				else NULL
			end
		) AS `proveedor`,
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
		) AS `units_per_pack`,
        max(
			case
				when `meta_key` = '_stock_shr' then `meta_value`
				else NULL
			end
		) AS `stock_showroom`
	from wp_postmeta
	inner join order_item_meta on order_item_meta.product_id = post_id
	group by post_id
),
seller_names as(
	select user_id, meta_value
    from wp_usermeta
    where meta_key = 'dokan_store_name'
)
select
	order_items.order_id,
	product_meta.product_id,
	order_items.order_item_name,
    order_items.order_item_id,
	line_qty,
    product_meta.stock_showroom,
	sku,
	units_per_pack,
	CASE
		WHEN REPLACE(wp_posts.guid, 'http://dev.', 'https://') LIKE '%://rintin.mx/uploads/%' 
		THEN REPLACE(REPLACE(wp_posts.guid, 'http://dev.', 'https://'), '://rintin.mx/uploads/', '://rintin.mx/wp-content/uploads/')
		ELSE REPLACE(wp_posts.guid, 'http://dev.', 'https://')
	END as img_url,
    meta_value as proveedor
from 
	order_items
	left join order_item_meta on order_item_meta.order_item_id = order_items.order_item_id
	left join product_meta on order_item_meta.product_id = product_meta.product_id
	left join wp_posts on wp_posts.id = product_meta.image_id 
    left join seller_names on seller_names.user_id = product_meta.proveedor
order by meta_value
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
        wp_pickeo = wp_pickeo[['order_id','order_item_name','line_qty','stock_showroom','sku','img_url','units_per_pack','product_id', 'proveedor', 'order_item_id']]
        # Nueva lista de nombres de columnas
        wp_pickeo.columns = ['order_id', 'Producto','Cantidad','Stock_Showroom','SKU','Imagen','units_per_pack','product_id', 'proveedor', 'order_item_id']
        print(f"El script se ejecutó en {minutes} minutos y {seconds} segundos.")
        wp_pickeo_general_dict = wp_pickeo.to_dict(orient='list')
        return wp_pickeo_general_dict
    else:
        return {}
