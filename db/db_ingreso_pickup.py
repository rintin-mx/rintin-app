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

def get_orders(db='repl') -> dict:
    config = config_db(db)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_pickeo_sql = f"""
           with cps as (
select
        distinct codigos_postales.codigo_postal AS codigo_postal
    from
        (
            (
                codigos_postales
                join cobertura on(
                    codigos_postales.id = cobertura.fk_id_codigo_postal
                )
            )
            join zonas_entrega on(
                cobertura.fk_id_zonas_entrega = zonas_entrega.id
            )
        )
    where
        zonas_entrega.zona_entrega like '%pickup%'
),
ordermeta_helper as(
    select
        post_id as order_id,
        max(
            case
                when `meta_key` = '_dokan_vendor_id' then `meta_value`
                else NULL
            end
        ) AS `dokan_vendor_id`,
         max(
			case
				when meta_key = '_shipping_postcode' then meta_value
				else NULL
			end
		) AS postcode
    from
        wp_postmeta
        inner join wp_posts on wp_posts.id = post_id
	where post_status = 'wc-parcel'
    group by
        post_id, post_status
	having dokan_vendor_id is not null
),
ordermeta as (
	select 
		order_id,
        dokan_vendor_id,
        meta_value as seller_name
	from ordermeta_helper
    inner join cps on postcode = codigo_postal
    inner join wp_usermeta on dokan_vendor_id = user_id and meta_key = 'dokan_store_name'
),
order_items as(
    select
        order_item_id,
        order_id
    from
        wp_woocommerce_order_items
        inner join wp_posts on wp_posts.id = order_id
    where
        order_item_type = 'line_item'
        and post_status = 'wc-parcel'
),
order_item_meta as (
    select
        `wp_woocommerce_order_itemmeta`.`order_item_id` AS `order_item_id`,
        order_id,
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
        `wp_woocommerce_order_itemmeta`.`order_item_id`, order_id
),
final as (
	select
		id as order_id,
        dokan_vendor_id,
        seller_name,
        post_status,
        case when post_parent = 0 then id else post_parent end as post_parent,
        line_qty as num_paquetes
	from wp_posts
    inner join ordermeta on ordermeta.order_id = wp_posts.id
    inner join order_item_meta on order_item_meta.order_id = wp_posts.id
)
select
    order_id,
    seller_name,
    post_status,
    post_parent,
    sum(num_paquetes) as num_paquetes
from
    final
group by
    order_id,
    seller_name,
    post_status,
    post_parent


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
        wp_pickeo = wp_pickeo[['order_id','seller_name', 'post_status', 'post_parent', 'num_paquetes']]
        wp_pickeo_general_dict = wp_pickeo.to_dict(orient='list')
        return wp_pickeo
    else:
        return {}

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
		case when post_parent = 0 then id else post_parent end as post_parent,
		post_status
	from wp_posts 
	where post_type = 'shop_order' and post_status NOT IN ('wc-pendientes_ograma','wc-failed', 'wc-caducado','wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial')
    and id not in (select distinct post_parent from wp_posts)
),
grouped_orders as(
select 
	post_parent,
	count(case when post_status not in ( 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end) as ordenes_activas,
	count(case when post_status = 'wc-parcel' then id else null end) as num_hijos_parcel,
    group_concat(case when post_status = 'wc-parcel' then id else null end separator ', ') as hijos_parcel
from 
	orders
group by post_parent
having num_hijos_parcel > 0
),
ordermeta as (
	select
		post_id as order_id,
        max(
			case
				when meta_key = '_shipping_postcode' then meta_value
				else NULL
			end
		) AS postcode
	from wp_postmeta inner join grouped_orders on grouped_orders.post_parent = wp_postmeta.post_id
    group by post_id
),
cps as (
select
        distinct codigos_postales.codigo_postal AS codigo_postal
    from
        (
            (
                codigos_postales
                join cobertura on(
                    codigos_postales.id = cobertura.fk_id_codigo_postal
                )
            )
            join zonas_entrega on(
                cobertura.fk_id_zonas_entrega = zonas_entrega.id
            )
        )
    where
        zonas_entrega.zona_entrega like '%pickup%'
)
select order_id as post_parent from ordermeta inner join cps on cps.codigo_postal = ordermeta.postcode
        """

        # Ejecutar la primera consulta
        cursor.execute(wp_seller_sql)

        # Obtener los resultados de la primera consulta
        resultados_wp_seller_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_ordenes = pd.DataFrame(resultados_wp_seller_sql)

    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
        # Registrar el tiempo de finalización
        end_time = time.time()

        # Calcular la duración
        duration = end_time - start_time

        if len(wp_ordenes) > 0:
            wp_ordenes.columns = ['post_parent']
            wp_order_general_dict = wp_ordenes.to_dict(orient='list')
            return wp_order_general_dict
        return None
