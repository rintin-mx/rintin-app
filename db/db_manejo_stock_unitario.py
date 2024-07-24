import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA
from integration.cache_api import update_stock_by_sku

import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def config_db(env='repl') -> dict:
    """
    Function to configure database connection parameters based on environment.

    Parameters:
    db (string): Enviroment name.

    Returns:
    dict: A dataframe containing database connection parameters.
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

def get_stok_in_orders(sku, db = 'repl'):
    '''
    Get stock in active orders of an specific sku
    
    Parameters:
    sku (Str): product's sku
    
    Returns:
    an integer with the total of stock in orders. If 0 then 0
    '''
    config = config_db()
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        sql = f'''
        with orders as (
	select 
		oim.meta_value as product_id,
		oim_qty.meta_value as qty
	from wp_posts orders 
	inner join wp_dokan_orders on wp_dokan_orders.order_id = orders.id
	inner join wp_posts estado on replace(orders.post_status, 'wc-', '') = estado.post_name 
	inner join wp_postmeta estado_m on estado.id = estado_m.post_id
	inner join wp_woocommerce_order_items oi on orders.id = oi.order_id
	inner join wp_woocommerce_order_itemmeta oim on oi.order_item_id = oim.order_item_id
	inner join wp_woocommerce_order_itemmeta oim_qty on oi.order_item_id = oim_qty.order_item_id
	where orders.post_type = 'shop_order' 
	and estado_m.meta_key = '_pre_pickeo' 
	and estado_m.meta_value = 1 
	and order_item_type = 'line_item' 
	and oim.meta_key = '_product_id'
	and oim_qty.meta_key = '_qty'
)
select sum(qty) as stock_count from orders
where product_id in (select post_id from wp_postmeta where meta_key = '_sku' and meta_value = '{sku}')
group by product_id
        '''
        cursor.execute(sql)
        results = cursor.fetchall()
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    if len(results) > 0:
        results_df = pd.DataFrame(results)
        return results_df['stock_count'][0]
    
    return 0

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

def get_one_product(sku, db = 'repl'):
    '''
    Get one product's information (id, name, stock, status, image, units per pack, cost)
    
    Parameters:
    sku (Str): product's sku
    
    Returns:
    DataFrame: A DataFrame containing the query results
    '''
    config = config_db()
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        sql = f'''
with skus as (
select 
	id,
	post_title,
	post_status
from 
	wp_posts
where 
	id = (select post_id from wp_postmeta where meta_key = '_sku' and meta_value = '{sku}')
),
product_meta as(
	select
		post_id as product_id,
        skus.post_title,
		skus.post_status,
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
				when `wp_postmeta`.`meta_key` = '_stock' then `wp_postmeta`.`meta_value`
				else NULL
			end
		) AS `stock`,
        max(
			case
				when `wp_postmeta`.`meta_key` = '_cost_of_goods' then `wp_postmeta`.`meta_value`
				else NULL
			end
		) AS `cost`,
		max(
			case
				when `wp_postmeta`.`meta_key` = '_units_per_pack' then `wp_postmeta`.`meta_value`
				else NULL
			end
		) AS `units_per_pack`
	from 
		wp_postmeta
	inner join
		skus on skus.id = wp_postmeta.post_id
	where 
		post_id in (select post_id from wp_postmeta where meta_key = '_sku' and meta_value = '{sku}')
)
select 
	product_id,
    product_meta.post_title,
    product_meta.post_status,
    sku,
    replace(wp_posts.guid, 'http://dev.', 'https://') as img_url,
    units_per_pack,
    stock,
    case when cost = '' or cost is null then 0 else cost end as cost
from 
	product_meta
left join 
	wp_posts on image_id = id
'''
        cursor.execute(sql)
        results = cursor.fetchall()
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    results_df = pd.DataFrame(results)
    return results_df

def update_product_status(product_id):
    '''
    Update of product status to proceso_stock
    
    Parameters:
    product_id (int): Id of the product
    
    Return: boolean
    '''
    config = config_db('prod')
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True, buffered=True)
            sql = f"UPDATE wp_posts SET post_status = 'proceso_stock' WHERE id = {product_id}"
            cursor.execute(sql)
            connection.commit()
            cursor.close()
            connection.close()
            return True
        return False
    except Exception as e:
        print(e)
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
        return False
    
def update_product_stock_on_db(product_id, actual_stock, new_stock, sku):
    '''
    Update of product stock made directly in the wp_postmeta table
    
    Parameters:
    product_id (int): Id of the product
    actual_stock (int): Previous stock value
    new_stock (int): Stock value to insert
    
    Return: boolean
    '''
    config = config_db('prod')
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            current_utc_time = datetime.utcnow()
            cst_offset = timedelta(hours=-6)
            cst_time = current_utc_time + cst_offset
            mysql_datetime_cst = cst_time.strftime('%Y-%m-%d %H:%M:%S')
            my_sql_datetime_utc = current_utc_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor = connection.cursor(dictionary=True, buffered=True)
            if new_stock != 0:
                #sql = f"UPDATE wp_postmeta SET meta_value = '{new_stock}' WHERE meta_key = '_stock' AND post_id = {product_id}"
                #cursor.execute(sql)
                update_stock_by_sku(sku, str(int(new_stock)))
                sql = f"UPDATE wp_postmeta SET meta_value = 'instock' WHERE meta_key = '_stock_status' AND post_id = {product_id}"
                cursor.execute(sql)
                try:
                    sql = f"DELETE from wp_term_relationships WHERE object_id = {product_id} and term_taxonomy_id = '212'"
                    cursor.execute(sql)
                except Exception:
                    pass
                sql = f"UPDATE wp_posts SET post_status = 'publish' WHERE id = {product_id}"
                cursor.execute(sql)
            else:
                #sql = f"UPDATE wp_postmeta SET meta_value = '{new_stock}' WHERE meta_key = '_stock' AND post_id = {product_id}"
                #cursor.execute(sql)
                update_stock_by_sku(sku, str(int(new_stock)))
                sql = f"UPDATE wp_postmeta SET meta_value = 'outofstock' WHERE meta_key = '_stock_status' AND post_id = {product_id}"
                cursor.execute(sql)
            sql = "INSERT INTO stock_log (product_id, previous_stock, new_stock, reason, modification_date, modification_date_mx) VALUES (%s, %s, %s, 'Cambio de stock por herramienta interna', %s, %s)"
            cursor.execute(sql, (product_id, actual_stock, new_stock, my_sql_datetime_utc, mysql_datetime_cst))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        return False
    except Exception as e:
        print(e)
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
        return False
    
def insert_to_stock_count_table(product_id, stock_sistema, stock_ordenes_activas, stock_total, stock_contado, diferencias, stock_a_insertar, responsable):
    '''
    Insert the counted product into the stock_bodegas table
    
    Parameters:
    product_id (int): Id of the product
    stock_fisico (int): Stock counted in the process
    stock_total (int): Stock in database + active order stock
    
    Return: boolean
    '''
    config = config_db('prod')
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True, buffered=True)
            current_utc_time = datetime.utcnow()
            cst_offset = timedelta(hours=-6)
            cst_time = current_utc_time + cst_offset
            mysql_datetime_cst = cst_time.strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO stock_bodegas (product_id, stock_sistema, stock_ordenes_activas, stock_total, stock_contado, diferencias, stock_a_insertar, fecha, responsable, fuente) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'conteo')"
            cursor.execute(sql, (product_id, stock_sistema, stock_ordenes_activas, stock_total, stock_contado, diferencias, stock_a_insertar, mysql_datetime_cst, responsable))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        return False
    except Exception as e:
        print(e, 'error al insertar')
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
        return False