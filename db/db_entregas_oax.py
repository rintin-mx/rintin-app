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
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_ordenes_query =f"""
with orders as (
	select
		wp_posts.id,
		case when post_parent = 0 then wp_posts.id else post_parent end as post_parent,
		post_status
	from wp_posts 
	where post_type = 'shop_order' and post_status NOT IN ('wc-pendientes_ograma','wc-failed', 'wc-caducado','wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial')
    and wp_posts.id not in (select distinct post_parent from wp_posts)
),
grouped_orders as(
select 
	post_parent,
	count(case when post_status not in ( 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end) as ordenes_activas,
	count(case when post_status = 'wc-recepcion-2' then id else null end) as hijos_recepcion
from 
	orders
group by post_parent
having hijos_recepcion > 0
),
ordermeta as (
	select
		post_id as order_id,
        ordenes_activas,
        hijos_recepcion,
        max(
			case
				when meta_key = '_shipping_postcode' then meta_value
				else NULL
			end
		) AS postcode,
        max(
			case
				when meta_key = '_shipping_state' then meta_value
				else NULL
			end
		) AS state,
        max(
			case
				when meta_key = '_shipping_address_1' then meta_value
                else NULL
			end
        ) as address,
        max(
			case
				when meta_key = '_billing_first_name' then meta_value
                else NULL
			end
        ) as first_name,
        max(
			case
				when meta_key = '_billing_last_name' then meta_value
                else NULL
			end
        ) as last_name,
        max(
			case
				when meta_key = '_billing_phone' then meta_value
                else NULL
			end
        ) as billing_phone,
        max(
			case
				when meta_key = '_billing_phone1' then meta_value
                else NULL
			end
        ) as billing_phone1
	from wp_postmeta inner join grouped_orders on grouped_orders.post_parent = wp_postmeta.post_id
    group by post_id, ordenes_activas, hijos_recepcion
),
order_items as(
	select ordermeta.*, wp_woocommerce_order_items.order_item_id
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
),
cps as (
select
        distinct codigos_postales.codigo_postal AS codigo_postal, zonas_entrega.zona_entrega
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
final as(
	select 
		concat(first_name, ' ', last_name) as name,
		order_id,
		ordenes_activas,
		hijos_recepcion,
		zona_entrega,
		case
				when billing_phone is null then right(
					replace(
						replace(billing_phone, ' ', ''),
						'+',
						''
					),
					10
				)
				when billing_phone = billing_phone1 then right(
					replace(
						replace(billing_phone, ' ', ''),
						'+',
						''
					),
					10
				)
				when char_length(billing_phone) < char_length(billing_phone1) then right(
					replace(
						replace(
							billing_phone1,
							' ',
							''
						),
						'+',
						''
					),
					10
				)
				when char_length(billing_phone1) >= char_length(billing_phone) then right(
					replace(
						replace(billing_phone, ' ', ''),
						'+',
						''
					),
					10
				)
				else right(
					replace(
						replace(billing_phone, ' ', ''),
						'+',
						''
					),
					10
				)
			end AS number_unified,
		address,
        line_qty
	from order_items 
	inner join cps on cps.codigo_postal = order_items.postcode
    left join order_item_meta on order_items.order_item_id = order_item_meta.order_item_id
)
select 
	order_id,
	name,
    ordenes_activas,
    hijos_recepcion,
    zona_entrega,
    number_unified,
    address,
    sum(line_qty) as num_paquetes
from final
group by 
	order_id,
	name,
    ordenes_activas,
    hijos_recepcion,
    zona_entrega,
    number_unified,
    address
        """
        cursor.execute(wp_ordenes_query)

        # Obtener los resultados de la primera consulta
        resultados_wp_ordenes = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        wp_ordenes = pd.DataFrame(resultados_wp_ordenes)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

        # Nueva lista de nombres de columnas
        #wp_seller=wp_seller[['user_id' 'dokan_store_name']]
        if len(wp_ordenes) > 0:
            wp_ordenes.columns = ['name', 'order_id', 'ordenes_activas' , 'hijos_recepcion', 'zona_entrega', 'number_unified', 'address', 'num_paquetes']
            wp_order_general_dict = wp_ordenes.to_dict(orient='list')
            return wp_order_general_dict
        return None