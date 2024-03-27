import sys
import time
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
from mysql.connector import Error
import pandas as pd

def config_db(db='repl') -> dict:
    
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

def insert_product_problem(product):
     
    # Create an entry on the "inconvenientes_unitarios_entregas"

    # Parameters:
    # order_id: str with the order_id

    # Returns:
    # False

	db = 'prod'
	config = config_db(db)
	current_date = time.strftime('%Y-%m-%d %H:%M:%S')
	try:
		connection = mysql.connector.connect(**config)
		if connection.is_connected():
			cursor = connection.cursor(dictionary=True)
			sql = "INSERT INTO inconvenientes_unitarios_entregas (order_item_id, cantidad_no_entrega, razon_no_entrega, fecha, fuente) VALUES (%s, %s, %s, %s, 'entregas_pickup')"
			cursor.execute(sql, (product['order_item_id'], product['cantidad_entregada'], product['razon_no_entrega'], current_date))
			connection.commit()
			cursor.close()
			connection.close()
			return True
		return False
	except Exception as e:
		return False

def insert_item_problem(product):
     
    # Create an entry on the "inconvenientes_entregas"

    # Parameters:
    # order_id: str with the order_id

    # Returns:
    # False

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
		return False

def get_order_items(order_id, db='repl') -> dict:
     
    # Get a list of order_items and their info

    # Parameters:
    # order_id: str with the order_id

    # Returns:
    # dictionary: a dictionary containing the query results 
    #             (order_item_id, order_item_name, qty, sku, img_url, order_id, line_total, order_item_type)

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
        where id not in (select distinct post_parent from wp_posts where post_type = 'shop_order') and post_status != 'wc-cancelled'
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

def get_lista_ordenes_padre(db='repl'):

    # Get a list of Parent orders and their children orders to be searched in the UI

    # Parameters:
    # None

    # Returns:
    # Dataframe: a dataframe containing the query results 
    #             (Parent_order_id, [children_order_id,children_order_id, ..., children_order_id])

    
    config = config_db(db)
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        ordenes_padres_e_hijos_sql = """
        with parent_orders as (
select
	ID as order_id
from
	wp_posts
where
	post_type = 'shop_order' and post_parent = 0 and post_status in ('wc-pickup-4','wc-recepcion-2') and ID not in (
    select
		distinct post_parent
	from
		wp_posts
    ) and post_date >= '2023-11-25 15:05:39'
),
children_orders as (
select
	post_parent as parent_id,
    group_concat(ID) as children_order
from
	wp_posts
where
	post_type = 'shop_order' and post_parent != 0 and post_date >= '2023-11-25 15:05:39'
group by
	post_parent
), shipping_detail as (
  select
    wp_woocommerce_order_items.order_item_name AS order_item_name,
    wp_woocommerce_order_items.order_id AS order_id
  from
    (
      wp_woocommerce_order_items
    )
  where
    wp_woocommerce_order_items.order_item_type = 'shipping'
),
shipping_method AS (
select
	shipping_detail.order_id AS order_id,
	group_concat(
	  shipping_detail.order_item_name separator ','
	) AS order_item_name
from
	shipping_detail
group by
	shipping_detail.order_id
),
order_client_info AS (
select 
	post_id as order_id,
    MAX(case When meta_key = '_customer_user' then meta_value else null end) as customer_user,
	MAX(case When meta_key = '_billing_first_name' then meta_value else null end) as billing_first_name,
    MAX(case When meta_key = '_billing_last_name' then meta_value else null end) as billing_last_name,
    MAX(case When meta_key = '_billing_phone' then meta_value else null end) as billing_phone
from
	wp_postmeta
group by
	post_id
),
helper as (
select
	order_client_info.order_id as order_id,
    concat(billing_first_name, ' ', billing_last_name) as full_name,
    order_client_info.billing_phone as phone,
    shipping_method.order_item_name as shipping_method
from
	order_client_info
left join
	shipping_method on shipping_method.order_id = order_client_info.order_id
)
select
	parent_orders.order_id as order_id,
    helper.full_name as full_name,
    helper.phone as phone,
    helper.shipping_method as shipping_method,
    case when children_orders.children_order is null then parent_orders.order_id else children_orders.children_order end as children_orders
from
	parent_orders
left join
	children_orders on parent_orders.order_id = children_orders.parent_id
left join
	helper on helper.order_id = parent_orders.order_id
        """
        
        # Ejecutar la primera consulta
        cursor.execute(ordenes_padres_e_hijos_sql)

        # Obtener los resultados de la primera consulta
        resultados_ordenes_padres_e_hijos_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        ordenes_padres_e_hijos = pd.DataFrame(resultados_ordenes_padres_e_hijos_sql)

    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close() 
        # Nueva lista de nombres de columnas
        return ordenes_padres_e_hijos
    
def ingreso_entrega(order_id, total_a_recibir, total_recibido, razon_diferencia, img_url, db = 'prod'):
    config = config_db(db)
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = f"""
            insert into ingreso_entrega_ordenes
                (order_id, total_a_recibir, total_recibido, razon_diferencia, fuente, img_url)
            values
                ({order_id}, {total_a_recibir}, {total_recibido}, '{razon_diferencia}', 'entregas_pickup', '{img_url}')
            """
            # Ejecutar la sentencia SQL
            cursor.execute(sql)
            connection.commit()

            print("Cambio insertado con éxito.")
            

    except Error as e:
        print("Error al conectar a la base de datos:", e)

    finally:
        # Cerrar la conexión y el cursor
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")