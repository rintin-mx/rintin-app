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

def get_products(db = 'repl'):
    
    # Get all the information needed from the products with stock in showroom

    # Parameters:
    # None

    # Returns:
    # Dataframe: A Dataframe containing the query results
    # ()

    config = config_db(db)
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        
        products_in_showroom = f"""
        select
	replace(link_imagen, 'http://dev.', 'https://') as img_url,
	pvm.product_id,
    sku_interno as sku,
    nombre_proveedor as proveedor,
    nombre_dueno_producto as dueno_producto,
    meta_brand as marca,
    case when MAX(case when meta_key = '_stock' then meta_value end) is null or MAX(case when meta_key = '_stock' then meta_value end) < 0 then 0 else MAX(case when meta_key = '_stock' then meta_value end) end as real_stock,
    nombre_producto as product_name,
    seller_name as seller,
    MAX(case when meta_key = '_stock_shr' then meta_value end) as stock_showroom
from
	product_view_materialized pvm
inner join
	wp_postmeta pm on pm.post_id = pvm.product_id
where
	meta_key = '_stock_shr' or meta_key = '_stock'
group by
	product_id
having
	stock_showroom > 0
        """
        # Ejecutar la primera consulta
        cursor.execute(products_in_showroom)

        # Obtener los resultados de la primera consulta
        resultados_products_in_showroom = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        products_in_showroom = pd.DataFrame(resultados_products_in_showroom)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
    return products_in_showroom

def get_all_skus(db = 'repl'):
    # Get all the information needed from the product selected

    # Parameters:

    # Returns:
    # Dataframe: A Dataframe containing the query results
    # (SKU)

    config = config_db(db)
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        
        all_skus = f"""
        select
	meta_value as SKU
from
	wp_postmeta
where
	meta_key = '_sku'
        """
        # Ejecutar la primera consulta
        cursor.execute(all_skus)

        # Obtener los resultados de la primera consulta
        resultados_all_skus = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        all_skus = pd.DataFrame(resultados_all_skus)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
    return all_skus

def get_one_product_info(product_sku, db = 'repl'):
    # Get all the information needed from the product selected

    # Parameters:
    # product_sku

    # Returns:
    # Dataframe: A Dataframe containing the query results
    # ()

    config = config_db(db)
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        
        products_in_showroom = f"""
        select
	replace(link_imagen, 'http://dev.', 'https://') as img_url,
	pvm.product_id,
    sku_interno as sku,
    nombre_proveedor as proveedor,
    nombre_dueno_producto as dueno_producto,
    meta_brand as marca,
    case when MAX(case when meta_key = '_stock' then meta_value end) is null or MAX(case when meta_key = '_stock' then meta_value end) < 0 then 0 else MAX(case when meta_key = '_stock' then meta_value end) end as real_stock,
    nombre_producto as product_name,
    seller_name as seller,
    MAX(case when meta_key = '_stock_shr' then meta_value end) as stock_showroom
from
	product_view_materialized pvm
inner join
	wp_postmeta pm on pm.post_id = pvm.product_id
where
	meta_key = '_stock_shr' or meta_key = '_stock'
group by
	product_id
having
	sku = '{product_sku}'
        """
        # Ejecutar la primera consulta
        cursor.execute(products_in_showroom)

        # Obtener los resultados de la primera consulta
        resultados_products_in_showroom = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        products_in_showroom = pd.DataFrame(resultados_products_in_showroom)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
    return products_in_showroom