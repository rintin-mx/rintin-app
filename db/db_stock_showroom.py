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
        with products as (
select
	wp_posts.ID as product_id,
    display_name as seller,
    post_title as product_name
from
	wp_posts
inner join
	wp_users on wp_users.id = post_author
where
	post_type = 'product'
), 
meta as (
select
	post_id as product_id,
    max(
		case
			when meta_key = '_sku' then meta_value
			else NULL
		end
	) AS sku,
    max(
		case
			when meta_key = '_stock' then meta_value
			else NULL
		end
	) AS real_stock,
    max(
		case
			when meta_key = '_proveedor' then meta_value
			else NULL
		end
	) AS proveedor,
	max(
		case
			when meta_key = '_dueno_producto' then meta_value
			else NULL
		end
	) AS dueno_producto,
    max(
		case
			when meta_key = '_brand' then meta_value
			else NULL
		end
	) AS brand,
    max(
		case
			when meta_key = '_stock_shr' then meta_value
			else NULL
		end
	) AS stock_showroom,
    max(
		case
			when meta_key = '_thumbnail_id' then meta_value
			else NULL
		end
	) AS image_id
from
	wp_postmeta
group by
	post_id
having
	stock_showroom > 0
),
product_prov as (
select
	products.product_id as product_id,
    sku,
    display_name as proveedor,
    dueno_producto,
    brand,
    real_stock,
    stock_showroom,
    product_name,
    seller,
    image_id
from
	meta
inner join
	products on products.product_id = meta.product_id
inner join
	wp_users on proveedor = wp_users.ID   
)
select
	product_id,
    sku,
    proveedor,
    display_name as dueno_producto,
    case when brand is null then 'N/A' else brand end as marca,
    real_stock,
    stock_showroom,
    product_name,
    seller,
    replace(wp_posts.guid, 'http://dev.', 'https://') as img_url
from
	product_prov
inner join
	wp_users on dueno_producto = wp_users.ID
inner join
	wp_posts on wp_posts.id = image_id
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
        with products as (
select
	wp_posts.ID as product_id,
    display_name as seller,
    post_title as product_name
from
	wp_posts
left join
	wp_users on wp_users.id = post_author
where
	post_type = 'product'
),
meta as (
select
	post_id as product_id,
    max(
		case
			when meta_key = '_sku' then meta_value
			else NULL
		end
	) AS sku,
    max(
		case
			when meta_key = '_stock' then meta_value
			else NULL
		end
	) AS real_stock,
    max(
		case
			when meta_key = '_proveedor' then meta_value
			else NULL
		end
	) AS proveedor,
	max(
		case
			when meta_key = '_dueno_producto' then meta_value
			else NULL
		end
	) AS dueno_producto,
    max(
		case
			when meta_key = '_brand' then meta_value
			else NULL
		end
	) AS brand,
    max(
		case
			when meta_key = '_stock_shr' then meta_value
			else NULL
		end
	) AS stock_showroom,
    max(
		case
			when meta_key = '_thumbnail_id' then meta_value
			else NULL
		end
	) AS image_id
from
	wp_postmeta
where post_id in (select post_id from wp_postmeta where meta_key = '_sku' and meta_value = '{product_sku}')
),
product_prov as (
select
	products.product_id as product_id,
    sku,
    display_name as proveedor,
    dueno_producto,
    brand,
    real_stock,
    stock_showroom,
    product_name,
    seller,
    image_id
from
	meta
inner join
	products on products.product_id = meta.product_id
left join
	wp_users on proveedor = wp_users.ID   
)
select
	product_id,
    sku,
    proveedor,
    display_name as dueno_producto,
    case when brand is null then 'N/A' else brand end as marca,
    real_stock,
    stock_showroom,
    product_name,
    seller,
    replace(wp_posts.guid, 'http://dev.', 'https://') as img_url
from
	product_prov
left join
	wp_users on dueno_producto = wp_users.ID
left join
	wp_posts on wp_posts.id = image_id
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

def update_stock_showroom(product_id, new_stock_showroom, should_create):
      
    # Update metadata 'stock_shr'

    # Parameters:
    # product_id, new_stock_showroom

    # Returns:
    # False

        db = 'prod'
        config = config_db(db)
        
        try:
            connection = mysql.connector.connect(**config)

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                if should_create:
                    sql = f"INSERT INTO wp_postmeta (post_id, meta_key, meta_value) VALUES ({product_id}, '_stock_shr', {new_stock_showroom})"
                else:
                    sql = f"update wp_postmeta set meta_value = {new_stock_showroom} where meta_key = '_stock_shr' and post_id = {product_id}"
                cursor.execute(sql)
                connection.commit()
                cursor.close()
                connection.close()
                return True
            return False
        except Exception as e:
            return False