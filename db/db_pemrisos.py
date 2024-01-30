# db/script_db.py
import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
import pandas as pd
import numpy as np
import time
import bcrypt
from mysql.connector import Error


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


# Función para insertar un permiso
def insertar_permiso(ops_id_fk, nombre_permiso, descripcion,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            # Consulta SQL para insertar un permiso
            insert_query = "INSERT INTO permisos (ops_id_fk, nombre_permiso, descripcion) VALUES (%s, %s, %s)"
            data = (ops_id_fk, nombre_permiso, descripcion)

            cursor.execute(insert_query, data)
            conexion.commit()
            print("Permiso insertado exitosamente.")

    except Error as e:
        print("Error al insertar el permiso:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Función para eliminar un permiso por ID
def eliminar_permiso(permiso_id,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            # Consulta SQL para eliminar un permiso por ID
            delete_query = "DELETE FROM permisos WHERE permiso_id = %s"
            data = (permiso_id,)
            cursor.execute(delete_query, data)
            conexion.commit()
            print("Permiso eliminado exitosamente.")

    except Error as e:
        print("Error al eliminar el permiso:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def actualizar_permiso(permiso_id, ops_id_fk, nuevo_nombre, nueva_descripcion,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()

            # Consulta SQL para actualizar un permiso por ID
            update_query = "UPDATE permisos SET ops_id_fk = %s, nombre_permiso = %s, descripcion = %s WHERE permiso_id = %s"
            data = (ops_id_fk, nuevo_nombre, nueva_descripcion, permiso_id)


            cursor.execute(update_query, data)
            conexion.commit()
            print("Permiso actualizado exitosamente.")

    except Error as e:
        print("Error al actualizar el permiso:", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Función para obtener todos los permisos
def obtener_todos_los_permisos(db='repl'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            # Consulta SQL para obtener todos los permisos
            select_query = "SELECT * FROM permisos"
            cursor.execute(select_query)
            permisos = cursor.fetchall()
            print("Permiso obtenido exitosamente.")
            print(permisos)

            return permisos

    except Error as e:
        print("Error al obtener los permisos:", e)
        return None
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()