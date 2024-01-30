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

def insert_user(db,userName, password):
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            # Hashing de la contraseña
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            print(hashed)
            query = "INSERT INTO userApp (email, contrasena) VALUES (%s, %s)"
            print(query)
            valores = (userName, hashed)
            print(valores)
            cursor.execute(query, valores)
            conexion.commit()
            print("Usuario insertado exitosamente.")
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

def validate_user(db,userName, password):
    print("validate_user")
    print(userName)
    print(password)
    config = config_db(db)
    # Establecer la conexión a la base de datos
    conexion = mysql.connector.connect(**config)
    # Registrar el tiempo de inicio
    start_time = time.time()
    try:
        if conexion.is_connected():
            cursor = conexion.cursor()
            query = "SELECT contrasena FROM userApp WHERE email = %s"
            cursor.execute(query, (userName,))
            resultado = cursor.fetchone()
            print("resultado")
            print(resultado)
            if resultado:
                contrasena_almacenada = resultado[0]
                # Compara la contraseña ingresada con el hash almacenado
                if bcrypt.checkpw(password.encode('utf-8'), contrasena_almacenada.encode('utf-8')):
                    print("Acceso permitido.")
                    end_time = time.time()
                    # Calcular la duración
                    duration = end_time - start_time
                    # Convertir a minutos y segundos
                    minutes = int(duration // 60)
                    seconds = int(duration % 60)
                    return True
                else:
                    print("Acceso denegado.")
                    return False
            else:
                print("Usuario no encontrado.")
    except Error as e:
        print("Error al conectar a MariaDB", e)
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    return False




