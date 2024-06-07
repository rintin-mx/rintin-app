import sys
sys.path.append('..')
import streamlit as st
from openai import OpenAI
import pandas as pd
import base64
from db.db_creacion_productos_ia import get_urls
from integration.gpt_prompt import client


pd.set_option('display.max_columns', None)

def create_download_link(val, filename):
    # Generate a link to download the csv

    # Parameters:
    # val: csv encoded
    # filename: string with csv file nanme

    # Returns:
    # A hyperlink with to download the file

    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.csv">Descargar CSV</a>'

def send_prompt(new_message):
    """
    Función que toma el prompt, las imágenes y la versión de GPT para hacer la petición

    Inputs: Ninguna
    Outputs: Completition (Combinación de prompt y versión para enviar a la API de GPT en el formato correcto para recibir su respuesta)
    """
    try:
        chat_completion = client.chat.completions.create(
            messages = new_message,
            model="gpt-4o"
        )

    except Exception as e:
        print(e)
        chat_completion = False

    return chat_completion

def ingreso_imagenes():
    """
    Función que permite al usuario ingresar URL's de productos para que GPT las analice

    Inputs: Ninguno
    Outputs: csv conteniendo características importantes de cada producto enviado
    """

    prompt_messages=[
        {
            "role": "user",
            "content": [
                {"type": "text",
                "text": """
                    Extrae de los productos en las imágenes: 
                    codigo_de_producto (si no se encuentra, dejar vacío), 
                    Categoria_padre (Hombre, mujer, niño/niña, unisex, productos varios),
                    Categoria_hijo (Ropa, calzado, Maquillaje, Bolsas/Mochilas/carteras, accesorios, escolar/profesional, papeleria),
                    Subcategoria_1 (Ropa Interior,Pantalones,Pantuflas,Sandalias,Tenis,Carteras,Jeans,Chalecos,Bolsas,Pijamas,Vestidos,Blusas,Ropa Deportiva,Sueters,Chamarras,Conjuntos,Playeras,Pants,Leggings,Sudaderas,Gorras/Viseras/Sombreros,Faldas,Shorts,Calcetines/calceteria,Bermudas,Ponchos/Capas/Kimonos,Camisas,Ropa de Maternidad,Trajes de Baño,Tops,Botas y Botines,Palazzo,Impermeables,Jumpsuit,Mangas,Lenceria,Mochilas,Joggers,Bufanda,Saco),
                    Subcategoria_2 (Tenis Casual,Corte Skinny,Corte Acampanado,Tenis Deportivo,Mochilas,Chamarra Mezclilla,Corte Wide Leg,Corte Mom,Pijamas,Ropa térmica,Corte Colombiano,Conjunto,Crop Top,Leggings,Boxers,Cacheteros,Brasier,Pantaletas,Falda,Short,Protectores,Corte Vaquero,Baby Dalls,Faja,Overol,Tops,Corte Cargo,Corte Recto,Corte Stretch,Tanga,Bikini,Calcetines tobillo,Trusa,Medias,Calcetines Altos,Calcetines cortos,Camiseta,Corset,Calcetines Medios,Bolsa Formal,Body,Corte Extra Skinny,Corte Slim Fit,Corte Regular Fit,Licras,Top niña,Talla Extra,Chaleco Mezclilla,Vestidos largos,Vestidos cortos),
                    Subcategoria_3 (Escoge entre estas opciones o deja vacío: Algodón, Encaje, Microfibra, Sin costura),
                    Tipo_de_producto (Escoge entre estas opciones o deja vacío: Linea continua, Promocion, Novedad),
                    Nombre_de_producto (Si existe uno en la imágen colócalo, sino, creea un nombre como lo haría un experto en ecomerce Mexicano en no más de 5 palabras),
                    Venta_por_unidad_o_paquete (escribir paquete si es por paquete y unidad si se vende por unidad),
                    Tipo_de_unidad (Kit, Piezas, Paquetes),
                    Unidades_por_paquete (si lo incluye la imagen, sino dejar vacío),
                    Marca (Si no aparece marca, dejar en blanco),
                    Material_composicion_y_porcentajes (Si aparece en la imagen información de la composición del producto, sino dejar vacío),
                    Importado_o_hecho_en_mexico (Coloca "Importado" o "Hecho en méxico"),
                    Colores_presentes_en_producto (varios colores (escribe los colores que identifiques SIN USAR COMAS PARA SEPARARLOS. SEPARALOS CON GUIONES), un color),
                    Tallas (Si se muestra en la imagen, sino dejar vacío),
                    Observaciones (Coloca observaciones que te parezcan relevantes del producto en no más de 20 palabras)

                    responde únicamente colocando esta información en un csv en formato tabla donde cada línea representa 1 producto o 1 imagen que ha sido enviada junto con este mensaje y no coloques tíldes en la información de respuesta. A demás, MUY MUY MUY IMPORTANTE si vas a hacer un listado, SEPARA LOS ELEMENTOS DE LAS LISTAS POR GUIONES, NUNCA POR COMAS. Por último, no te saltes campos. Si no tienes respuesta para un campo, dejalo vacío pero NO TE SALTES NINGUN CAMPO.
                    """
                },
            ],
        }
    ]

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
                    prompt_messages[0]["content"].append(images[i])

                response = send_prompt(prompt_messages)

                if response == False:
                    st.error("Error de envío de imágenes. Escoja menos imágenes a enviar para reducir la carga.")
                else:
                    
                    reply = response.choices[0].message.content
                    rows = reply.splitlines()[1:-1]
                    labels = rows[0].split(",")
                    df = pd.DataFrame(columns = labels)
                    for i in range(len(rows) - 1):
                        splitted_line = rows[i+1].split(",")
                        if len(splitted_line) < len(labels):
                            diff = len(labels) - len(splitted_line)
                            for j in range(diff):
                                splitted_line.append("")

                        if len(splitted_line) > len(labels):
                            splitted_line = splitted_line[0:len(labels)]

                        temporal_df = pd.DataFrame([splitted_line], columns = labels)
                        df = pd.concat([df, temporal_df], ignore_index=True)
                        
                    st.session_state['response_df'] = df
                    st.session_state['current_view'] = 'revision_de_informacion'
                    st.session_state['creacion_productos_urls'] = urls
                    st.rerun()
            
    else:
        if not day_off:
            st.warning("Estas añadiendo más de 30 productos para generar información, por favor no excedas los 30 productos")

def revision_info(urls, df):

    """
    Función que permite al usuario descargar el csv generado para la creación de productos

    Inputs: urls (lista de urls de las fotos que envió previamente)
    Outputs: Link de descarga del csv que contiene las propiedades de los productos
    """

    answer_data = df

    #print(answer_data)

    st.title("Revisión de información.")
    st.write("##")

    st.write(f"Imágenes adjuntadas: {len(urls)}")
    st.write(f"Descripciones recibidas: {len(answer_data['Categoria_padre'])}")

    if len(urls) > len(answer_data['Categoria_padre']):
        urls = urls[0:len(answer_data['Categoria_padre'])]
        st.warning("Considerar que pueden faltar descripciones de imágenes adjuntas debido a que la IA puede cometer errores.")

    if len(urls) < len(answer_data['Categoria_padre']):
        diff = len(answer_data['Categoria_padre']) - len(urls)
        st.warning("Considerar que pueden faltar descripciones de imágenes adjuntas debido a que la IA puede cometer errores.")
        for i in range(diff):
            urls.append("")

    answer_data["Foto"] = urls

    answer_data.to_csv("creation_file.csv", index = False)

    if st.button("Descargar información"):

        with open('creation_file.csv', 'r') as file:
            csv_content = file.read().encode()
            html = create_download_link(csv_content, 'Archivo de creación de productos')
            st.markdown(html, unsafe_allow_html=True)

    if st.button("Volver"):
        if 'creacion_productos_urls' in st.session_state:
            del st.session_state['creacion_productos_urls']
        if 'response_df' in st.session_state:
            del st.session_state['response_df']
        
        st.session_state['current_view'] = 'creacion_producto_ia'
        st.rerun()