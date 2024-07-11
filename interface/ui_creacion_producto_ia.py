import sys
sys.path.append('..')
import streamlit as st
from openai import OpenAI
import pandas as pd
import base64
from db.db_creacion_productos_ia import get_urls


pd.set_option('display.max_columns', None)

key = "sk-proj-Tw1KNpopjJ5E9hxFrRtsT3BlbkFJlQIbd2Z8Jq0VExcGvMNG"

client = OpenAI(api_key=key)

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

        reply = chat_completion.choices[0].message.content.splitlines()
        label_index = reply.index('codigo_de_producto, Categoria_padre, Categoria_hijo, Subcategoria_1, Subcategoria_2, Subcategoria_3, Tipo_de_producto, Nombre_de_producto, Venta_por_unidad_o_paquete, Tipo_de_unidad, Unidades_por_paquete, Marca, Material_composicion_y_porcentajes, Importado_o_hecho_en_mexico, Colores_presentes_en_producto, Tallas, Observaciones')

        # Caso respuesta de GPT no tiene la fila de labels
        if label_index == -1:
            return "no_labels"
        
        # Caso respuesta de GPT no tiene la fila de descripción del producto
        if len(reply) - 1 < label_index + 1:
            return "empty_description"
        
        return reply[label_index:label_index+2]

    except Exception as e:

        # Caso GPT responde con error por exceso de TOKENS
        print(e)
        return False

    
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
                    Tarea: Siendo una persona mexicana experta en la industria de la moda que vende sus productos por mayoreo por medio de un ecommerce y orientado a un cliente de clase media y baja, extraer información de las imágenes de los productos y organizarla en un formato de tabla CSV.
                    Información a Extraer de la imagen:
                    codigo_de_producto: Si se encuentra, de lo contrario dejar en blanco.
                    Categoria_padre: (Elige uno: Hombre, mujer, niño/niña, unisex, productos varios, Duos).
                    Categoria_hijo: (Dependiendo de la eleccion en Categoria_padre, si escogiste Hombre: Calzado, Bolsas Mochilas y Carteras, Ropa; Mujer: Calzado, Ropa, Bolsas Mochilas y Carteras, Maquillaje; niño/niña: Bolsas Mochilas y Carteras, Calzado, Ropa; Productos Varios: Escolar/Profesional, Accesorios, Papeleria, Paraguas; unisex: Bolsas Mochilas y Carteras, Gorras Viceras y Sombreros, Accesorios; Duos: Ropa. Si no hay una categoría que se ajuste dentro de las opciones en la eleccion de categoria_padre, dejar en blanco).
                    Subcategoria_1: (Dependiendo de la eleccion en Categoria_hijo, si escogiste Accesorio: Mangas; Bolsas, Mochilas y Carteras: Cangurera, Carteras, Mariconeras, Bolsas, Mochilas, Lonchera, Lapicera; Calzado: Botas y Botines, Pantuflas, Sandalias, Tenis, Alpargatas, Flats / Valerinas; Bermudas, Blusas, Bufanda, Calcentines y Calceteria, Camisas, Camison, Chalecos, Chamarras, Conjuntos, Faldas, Gorras Viseras y Sombreros, Impermeables, Jeans, Joggers, Jumpsuit, Leggings, Lenceria, Mangas, Palazzo, Pantalones, Pants, Pijamas, Playeras, Ponchos Capas y Batas, Ropa de Maternidad, Ropa Deportiva, Ropa Escolar, Ropa Interior, Sacos, Shorts, Sudaderas, Sueteres, Tallas Extra, Trajes de Baño, Vestidos y Palazzos, Vestidos. Si no hay una categoría que se ajuste dentro de las opciones en la eleccion de categoria_hijo, dejar en blanco).
                    Subcategoria_2: (Dependiendo de la eleccion en Subcategoria_1, si escogiste Blusas: Body, Corset, Crop Top, Tops, Bluson; Calcentines y Calceteria: Calceta, Calcetines Altos, Calcetines Cortos, Calcetines Medios, Calcetines Tobillo, Medias, Protectores; Jeans: Short, Chaleco Mezclilla, Corte Colombiano, Corte Mom, Talla Extra, Overol, Corte Acampanado, Vestidos Cortos, Faldas, Chamarra Mezclilla, Corte Skinny, Corte Slim Fit, Corte Extra Skinny, Corte Regular Fit, Cargo, Corte Recto; Pantalones: Cargo, Acampanado; Ropa Deportiva: Licras, Tops, Conjunto, Short; Vestidos: Vestidos Cortos, Vestidos Largos; Ropa Interior: Bikini, Boxers, Brasier, Cachetero, Conjuntos, Faja, Pantaletas, Tanga, Top, Top Niña, Trusa. Si no hay una categoría que se ajuste dentro de las opciones en la eleccion de subcategoria_1, dejar en blanco).
                    Subcategoria_3: (Dependiendo de la eleccion en Subcategoria_2, si escogiste Bikini: Algodon, Microfibra, Sin Costura, Encaje; Boxers: Algodon, Microfibra, Sin Costura, Encaje; Cachetero: Sin Costura, Encaje; Pantaletas: Algodon, Microfibra, Sin Costura, Encaje; Tanga: Algodon, Microfibra, Sin Costura, Encaje; Top: Algodon, Microfibra, Sin Costura, Encaje; Trusa: Algodon, Microfibra. Si no hay una categoría que se ajuste dentro de las opciones en la eleccion de subcategoria_2, dejar en blanco)
                    Tipo_de_producto: (Elige de: Linea continua-Promocion-Novedad) o deja en blanco.
                    Nombre_de_producto: Si se encuentra en la imagen, de lo contrario crea un nombre como experto en comercio electrónico mexicano en no más de 5 palabras.
                    Venta_por_unidad_o_paquete: (Elige uno: paquete-unidad).
                    Tipo_de_unidad: (Elige uno: Kit-Piezas-Paquetes).
                    Unidades_por_paquete: Si se indica en la imagen, de lo contrario dejar en blanco.
                    Marca: Si no está presente, dejar en blanco.
                    Material_composicion_y_porcentajes: Si se indica en la imagen, dejar en blanco.
                    Importado_o_hecho_en_mexico: (Elige uno: Importado-Hecho en mexico).
                    Colores_presentes_en_producto: (Elige uno: varios colores (lista colores sin comas)-un color).
                    Tallas: Si se indica en la imagen, dejar en blanco.
                    Observaciones: Anota cualquier observación relevante del producto en no más de 20 palabras.
                    Formato de documento csv:
                    Responde organizando la información extraída en un formato de tabla CSV.
                    Cada línea debe representar un producto o una imagen.
                    No incluyas tildes en la respuesta.
                    Si enumeras elementos, sepáralos con guiones, no comas.
                    No omitas ningún campo; deja en blanco si no hay información disponible.
                    Ejemplo:
                    codigo_de_producto, Categoria_padre, Categoria_hijo, Subcategoria_1, Subcategoria_2, Subcategoria_3, Tipo_de_producto, Nombre_de_producto, Venta_por_unidad_o_paquete, Tipo_de_unidad, Unidades_por_paquete, Marca, Material_composicion_y_porcentajes, Importado_o_hecho_en_mexico, Colores_presentes_en_producto, Tallas, Observaciones
                    12345, mujer, Ropa, Blusas, Corte Slim Fit, Algodon, Novedad, Blusa elegante, unidad, Piezas, 1, Zara, Algodon 100%, Importado, varios colores rojo-azul-verde, M-L, Sin observaciones
                    Instrucciones: Usa este formato para extraer y organizar la información de cada imagen de producto proporcionada.
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

    next_button = st.button("Avanzar")
    placeholder = st.empty()
    next_spinner = st.spinner("Generando propiedades")

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

        if next_button:

            with placeholder, next_spinner:
                
                labels = ["codigo_de_producto", "Categoria_padre", "Categoria_hijo", "Subcategoria_1", "Subcategoria_2", "Subcategoria_3", "Tipo_de_producto", "Nombre_de_producto",
                          "Venta_por_unidad_o_paquete", "Tipo_de_unidad", "Unidades_por_paquete", "Marca", "Material_composicion_y_porcentajes", "Importado_o_hecho_en_mexico",
                          "Colores_presentes_en_producto", "Tallas", "Observaciones", "Foto"]
                df = pd.DataFrame(columns = labels)

                for i in range(len(images)):
                    prompt_messages[0]["content"].append(images[i])

                    response = send_prompt(prompt_messages)

                    if response == "empty_description" or response == "no_labels" or response == False:
                        row = []
                        for j in range(len(labels) - 1):
                            row.append("")
                        
                        row.append(urls[i])
                        temporal_df = pd.DataFrame([row], columns = labels)
                        df = pd.concat([df, temporal_df], ignore_index=True)
                    else:
                        rows = response

                        splitted_line = rows[1].split(",")
                        splitted_line.append(urls[i])

                        if len(splitted_line) < len(labels):
                            diff = len(labels) - len(splitted_line)
                            for k in range(diff):
                                splitted_line.append("")

                        if len(splitted_line) > len(labels):
                            splitted_line = splitted_line[0:len(labels)]

                        temporal_df = pd.DataFrame([splitted_line], columns = labels)
                        df = pd.concat([df, temporal_df], ignore_index=True)
                        
                    prompt_messages[0]["content"].pop(1)

                else:
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

    st.title("Revisión de información.")
    st.write("##")

    st.write(f"Imágenes adjuntadas: {len(urls)}")

    for i in range(len(answer_data["Foto"])):
        if answer_data.loc[i, "Foto"][:8] != 'https://':
            answer_data.loc[i, "Foto"] = urls[i]

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
        if 'overload' in st.session_state:
            del st.session_state['overload']
        
        st.session_state['current_view'] = 'creacion_producto_ia'
        st.rerun()