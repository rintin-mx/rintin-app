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
            'database': DATABASE,
            'charset': 'latin1'
        }
    else:
        config = {
            'user': USER_REPLICA,
            'password': PASSWORD_REPLICA,
            'host': HOST_REPLICA,
            'database': DATABASE_REPLICA
        }
    return config

def update_order_metadata(order_id, num_guia, logis_op):
    config = config_db('prod')
    print(':)')
    print(order_id)
    
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True, buffered=True)
            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "SELECT * FROM wp_postmeta WHERE post_id = %s AND meta_key = '_numero_guia_interno'"
            cursor.execute(sql, (order_id,))
            print('primer select')
            print(cursor.rowcount)
            if cursor.rowcount == 0:
                sql = "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, '_numero_guia_interno', %s)"
                cursor.execute(sql, (order_id, num_guia))
            else:
                sql = "UPDATE wp_postmeta SET meta_value = %s WHERE meta_key = '_numero_guia_interno' AND post_id = %s "
                cursor.execute(sql, (num_guia, order_id))

            sql = "SELECT * FROM wp_postmeta WHERE post_id = %s AND meta_key = '_logis_op_interno'"
            cursor.execute(sql, (order_id,))
            print('segundo select')
            print(cursor.rowcount)
            if cursor.rowcount == 0:
                sql = "INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES (%s, '_logis_op_interno', %s)"
                cursor.execute(sql, (order_id, logis_op))
            else:
                sql = "UPDATE wp_postmeta SET meta_value = %s WHERE meta_key = '_logis_op_interno' AND post_id = %s "
                cursor.execute(sql, (logis_op, order_id))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return False

def get_ordenes_generar_guia(db='repl') -> dict:
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
		post_status,
        case when meta_value is null then wp_dokan_orders.seller_id else meta_value end as seller_id
	from wp_posts 
    left join wp_dokan_orders on order_id = wp_posts.id
    left join wp_postmeta on post_id = wp_posts.id
	where post_type = 'shop_order' and post_status NOT IN ('wc-pendientes_ograma','wc-failed', 'wc-caducado','wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial')
    and wp_posts.id not in (select distinct post_parent from wp_posts)
    and meta_key = '_dokan_vendor_id'
    having seller_id != 2705
),
order_shipping as (
	select 
		distinct order_id
	from wp_woocommerce_order_items where order_item_type = 'shipping' and order_item_name like '%oax%'
),
grouped_orders as(
select 
	post_parent,
	count(case when post_status not in ( 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end) as ordenes_activas,
	count(case when post_status = 'wc-generar_guia' then id else null end) as num_hijos_guia,
    group_concat(case when post_status not in ( 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-delivered', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then id else null end separator ', ') as hijos_guia
from 
	orders
group by post_parent
having num_hijos_guia > 0
),
ordermeta as (
	select
		post_id as order_id,
        hijos_guia,
        ordenes_activas,
        num_hijos_guia,
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
				when meta_key = '_numero_guia' then meta_value
				else NULL
			end
		) AS numero_guia,
        max(
			case
				when meta_key = '_logis_op' then meta_value
				else NULL
			end
		) AS logis_op
	from wp_postmeta inner join grouped_orders on grouped_orders.post_parent = wp_postmeta.post_id
    group by post_id, hijos_guia, ordenes_activas, num_hijos_guia
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
)
select 
	order_id,
    case when hijos_guia = order_id then null else hijos_guia end as hijos_guia,
    postcode,
    state,
	case when numero_guia is null then '' else numero_guia end as numero_guia, 
    case when logis_op = '' then null when logis_op = 'none' then null else logis_op end as logis_op,
	ordenes_activas,
	num_hijos_guia,
	zona_entrega
from ordermeta 
left join cps on cps.codigo_postal = ordermeta.postcode
where
	zona_entrega like '%pickup%' or order_id in (select * from order_shipping)

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
            wp_ordenes.columns = ['order_id', 'hijos_guia' , 'postcode', 'state', 'numero_guia', 'logis_op', 'ordenes_activas', 'num_hijos_guia', 'zona_entrega']
            wp_order_general_dict = wp_ordenes.to_dict(orient='list')
            return wp_order_general_dict
        return None