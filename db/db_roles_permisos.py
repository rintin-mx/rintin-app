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

def insertar_rol_permiso(rol_id, permiso_id,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            sql = "INSERT INTO roles_permisos (rol_id_fk, permiso_id_fk) VALUES (%s, %s)"
            valores = (rol_id, permiso_id)
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

def eliminar_rol_permiso(rol_id, permiso_id,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        cursor = conexion.cursor()
        sql = "DELETE FROM roles_permisos WHERE rol_id_fk = %s and permiso_id_fk = %s"
        valores = (rol_id,permiso_id)
        cursor.execute(sql, valores)
        conexion.commit()
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def actualizar_rol_permiso(rol_id, permiso_id,db='prod'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            sql = "UPDATE roles_permisos SET rol_id = %s, permiso_id = %s"
            valores = (rol_id, permiso_id)
            cursor.execute(sql, valores)
            conexion.commit()
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_todos_los_roles_permisos(db='repl'):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("""SELECT rp.rol_id_fk ,rp.permiso_id_fk,r.nombre_rol, p.nombre_permiso
                FROM roles_permisos rp 
                inner join roles r on rp.rol_id_fk =r.rol_id 
                inner join permisos p  on p.permiso_id =rp.permiso_id_fk 
                INNER JOIN  opciones_sistema os on os.ops_id = p.ops_id_fk 
                """)
            # Obtener los roles_permisos
            roles_permisos = cursor.fetchall()
            return roles_permisos
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    