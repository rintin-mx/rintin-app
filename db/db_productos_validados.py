# db/script_db.py
import sys

from integration.cache_api import update_stock_by_sku
sys.path.append('..')
import streamlit as st
from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
from mysql.connector import Error
import time
import datetime



def config_db(db='repl') -> dict:
    # Registrar el tiempo de inicio
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

def insert_productos_validados(productID, SKU, usuarioTimestamp, orderID, cantidadOrden, cantidadPickeada, fuente, email, estado_anterior, estado_actual, razon):
    db ='prod'
    config = config_db(db)
    start_time = time.time()
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "INSERT INTO validacion_stock (productID, SKU, usuarioTimestamp, orderID, cantidadOrden, cantidadPickeada, fuente, email, estado_anterior, estado_actual, razon) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)"
            # Ejecutar la sentencia SQL
            cursor.execute(sql, (productID, SKU, usuarioTimestamp, orderID, cantidadOrden, cantidadPickeada,fuente, email, estado_anterior, estado_actual, razon))
            connection.commit()

            
    finally:
        # Cerrar la conexión y el cursor
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_order_product_status(sku, razon) -> dict:
    '''
    Update of product stock through the wordpress api
    
    Parameters:
    sku (string): product's sku
    
    Return: boolean
    '''
    try:
        update_stock_by_sku(sku, '0', razon)
        return True
    except Exception as e:
        print(e)

 


