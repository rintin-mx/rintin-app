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

def insertar_usuario_rol(usuario_id_fk, rol_id_fk,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            sql = "INSERT INTO usuarios_roles (usuario_id_fk, rol_id_fk) VALUES (%s, %s)"
            valores = (usuario_id_fk, rol_id_fk)
            cursor.execute(sql, valores)
            conexion.commit()
            print("usuarios_roles insertado exitosamente.")
             # Registrar el tiempo de finalización
            end_time = time.time()
            # Calcular la duración
            duration = end_time - start_time
            # Convertir a minutos y segundos
            minutes = int(duration // 60)
            seconds = int(duration % 60)
    except Error as e:
        print("Error al conectar a MariaDB", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def eliminar_usuario_rol(usuario_id_fk, rol_id_fk,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        cursor = conexion.cursor()
        sql = "DELETE FROM usuarios_roles WHERE usuario_id_fk = %s and rol_id_fk = %s"
        valores = (usuario_id_fk, rol_id_fk)
        cursor.execute(sql, valores)
        conexion.commit()
        print("Rol eliminado con éxito.")
    except mysql.connector.Error as error:
        print("Error al eliminar el rol: {}".format(error))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def actualizar_usuario_rol(usuario_id_fk, rol_id_fk,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            sql = "UPDATE roles_permisos SET rol_id = %s, permiso_id = %s"
            valores = (usuario_id_fk, rol_id_fk)
            cursor.execute(sql, valores)
            conexion.commit()
            print("actualizar_usuario_rol actualizado con éxito.4444444")
    except mysql.connector.Error as error:
        print("Error al actualizar el rol: {}".format(error))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_todos_los_usuario_rol(db='repl'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM usuarios_roles")
            # Obtener los roles_permisos
            roles_permisos = cursor.fetchall()
            return roles_permisos
    except mysql.connector.Error as error:
        print("Error al obtener los roles: {}".format(error))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    