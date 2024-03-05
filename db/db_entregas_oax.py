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

def get_route_orders(route_id, db='repl'):
	config = config_db(db)
	try:
		connection = mysql.connector.connect(**config)
		cursor = connection.cursor(dictionary=True)
		sql = f"""
		with orders as(
	SELECT ordenes_de_ruta.order_id, entrega_ordenes.estado 
	FROM wordpress.rutas_envios 
	inner join ordenes_de_ruta on ordenes_de_ruta.id_ruta = rutas_envios.id_ruta 
    inner join entrega_ordenes on entrega_ordenes.order_id = ordenes_de_ruta.order_id
	where ordenes_de_ruta.estado = 'pending' and rutas_envios.id_ruta = {route_id}
),
ordermeta as (
	select
		post_id as order_id,
		orders.estado,
		max(
			case
				when meta_key = '_shipping_postcode' then meta_value
				else NULL
			end
		) AS postcode,
        max(
			case
				when meta_key = '_payment_method' then meta_value
				else NULL
			end
		) AS metodo_pago,
		max(
			case
				when meta_key = '_shipping_state' then meta_value
				else NULL
			end
		) AS state,
		max(
			case
				when meta_key = '_shipping_address_index' then meta_value
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
		) as billing_phone1,
		max(
			case
				when meta_key = '_order_total' then meta_value
				else NULL
			end
		) as order_total
		
	from wp_postmeta inner join orders on orders.order_id = wp_postmeta.post_id
	group by post_id, estado
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
		zona_entrega,
		order_items.estado,
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
		line_qty,
		order_total,
        metodo_pago
	from order_items 
	inner join cps on cps.codigo_postal = order_items.postcode
	left join order_item_meta on order_items.order_item_id = order_item_meta.order_item_id
)
select
	order_id,
	name,
	zona_entrega,
	number_unified,
	address,
	sum(line_qty) as num_paquetes,
	order_total,
	estado,
    metodo_pago
from final
group by 
	order_id,
	name,
	zona_entrega,
	number_unified,
	address,
	order_total,
	estado,
    metodo_pago
		"""
		cursor.execute(sql)
		results = cursor.fetchall()
		orders = pd.DataFrame(results)
	finally:
		cursor.close()
		connection.close()
		if len(orders) > 0:
			orders.columns = ['order_id', 'name', 'zona_entrega', 'number_unified', 'address', 'num_paquetes', 'order_total', 'estado', 'metodo_pago']
			orders_dict = orders.to_dict(orient='list')
			return orders_dict
		return None

def has_active_route(user_id, db='repl'):
	config = config_db(db)
	try:
		connection = mysql.connector.connect(**config)
		cursor = connection.cursor(dictionary=True)
		sql = f"SELECT * FROM wordpress.rutas_envios where responsable = '{user_id}' and estado = 'En ruta';"
		print(sql)
		cursor.execute(sql)
		results = cursor.fetchone()
		print('results')
		print(results)
		cursor.close()
	finally:

		connection.close()
		if results is None:
			return 0
		else:
			return results['id_ruta']



def insert_route(responsable, order_list):
	db = 'prod'
	config = config_db(db)
	current_date = time.strftime('%Y-%m-%d %H:%M:%S')
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor = connection.cursor(dictionary=True)
			sql = "INSERT INTO rutas_envios (responsable, estado, fecha_creacion, fecha_edicion) VALUES (%s, 'En ruta', %s, %s)"
			cursor.execute(sql, (responsable, current_date, current_date))
			inserted_id = cursor.lastrowid
			print('inserted_id')
			print(inserted_id)
			for order in order_list:
				sql = f"INSERT INTO ordenes_de_ruta (id_ruta, order_id, estado, fecha_modificacion) VALUES ({inserted_id}, {order['order_id']}, 'pending', '{current_date}')"
				print(sql)
				cursor.execute(sql)
				sql = f"INSERT IGNORE INTO entrega_ordenes (order_id, total_a_recibir, total_recibido, estado) VALUES ({order['order_id']}, {order['total']}, 0, 'Pendiente entrega')"
				print(sql)
				cursor.execute(sql)
			connection.commit()
			cursor.close()
			connection.close()
			return True
	except Exception as e:
		connection.commit()
		cursor.close()
		connection.close()
		print('Error al realizar la inserción:', e)
		return False

def insert_product_problem(product):
	db = 'prod'
	config = config_db(db)
	current_date = time.strftime('%Y-%m-%d %H:%M:%S')
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor = connection.cursor(dictionary=True)
			sql = "INSERT INTO inconvenientes_unitarios_entregas (order_item_id, cantidad_no_entrega, razon_no_entrega, fecha) VALUES (%s, %s, %s, %s)"
			cursor.execute(sql, (product['order_item_id'], product['cantidad_entregada'], product['razon_no_entrega'], current_date))
			connection.commit()
			cursor.close()
			connection.close()
			return True
		return False
	except Exception as e:
		print('Error al realizar la inserción:', e)
		return False

def insert_item_problem(product):
	db = 'prod'
	config = config_db(db)
	current_date = time.strftime('%Y-%m-%d %H:%M:%S')
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor = connection.cursor(dictionary=True)
			sql = "INSERT INTO inconvenientes_entregas (id_ruta, order_item_id, cantidad_entregada, razon_no_entrega, fecha) VALUES (%s, %s, %s, %s)"
			cursor.execute(sql, (product['order_item_id'], product['cantidad_entregada'], product['razon_no_entrega'], current_date))
			connection.commit()
			cursor.close()
			connection.close()
			return True
		return False
	except Exception as e:
		print('Error al realizar la inserción:', e)
		return False

def update_route_order_status(route_id, order_id, status, reason, img_url):
	db = 'prod'
	config = config_db(db)
	current_date = time.strftime('%Y-%m-%d %H:%M:%S')
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor =  connection.cursor(dictionary=True)
			status_for_route_order = 'success'
			sql = f"UPDATE entrega_ordenes SET estado = '{status}' WHERE order_id = {order_id}"
			cursor.execute(sql)
			sql = f"UPDATE entrega_ordenes SET img_url = '{img_url}' WHERE order_id = {order_id}"
			cursor.execute(sql)
			if status != 'Entregado':
				status_for_route_order= 'failed'
				sql = f"UPDATE entrega_ordenes SET razon_no_entrega = '{reason}' WHERE order_id = {order_id}"
				cursor.execute(sql)
				sql = f"UPDATE wp_postmeta SET meta_value = '{reason}' WHERE post_id = {order_id} and meta_key = '_razon_no_entrega'"
				cursor.execute(sql)
			sql = f"UPDATE ordenes_de_ruta SET estado = '{status_for_route_order}' WHERE order_id = {order_id} and id_ruta = {route_id}"
			cursor.execute(sql)
			sql = f"UPDATE ordenes_de_ruta SET fecha_modificacion = '{current_date}' WHERE order_id = {order_id} and id_ruta = {route_id}"
			cursor.execute(sql)
			connection.commit()
			cursor.close()
			connection.close()
			return True
		return False
	except Exception as e:
		print('Error al actualizar la data:', e)
		return False

def update_route_status(route_id, status):
	db = 'prod'
	config = config_db(db)
	current_date = time.strftime('%Y-%m-%d %H:%M:%S')
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor =  connection.cursor(dictionary=True)
			sql = f"UPDATE rutas_envios SET estado = '{status}' WHERE id_ruta = {route_id}"
			cursor.execute(sql)
			sql = f"UPDATE rutas_envios SET fecha_edicion = '{current_date}' WHERE id_ruta = {route_id}" 
			cursor.execute(sql)
			connection.commit()
			cursor.close()
			connection.close()
			return True
		return False
	except Exception as e:
		print('Error al actualizar la data:', e)
		return False

def update_recieved_money(order_id, money_amount):
	db = 'prod'
	config = config_db(db)
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor =  connection.cursor(dictionary=True)
			sql = f"UPDATE entrega_ordenes SET total_recibido = '{money_amount}' WHERE order_id = {order_id}"
			cursor.execute(sql)
			connection.commit()
			cursor.close()
			connection.close()
			return True
		return False
	except Exception as e:
		print('Error al actualizar la data:', e)
		return False

def get_orders(db='repl') -> dict:
	config = config_db(db)
	try:
		conexion = mysql.connector.connect(**config)
		# Crear un cursor para ejecutar consultas
		cursor = conexion.cursor(dictionary=True)
		wp_ordenes_query =f"""
with orders_in_progress as (
	select
		distinct order_id
	from rutas_envios inner join ordenes_de_ruta on rutas_envios.id_ruta = ordenes_de_ruta.id_ruta
	where rutas_envios.estado = 'En ruta'
),
orders as (
	select
		wp_posts.id,
		case when post_parent = 0 then wp_posts.id else post_parent end as post_parent,
		post_status
	from wp_posts 
	where post_type = 'shop_order' and post_status NOT IN ('wc-pendientes_ograma','wc-failed', 'wc-caducado','wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial')
	and wp_posts.id not in (select distinct post_parent from wp_posts)
	and wp_posts.id not in (select order_id from orders_in_progress)
),
grouped_orders as(
select 
	post_parent,
	count(case when post_status not in ( 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end) as ordenes_activas,
	count(case when post_status = 'wc-recepcion-2' then id else null end) as hijos_recepcion
from 
	orders
group by post_parent
having hijos_recepcion = ordenes_activas
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
				when meta_key = '_shipping_address_index' then meta_value
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
		) as billing_phone1,
		max(
			case
				when meta_key = '_order_total' then meta_value
				else NULL
			end
		) as order_total
		
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
		order_items.order_id,
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
		line_qty,
		order_total
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
	sum(line_qty) as num_paquetes,
	order_total
from final
group by 
	order_id,
	name,
	ordenes_activas,
	hijos_recepcion,
	zona_entrega,
	number_unified,
	address,
	order_total


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
			wp_ordenes.columns = ['order_id', 'name', 'ordenes_activas' , 'hijos_recepcion', 'zona_entrega', 'number_unified', 'address', 'num_paquetes', 'order_total']
			wp_order_general_dict = wp_ordenes.to_dict(orient='list')
			return wp_order_general_dict
		return None


def get_order_items(order_id, db='repl') -> dict:
	config = config_db(db)
	try:
		conexion = mysql.connector.connect(**config)
		# Crear un cursor para ejecutar consultas
		cursor = conexion.cursor(dictionary=True)
		sql =f"""

with orders as (
	select
		id as order_id,
        case when post_parent = 0 then id else post_parent end as post_parent
	from
		wp_posts
	where id not in (select distinct post_parent from wp_posts where post_type = 'shop_order')
	having
		post_parent = {order_id}
		
),
order_items as(
	select order_item_id, orders.order_id, order_item_name, order_item_type
	from wp_woocommerce_order_items
	inner join orders on wp_woocommerce_order_items.order_id = orders.order_id
    where order_item_type = 'line_item'
    union 
    select order_item_id, order_id, order_item_name, order_item_type
	from wp_woocommerce_order_items
    where (order_item_type = 'shipping' or order_item_type = 'fee') and order_id = {order_id}
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
				when `wp_woocommerce_order_itemmeta`.`meta_key` = 'cost' then `wp_woocommerce_order_itemmeta`.`meta_value`
				else NULL
			end
		) AS `cost`,
		max(
			case
				when `wp_woocommerce_order_itemmeta`.`meta_key` = '_product_id' then `wp_woocommerce_order_itemmeta`.`meta_value`
				else NULL
			end
		) AS `product_id`,
        max(
			case
				when `wp_woocommerce_order_itemmeta`.`meta_key` = '_line_total' then `wp_woocommerce_order_itemmeta`.`meta_value`
				else NULL
			end
		) AS `line_total`
		
		
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
	order_items.order_item_id,
	order_items.order_item_name,
	line_qty,
	sku,
	replace(wp_posts.guid, 'http://dev.', 'https://') as img_url,
    order_items.order_id,
    case 
		when order_item_type = 'line_item' then line_total / line_qty
        when order_item_type = 'shipping' then cost 
        when order_item_type = 'fee' then line_total
	end as line_total,
    order_item_type
from 
	order_items
	left join order_item_meta on order_item_meta.order_item_id = order_items.order_item_id
	left join product_meta on order_item_meta.product_id = product_meta.product_id
	left join wp_posts on wp_posts.id = product_meta.image_id

		"""
		cursor.execute(sql)

		# Obtener los resultados de la primera consulta
		results = cursor.fetchall()

		# Convertir los resultados a un DataFrame de pandas
		order_items = pd.DataFrame(results)
	finally:
		# Cerrar el cursor y la conexión
		cursor.close()
		conexion.close()

		# Nueva lista de nombres de columnas
		#wp_seller=wp_seller[['user_id' 'dokan_store_name']]
		if len(order_items) > 0:
			order_items.columns = ['order_item_id', 'order_item_name', 'line_qty' , 'sku', 'img_url', 'order_id', 'line_total', 'order_item_type']
			wp_order_general_dict = order_items.to_dict(orient='list')
			return wp_order_general_dict
		return None