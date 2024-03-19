import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
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
	post_type = 'shop_order' and post_status in ('wc-pickup-4','wc-recepcion-2') and post_parent = 0
),
children_orders as (
select
	post_parent as parent_id,
    group_concat(ID) as children_order
from
	wp_posts
where
	post_type = 'shop_order' and post_parent != 0
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