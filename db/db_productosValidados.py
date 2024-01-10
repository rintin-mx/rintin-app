# db/script_db.py
import sys
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

def insert_productos_validados(productID, SKU, usuarioTimestamp, orderID, cantidadOrden, cantidadPickeada, fuente, email):
    db ='prod'
    config = config_db(db)
    start_time = time.time()
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Consulta SQL para insertar datos
            # Sentencia SQL para insertar datos
            sql = "INSERT INTO productosValidados (productID, SKU, usuarioTimestamp, orderID, cantidadOrden, cantidadPickeada, fuente, email) VALUES (%s, %s, %s, %s, %s, %s,%s, %s)"
            # Ejecutar la sentencia SQL
            cursor.execute(sql, (productID, SKU, usuarioTimestamp, orderID, cantidadOrden, cantidadPickeada,fuente, email))
            connection.commit()

            print("Evento insertado con éxito.")
            

    except Error as e:
        print("Error al conectar a la base de datos:", e)

    finally:
        # Cerrar la conexión y el cursor
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")

def update_order_product_status(product_id,estatus) -> dict:
    db='prod'
    config = config_db(db)
    start_time = time.time()
    try:
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor(dictionary=True)
        sql = "UPDATE wp_posts SET post_status = %s WHERE ID=%s"
        cursor.execute(sql, (estatus,product_id))
        conexion.commit()
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

 


