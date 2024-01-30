# db/script_db.py
import sys
sys.path.append('..')
import streamlit as st
from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
from mysql.connector import Error
import time
import datetime
import json



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


def event_instert(EventName,EventAction,EventUser,EventDetail=''):
    db = 'prod'
    datos_json_str=''
    if EventDetail != '': 
        print('EventDetail')
        print(EventDetail)
        datos_json_str = json.dumps(EventDetail)

    config = config_db(db)
    start_time = time.time()
    connection = mysql.connector.connect(**config)
    try:
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            insert_query = """
            INSERT INTO wordpress.UserInteractionEvents  (EventName, EventAction, EventUser,EventDetail) 
            VALUES (%s, %s, %s,%s)
            """
            # Datos a insertar
            event_data = (EventName, EventAction, EventUser,datos_json_str)
            # Ejecutar la consulta
            cursor.execute(insert_query, event_data)
            # Asegurar los cambios en la base de datos
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


def upsert_user_session(user_id, is_logged_in,db):
    config = config_db(db)
    start_time = time.time()
    if login_timestamp is None:
        login_timestamp = datetime.datetime.now()
    if logout_timestamp is None:
        logout_timestamp = datetime.datetime.now()
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Consulta SQL para insertar datos
            sql = """
            INSERT INTO UserSessions (UserID, IsLoggedIn, LoginTimestamp, LogoutTimestamp)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            IsLoggedIn = VALUES(IsLoggedIn),
            LoginTimestamp = VALUES(LoginTimestamp),
            LogoutTimestamp = VALUES(LogoutTimestamp)
            """

            # Ejecutar la sentencia SQL
            cursor.execute(sql, (user_id, is_logged_in, login_timestamp, logout_timestamp))
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

def get_user_session(user_id):
    config = config_db()
    start_time = time.time()
    if login_timestamp is None:
        login_timestamp = datetime.datetime.now()
    if logout_timestamp is None:
        logout_timestamp = datetime.datetime.now()
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

                # Sentencia SQL para obtener la sesión del usuario
            sql = "SELECT * FROM UserSessions WHERE UserID = %s"

            # Ejecutar la consulta
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            return result

    except Error as e:
        print("Error al conectar a la base de datos:", e)

    finally:
        # Cerrar la conexión y el cursor
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")