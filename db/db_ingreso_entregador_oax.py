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

def get_routes(db='repl') -> dict:
	config = config_db(db)
	try:
		conexion = mysql.connector.connect(**config)
		# Crear un cursor para ejecutar consultas
		cursor = conexion.cursor(dictionary=True)
		sql =f"""
select id_ruta, responsable, fecha_creacion from rutas_envios where estado = 'Finalizado'
		"""
		cursor.execute(sql)

		# Obtener los resultados de la primera consulta
		results = cursor.fetchall()

		# Convertir los resultados a un DataFrame de pandas
		routes = pd.DataFrame(results)
	finally:
		# Cerrar el cursor y la conexión
		cursor.close()
		conexion.close()

		# Nueva lista de nombres de columnas
		#wp_seller=wp_seller[['user_id' 'dokan_store_name']]
		if len(routes) > 0:
			routes.columns = ['id_ruta', 'responsable', 'fecha_creacion']
			wp_order_general_dict = routes.to_dict(orient='list')
			return wp_order_general_dict
		return None

def get_route_orders(route_id, db='repl'):
	config = config_db(db)
	try:
		connection = mysql.connector.connect(**config)
		cursor = connection.cursor(dictionary=True)
		sql = f"""
		with orders as(
	SELECT ordenes_de_ruta.order_id, entrega_ordenes.total_recibido
	FROM wordpress.rutas_envios 
	inner join ordenes_de_ruta on ordenes_de_ruta.id_ruta = rutas_envios.id_ruta 
	inner join entrega_ordenes on entrega_ordenes.order_id = ordenes_de_ruta.order_id
	where rutas_envios.id_ruta = {route_id}
),
ordermeta as (
	select
		post_id as order_id,
		orders.total_recibido,
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
		) as last_name
		
	from wp_postmeta inner join orders on orders.order_id = wp_postmeta.post_id
	group by post_id, total_recibido
),
final as(
	select 
		concat(first_name, ' ', last_name) as name,
		order_id,
		ordermeta.total_recibido
	from ordermeta 

)
select
	order_id,
	name,
	total_recibido
from final

		"""
		cursor.execute(sql)
		results = cursor.fetchall()
		orders = pd.DataFrame(results)
	finally:
		cursor.close()
		connection.close()
		if len(orders) > 0:
			orders.columns = ['order_id', 'name', 'total_recibido']
			orders_dict = orders.to_dict(orient='list')
			return orders_dict
		return None

def update_route(route_id, order_list, estado):
	db = 'prod'
	config = config_db(db)
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor =  connection.cursor(dictionary=True)
			sql = f"UPDATE rutas_envios SET estado = '{estado}' WHERE id_ruta = {route_id}"
			cursor.execute(sql)
			for order in order_list:
				sql = f"INSERT IGNORE INTO ingreso_entrega_ordenes (order_id, total_a_recibir, total_recibido, razon_diferencia) VALUES ({order['order_id']}, {order['total']}, {order['ingresado']}, {order['razon']})"
				print(sql)
				cursor.execute(sql)
			connection.commit()
			cursor.close()
			connection.close()
			return True
		return False
	except Exception as e:
		print('Error al actualizar la data:', e)
		cursor.close()
		connection.close()
		return False

