import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
import pandas as pd

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

def get_urls(date, db='repl'):

    # Get a list of urls to be searched in the UI

    # Parameters:
    # lenght: number of images to return

    # Returns:
    # Dataframe: a dataframe containing the query results 
    #             (post_title, post_name, url)

    
    config = config_db(db)
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        image_urls = f"""
            select
                CASE
                    WHEN guid LIKE '%rintin.mx/uploads/%' 
                    THEN REPLACE(guid, 'rintin.mx/uploads/', 'rintin.mx/wp-content/uploads/')
                    ELSE guid
                END as url
            from
                wp_posts
            where
                post_type = 'attachment'
                and post_mime_type like '%image%'
                and date(post_date) = '{date}'
            order by
                post_date desc
        """
        
        # Ejecutar la primera consulta
        cursor.execute(image_urls)

        # Obtener los resultados de la primera consulta
        resultados_image_urls = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        image_urls = pd.DataFrame(resultados_image_urls)

    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close() 
        # Nueva lista de nombres de columnas
        return image_urls