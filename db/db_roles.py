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

def insert_rol(rol, descripcion,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            sql = "INSERT INTO roles (nombre_rol, descripcion) VALUES (%s, %s)"
            valores = (rol, descripcion)
            cursor.execute(sql, valores)
            conexion.commit()
             # Registrar el tiempo de finalización
            end_time = time.time()

            # Calcular la duración
            duration = end_time - start_time

            # Convertir a minutos y segundos
            minutes = int(duration // 60)
            seconds = int(duration % 60)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def eliminar_rol(rol_id,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        cursor = conexion.cursor()
        sql = "DELETE FROM roles WHERE rol_id = %s"
        valores = (rol_id,)
        cursor.execute(sql, valores)
        conexion.commit()
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def actualizar_rol(rol_id, nuevo_nombre, nueva_descripcion,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            sql = "UPDATE roles SET nombre_rol = %s, descripcion = %s WHERE rol_id = %s"
            valores = (nuevo_nombre, nueva_descripcion, rol_id)
            cursor.execute(sql, valores)
            conexion.commit()
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_todos_los_roles(db='repl'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM roles")
            # Obtener los registros
            registros = cursor.fetchall()
            return registros
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    