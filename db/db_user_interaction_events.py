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



def event_instert(EventName, EventAction, EventUser, EventDetail=None):
    db = 'prod'
    config = config_db(db)
    start_time = time.time()
    
    # Convertir EventDetail a str si no es None
    if EventDetail is not None:
        EventDetail = str(EventDetail)

    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # Consulta SQL para insertar datos
            insert_query = """
            INSERT INTO UserInteractionEvents (EventName, EventAction, EventUser, EventDetail) 
            VALUES (%s, %s, %s, %s)
            """
            # Datos a insertar
            event_data = (EventName, EventAction, EventUser, EventDetail)
            # Ejecutar la consulta
            cursor.execute(insert_query, event_data)
            # Asegurar los cambios en la base de datos
            connection.commit()
            print("Evento insertado correctamente")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

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

            


    finally:
        # Cerrar la conexión y el cursor
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_session(user_id):
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

                # Sentencia SQL para obtener la sesión del usuario
            sql = "SELECT * FROM UserSessions WHERE UserID = %s"

            # Ejecutar la consulta
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()

            return result


    finally:
        # Cerrar la conexión y el cursor
        if connection.is_connected():
            cursor.close()
            connection.close()
