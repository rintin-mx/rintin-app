# db/script_db.py
import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

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

def get_products_grouped_by_seller():
    '''
    Get products that have a "bodega" linked to them with their respective seller and proveedor information
    
    Returns:
    list: A list containing the query results. None if no results where queried
    '''
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
where post_type = 'product' and pm.meta_key = '_proveedor' and u1.meta_key = 'dokan_store_name' and u2.meta_key = 'dokan_store_name' and u3.meta_key = 'bodega' and u3.meta_value is not null and post_status != 'proceso_stock'
        """

        cursor.execute(sql)
        results = cursor.fetchall()
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

    if len(results) > 0:
        return results
    else:
        return None

def get_products_by_proveedor_seller(seller_id, proveedor_id):
    '''
    Get products that have a "bodega" linked to them with their respective seller and proveedor information
    
    Parameters:
    seller_id (int): Seller id
    proveedor_id (int): Proveedor id
    
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
    from wp_posts
    inner join wp_postmeta pm on post_id = id
    inner join wp_usermeta u1 on u1.user_id = post_author
    inner join wp_usermeta u2 on u2.user_id = pm.meta_value
    inner join wp_usermeta u3 on u3.user_id = post_author
    where post_type = 'product' 
    and pm.meta_key = '_proveedor' 
    and u1.meta_key = 'dokan_store_name' 
    and u2.meta_key = 'dokan_store_name' 
    and u3.meta_key = 'bodega' 
    and u3.meta_value is not null
    and pm.meta_value = {proveedor_id}
    and post_author ={seller_id}
    and post_status != 'proceso_stock'
),
product_meta as(
	select
		post_id as product_id, 
        post_title,
        post_status,
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
	from wp_postmeta
	inner join skus on skus.id = post_id
	group by post_id, post_title, post_status
    having sku is not null
)
select 
	product_id,
    product_meta.post_title,
    product_meta.post_status,
    sku,
    replace(wp_posts.guid, 'http://dev.', 'https://') as img_url,
    units_per_pack,
    stock,
    cost
from product_meta
left join wp_posts on image_id = id
'''
        cursor.execute(sql)
        results = cursor.fetchall()
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    results_df = pd.DataFrame(results)
    return results_df

def get_products_in_active_orders(seller_id):
    '''
    Get products that that are in active orders of an specific seller
    
    Parameters:
    seller_id (int): Seller id
    
    Returns:
    dict: A dictionary of arrays containing the query results. Dictionary with empty arrays if no results where queried
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
            and seller_id = {seller_id}
        )
        select product_id, sum(qty) as stock_count from orders group by product_id
        '''
        cursor.execute(sql)
        results = cursor.fetchall()
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    if len(results) > 0:
        results_df = pd.DataFrame(results)
        results_dict = results_df.to_dict(orient='list')
        return results_dict
    return {"product_id": [], "stock_count": []}

def insert_to_stock_count_table(product_id, stock_fisico, stock_total):
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
            sql = "INSERT INTO stock_bodegas (product_id, stock_total, stock_fisico) VALUES (%s, %s, %s)"
            cursor.execute(sql, (product_id, stock_fisico, stock_total))
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

def update_product_status_bulk(product_id_list):
    '''
    Update of product status to proceso_stock
    
    Parameters:
    product_id_list (string): String of concatenated ids separated by ', '
    
    Return: boolean
    '''
    config = config_db('prod')
    print(product_id_list)
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True, buffered=True)
            sql = f"UPDATE wp_posts SET post_status = 'proceso_stock' WHERE id in ({product_id_list})"
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

def update_product_stock_on_db(product_id, actual_stock, new_stock):
    '''
    Update of product stock made directly in the wp_postmeta table
    
    Parameters:
    product_id (int): Id of the product
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
                sql = f"UPDATE wp_postmeta SET meta_value = '{new_stock}' WHERE meta_key = '_stock' AND post_id = {product_id}"
                cursor.execute(sql)
                sql = f"UPDATE wp_postmeta SET meta_value = 'instock' WHERE meta_key = '_stock_status' AND post_id = {product_id}"
                cursor.execute(sql)
                try:
                    sql = f"DELETE from wp_term_relationships WHERE object_id = {product_id} and term_taxonomy_id = '212'"
                    cursor.execute()
                except Exception:
                    pass
                sql = f"UPDATE wp_posts SET post_status = 'publish' WHERE id = {product_id}"
                cursor.execute(sql)
            else:
                sql = f"UPDATE wp_postmeta SET meta_value = '{new_stock}' WHERE meta_key = '_stock' AND post_id = {product_id}"
                cursor.execute(sql)
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