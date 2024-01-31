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

def get_ordenes_generar_guia(db='repl') -> dict:
    config = config_db(db)
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_ordenes_query =f"""

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
        zonas_entrega.zona_entrega not like '%pickup%'
),
orders as (
	select 
		id
	from wp_posts
    where post_status = 'wc-generar_guia'
    and id not in (select distinct post_parent from wp_posts where post_type = 'shop_order')
),
ordermeta as (
	select
		post_id as order_id,
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
	from wp_postmeta inner join orders on orders.id = wp_postmeta.post_id
    group by post_id
)
select 
	order_id, 
    postcode, 
    state, 
    case when numero_guia is null then '' else numero_guia end as numero_guia, 
    case when logis_op = '' then null when logis_op = 'none' then null else logis_op end as logis_op
    from ordermeta inner join cps on cps.codigo_postal = ordermeta.postcode

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
            wp_ordenes.columns = ['order_id', 'postcode', 'state', 'numero_guia', 'logis_op']
            wp_order_general_dict = wp_ordenes.to_dict(orient='list')
            return wp_order_general_dict
        return None