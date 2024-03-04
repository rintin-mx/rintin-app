# db/script_db.py
import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
import pandas as pd
import numpy as np


def config_db(env='repl') -> dict:
    """
    Function to configure database connection parameters based on environment.

    Parameters:
    db (string): Enviroment name.

    Returns:
    dict: A dictionary containing database connection parameters.
    """
    if env == 'prod':
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

def get_products_grouped_by_seller():
    config = config_db()
    try:
        connection = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = connection.cursor(dictionary=True)
        sql = """
select 
	id,
    post_author as seller_id,
    pm.meta_value as proveedor_id,
    u1.meta_value as seller_name,
    u2.meta_value as proveedor_name,
    u3.meta_value as bodega
from wp_posts
inner join wp_postmeta pm on post_id = id
inner join wp_usermeta u1 on u1.user_id = post_author
inner join wp_usermeta u2 on u2.user_id = pm.meta_value
inner join wp_usermeta u3 on u3.user_id = post_author
where post_type = 'product' and pm.meta_key = '_proveedor' and u1.meta_key = 'dokan_store_name' and u2.meta_key = 'dokan_store_name' and u3.meta_key = 'bodega' and u3.meta_value is not null
        """

        cursor.execute(sql)
        results = cursor.fetchall()
        results_df = pd.DataFrame(results)
    finally:
        cursor.close()
        connection.close()

    if len(results_df) > 0:
        results_df = results_df[['id','seller_id', 'proveedor_id', 'seller_name', 'proveedor_name', 'bodega']]
        results_general_df = results_df.to_dict(orient='list')
        return results_general_df
    else:
        return {}