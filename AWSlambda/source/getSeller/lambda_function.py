import json
import mysql.connector
import time
import pandas as pd
import os


def config_db(db) -> dict:
    # Registrar el tiempo de inicio
    if db == 'prod':
        config = {
            'user': os.environ['USER_PROD'],
            'password': os.environ['PASSWORD_PROD'],
            'host': os.environ['HOST_PROD'],
            'database': os.environ['DATABASE_PROD']
        }
    else:
        config = {
            'user': os.environ['USER_REPLICA'],
            'password': os.environ['PASSWORD_REPLICA'],
            'host': os.environ['HOST_REPLICA'],
            'database': os.environ['DATABASE_REPLICA']
        }
    return config

def lambda_handler(event, context):
    config = config_db('repl')
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        wp_seller_sql = """
                with orders as (
                select
                    id,
                    post_status
                from
                    wp_posts
                where
                    post_status = 'wc-recolectar-2'
            ),
            ordermeta as(
                select
                    post_id as order_id,
                    post_status,
                    max(
                        case
                            when `meta_key` = '_dokan_vendor_id' then `meta_value`
                            else NULL
                        end
                    ) AS `dokan_vendor_id`
                from
                    wp_postmeta inner join orders on orders.id = post_id
                group by post_id, post_status
                having dokan_vendor_id in ('3587', '998', '1352', '2636', '3759', '2751', '2166', '1663', '2705', '7180', '7201', '7202','3465', '5894')
            ),
            users as (
                select 
                    user_id,
                    max(
                        case
                            when `meta_key` = 'dokan_store_name' then `meta_value`
                            else NULL
                        end
                    ) AS `dokan_store_name`
                from wp_usermeta
                inner join ordermeta on ordermeta.dokan_vendor_id = user_id
                group by user_id
            )
            select order_id , dokan_vendor_id as seller_id, dokan_store_name as seller_name, post_status as estado
            from ordermeta
            inner join users on users.user_id = ordermeta.dokan_vendor_id
            order by order_id ASC 
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
        wp_seller=wp_seller[['order_id', 'seller_name','estado']]
        wp_seller.columns = ['order_id', 'Seller','estado']
        wp_seller_general_dict = wp_seller.to_dict(orient='list')
        return {
        'statusCode': 200,
        'body': json.dumps(wp_seller_general_dict),
        'headers': {
            'Content-Type': 'application/json'
        }
    }

