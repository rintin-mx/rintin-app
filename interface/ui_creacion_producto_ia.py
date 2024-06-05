import sys
sys.path.append('..')
import streamlit as st
from openai import OpenAI
import csv
import pandas as pd
import base64
from db.db_creacion_productos_ia import get_urls
from integration.gpt_prompt import messages, client


def create_download_link(val, filename):
    # Generate a link to download the csv

    # Parameters:
    # val: csv encoded
    # filename: string with csv file nanme

    # Returns:
    # A hyperlink with to download the file

    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.csv">Descargar CSV</a>'

def send_prompt():
    """
    Función que toma el prompt, las imágenes y la versión de GPT para hacer la petición

    Inputs: Ninguna
    Outputs: Completition (Combinación de prompt y versión para enviar a la API de GPT en el formato correcto para recibir su respuesta)
    """
    chat_completion = client.chat.completions.create(
        messages = messages,
        model="gpt-4o"
    )
    return chat_completion

def ingreso_imagenes():
    """
    Función que permite al usuario ingresar URL's de productos para que GPT las analice

    Inputs: Ninguno
    Outputs: csv conteniendo características importantes de cada producto enviado
    """

    st.title("Ingreso de Imágenes")

    date = st.date_input("Selecciona un día para consultar las imágenes cargadas en la fecha")

    img_list = get_urls(date)

    day_off = False
    if img_list.empty:
        st.warning("Este día no se subieron imágenes, por favor escoge otro.")
        img_list.loc[0, 'url'] = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"
        day_off = True

    images = []
    urls = []

    st.divider()

    for i in range(len(img_list['url'])):

        col1, col2 = st.columns([4, 6])

        with col1:
            st.image(img_list.loc[i, 'url'], use_column_width=True)
        with col2:
            
            if not day_off:
                listed = st.checkbox("Crear información para este producto.", key=f"checkbox{i}")
            else:
                listed = False

            if listed:
                urls.append(img_list.loc[i, 'url'])
                images.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_list.loc[i, 'url'],
                        },
                    },
                )

    if len(images) <= 30 and not day_off:

        if st.button("Avanzar"):

            with st.spinner(f'Generando propiedades'):

                for i in range(len(images)):
                    messages[0]["content"].append(images[i])

                response = send_prompt()
                reply = response.choices[0].message.content
                rows = reply.splitlines()

                with open('creation_file.csv', 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for i in range (len(rows)):
                        if i != 0 and i != len(rows)-1:
                            splitted_row = rows[i].split(',')
                            writer.writerow(splitted_row)

            st.session_state['current_view'] = 'revision_de_informacion'
            st.session_state['creacion_productos_urls'] = urls
            st.rerun()

    else:
        if not day_off:
            st.warning("Estas añadiendo más de 30 productos para generar información, por favor no excedas los 30 productos")

def revision_info(urls):

    """
    Función que permite al usuario descargar el csv generado para la creación de productos

    Inputs: urls (lista de urls de las fotos que envió previamente)
    Outputs: Link de descarga del csv que contiene las propiedades de los productos
    """

    answer_data = pd.read_csv("creation_file.csv")
    answer_data["Foto"] = urls
    answer_data.to_csv("creation_file.csv", index = False)

    st.title("Revisión de información.")
    st.write("##")

    if st.button("Descargar información"):

        with open('creation_file.csv', 'r') as file:
            csv_content = file.read().encode()
            html = create_download_link(csv_content, 'Archivo de creación de productos')
            st.markdown(html, unsafe_allow_html=True)

    if st.button("Volver"):
        st.session_state['current_view'] = 'creacion_producto_ia'
        st.rerun()