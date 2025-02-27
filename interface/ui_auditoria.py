import sys
import re
sys.path.append('..')
from typing import List
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productos_validados import insert_productos_validados
from db.db_user_interaction_events import event_instert
from datetime import datetime
from streamlit_searchbox import st_searchbox
from db.db_auditoria import  get_product_changes, insert_producto_problema, guardar_productos_extra, get_wa_group_id
from st_mui_table import st_mui_table
from fpdf import FPDF
import base64
from integration.endpoint_whapi import send_post_request_to_api


noAuditoriaOpt = ['No llego', 'Defectuoso']

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

async def update_order_note__wordpress(order_id, order_notes):
    result = await endpoint_write_order_note(order_id, order_notes)
    return result

def ver_detalle(order_id,seller_id,seller_name,num_paquetes,estado):
    #'order_id','seller_id','seller_name', 'num_paquetes','estado'
    st.session_state.orderId = order_id
    st.session_state.sellerid = seller_id
    st.session_state.nombreSeller = seller_name
    st.session_state.estadoPedido = estado
    st.session_state.num_paquetes =num_paquetes
    st.session_state.current_view = 'detalleAuditoria'
    st.session_state['estadoUITP']=True
    st.session_state.disabled = True
    st.rerun()

def orderMsjString(objeto, status):
    linea=''
    ahora = datetime.now()
    fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
    fuente='auditoria'
    insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'],fuente,st.session_state.useremail, 'wc-auditoria-2', 'wc-' + status, objeto['razon'])
    linea = f"Producto: {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe audito {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}\nRazón de diferencia: {objeto['razon']}"
    return linea

def UIDetallePedido(data_deta,data_issues,idPedido):
    st.subheader(f"Detalle de la orden: {idPedido}")
    if st.button("Regresar la lista de auditoría"):
            st.session_state.current_view = 'auditoria'
            st.rerun()

    if data_issues and len(data_issues.get('ID', [])) > 0:
        st.warning("⚠️ Esta orden pasó por recolección con problemas. Antes de auditar, debes juntarlo con el resto del pedido.")

        # 🔹 Convertimos el diccionario de listas en una lista de diccionarios
        data_issues_list = [dict(zip(data_issues.keys(), values)) for values in zip(*data_issues.values())]

        for index, issue in enumerate(data_issues_list):
            mensaje = (f"ℹ️ **Problema de recolección #{index+1}:**\n"
                       f"📦 **Producto:** {issue['Producto']}\n"
                       f"🔢 **SKU:** {issue['SKU']}\n"
                       f"❌ **Piezas Faltantes:** {issue['Piezas Faltantes']}\n"
                       f"🔍 **Incidencia:** {issue['Incidencia']}\n"
                       f"📅 **Fecha:** {issue['Creado']}")
            st.info(mensaje)


    #estilos en los textos
    st.write("---")
    # Inicializar una lista para los estados
    estados = []
    cantidad_pickeada =0
    bodega = data_deta['bodega'][0]
    
    if bodega == 'centro_cdmx':
        banner_text = 'Recolectar'
        banner_status = 'recolectar-2'
    else:
        banner_text = 'Recolección con problemas'
        banner_status = 'rec-problem-2'
    df = pd.DataFrame(data_deta)
    objArry=[]

    # agrupa los order_item_id de los productos
    order_item_ids = ''
    for id in df["order_item_id"]:
        order_item_ids += f"{id}, "
    order_item_ids = order_item_ids[:-2]

    # obtiene la lista de los productos con reemplazo
    changed_list = get_product_changes(order_item_ids)

    sellerId = 0
    for i, pedido in df.iterrows():
        sellerId = pedido.seller_id
        #col1, col2, col3, col4, col5 = st.columns(5)
        has_substitute = False
        substitute = ''
        for prod in changed_list.iterrows():
            if(prod[1].order_item_id == pedido.order_item_id):
                has_substitute = True
                substitute = prod[1].nuevo_producto_sku

        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 3])
        with col1:
            if pedido.Imagen is not  None:
                st.image(pedido.Imagen, use_column_width=True )
            else:
                st.write("Sin imagen")

        with col2:
            st.markdown(f'##### Nombre: {pedido.Producto}')
            st.markdown(f'##### SKU: {pedido.SKU}')
            st.markdown(f'##### Unidades: {pedido.units_per_pack}')            
        with col3:
            st.markdown(f'##### Cantidad: {pedido.Cantidad}')
            if has_substitute:
                st.warning(f'##### SKU de reemplazo: {substitute}')
            
            st.write("")  # Espacio extra

        with col4:
            cantidad_pickeada = st.number_input(f"Auditado", key=f"cantidad_{i}", value=0,min_value=0, max_value=int(pedido.Cantidad))
            faltan_piezas = st.checkbox(
                "Faltan piezas", 
                key=f"faltan_piezas_{i}"
            )
            piezas_faltantes = 0
            if faltan_piezas:
                piezas_faltantes = st.number_input(
                    "Ingrese piezas faltantes", 
                    key=f"piezas_faltantes_{i}", 
                    value=0, 
                    min_value=0, 
                    max_value=10,
                    placeholder="Ingrese piezas faltantes"
                )
        with col5:
            if faltan_piezas:
                estado = 'NO OK'
                st.error('Faltan piezas - NO OK')
            elif cantidad_pickeada == int(pedido.Cantidad):
                estado = 'OK'
                st.success(estado)
            elif cantidad_pickeada > int(pedido.Cantidad):
                st.error('Cantidad excedida')
                estado = 'NO OK'
            else:
                estado = 'NO OK'
                st.error(estado)

            defectuoso = ''
            razon = None

            # Mostrar "Razón no auditoría" solo si:
            # - La cantidad pickeada es menor a la cantidad pedida
            # - NO se ha marcado "Faltan piezas" mientras la cantidad pickeada es completa
            if cantidad_pickeada < int(pedido.Cantidad) or (faltan_piezas and cantidad_pickeada < int(pedido.Cantidad)):
                razon = st.selectbox(
                    'Razón no auditoría', 
                    options=noAuditoriaOpt, 
                    key=f"razon_{pedido.product_id}"
                )
                if razon == 'Defectuoso':
                    defectuoso = st.text_input('Describa defecto', key=f"defecto_{pedido.product_id}")


        estados.append(estado)
        objArry.append({"order_id":pedido.order_id,
                        "nombre_producto":pedido.Producto,
                        "producto_id":pedido.product_id,
                        "sku":pedido.SKU,
                        "cantidad_sistema":int(pedido.Cantidad),
                        "cantidad_nueva":cantidad_pickeada,
                        "estado":estado,
                        "seller_id":pedido.seller_id,
                        "razon": razon, 
                        "defectuoso": defectuoso,
                        "faltan_piezas": faltan_piezas,
                        "piezas_faltantes": piezas_faltantes,
                        "pedido": pedido
                        })
        st.write('---')

    
    

    
    
    # Inicializar lista de productos extra en session_state
    if "extra_productos" not in st.session_state:
        st.session_state["extra_productos"] = []

    st.write("### ⚠️ Llegó producto extra")

    # Botón para agregar un nuevo producto extra
    if st.button("➕ Agregar nuevo producto extra"):
        st.session_state["extra_productos"].append({
            "id": len(st.session_state["extra_productos"]) + 1,  # ID único
            "codigo_extra_producto": "",
            "unidad_extra_producto": "Unidad",
            "cantidad_extra_producto": 1
        })

    # Mostrar inputs dinámicos para cada producto extra agregado
    productos_a_eliminar = []
    for idx, producto in enumerate(st.session_state["extra_productos"]):
        with st.container():  # Contenedor para cada producto
            st.write(f"### Producto Extra #{idx + 1}")

            col1, col2, col3, col4 = st.columns([3, 3, 2, 1])

            with col1:
                codigo = st.text_input(
                    "Código del producto extra",
                    value=producto["codigo_extra_producto"],  # Usamos value en lugar de modificar session_state
                    key=f"codigo_extra_producto_{idx}"
                )

            with col2:
                unidad = st.selectbox(
                    "Tipo de unidad",
                    ["Unidad", "Caja", "Paquete"],
                    index=["Unidad", "Caja", "Paquete"].index(producto["unidad_extra_producto"]),
                    key=f"unidad_extra_producto_{idx}"
                )

            with col3:
                cantidad = st.number_input(
                    "Cantidad",
                    min_value=1,
                    value=producto["cantidad_extra_producto"],
                    key=f"cantidad_extra_producto_{idx}"
                )

            with col4:
                if st.button("🗑️", key=f"eliminar_{idx}"):
                    productos_a_eliminar.append(idx)

        # Guardar cambios en el objeto después de que los widgets actualizan los valores
        producto["codigo_extra_producto"] = codigo
        producto["unidad_extra_producto"] = unidad
        producto["cantidad_extra_producto"] = cantidad

    # Eliminar productos extra marcados
    if productos_a_eliminar:
        st.session_state["extra_productos"] = [
            prod for i, prod in enumerate(st.session_state["extra_productos"]) if i not in productos_a_eliminar
        ]
        st.experimental_rerun()  # Recargar la interfaz para reflejar los cambios




    agrupacion=[]
    recolec=[]
    for i in range(len(objArry)):
        if objArry[i]['estado'] =='OK':
            agrupacion.append(objArry[i]['order_id'])
        else:
            recolec.append(objArry[i]['order_id'])
    trigger_btn = ui.button(text="Auditar", key="trigger_btn")
    respuesta = False
    if len(agrupacion)==len(objArry):
        banner_text = 'Pedidos por agrupar'
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Bodega y Auditoría", description=f'Enviaremos el pedido #{str(idPedido)} a "{banner_text}"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner(f'Actualizando estado del pedido a "Pedidos por agrupar"'):
                if st.session_state.useremail is not None:
                    EventName,EventAction,EventUser='auditoria','Se envio el pedido a "Pedidos agrupar"',st.session_state.useremail
                    event_instert(EventName,EventAction,EventUser, idPedido)
                
                banner_status='auditoria-2'
                r = asyncio.run(update_status_wordpress(idPedido, banner_status))

                asyncio.run(update_order_note__wordpress(idPedido, "Pedido confirmado en bodega por Auditoria"))
                
                banner_status='agrupar-pedidos'
                r = asyncio.run(update_status_wordpress(idPedido, banner_status))
            st.session_state.current_view = 'finalProceso'
            st.session_state.current_status = banner_text
            st.rerun()
           
    else:
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Auditoría", description=f'Enviaremos el pedido #{idPedido} a "{banner_text}"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order_2")
        if respuesta:
            with st.spinner(f'Actualizando estado del pedido a "{banner_text}"'):
                lineasProblemas = []
                i=0
                for objeto in objArry:
                    if objeto['estado'] == 'NO OK':
                        #lineasProblemas.append(orderMsjString(objeto, banner_status))
                        insert_producto_problema(objeto)
                        wa_group_id = get_wa_group_id(sellerId)
                        mensaje_seller = generar_mensaje_seller(objeto)
                        if wa_group_id is not 0:
                            send_post_request_to_api(wa_group_id,mensaje_seller)
                        asyncio.run(update_order_note__wordpress(idPedido,  generar_mensaje_wordpress(objeto)))

                #if len(lineasProblemas) > 0:
                #    order_notes = "\n".join(lineasProblemas)
                #    with st.spinner(f'Actualizano las notas del pedido para auditoria  en las bodegas CDMX'):
                #        asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                # OJO QUITAR
                r = asyncio.run(update_status_wordpress(idPedido, banner_status))

                if not st.session_state["extra_productos"]:
                    st.error("⚠️ No hay productos extra para guardar.")
                else:
                    guardar_productos_extra(st.session_state["extra_productos"], idPedido, sellerId)
                    st.session_state["extra_productos"] = []  # Limpiar después de guardar
                
                if st.session_state.useremail is not None:
                    EventName,EventAction,EventUser='auditoria','Se envio el pedido a "Pedidos agrupar"',st.session_state.useremail
                    event_instert(EventName,EventAction,EventUser, idPedido)
            st.session_state.current_view = 'finalProceso'
            st.session_state.current_status = banner_text
            st.rerun()

def truncar_texto(texto, max_long=30, sufijo="..."):
    """Trunca texto si excede max_long y le agrega sufijo."""
    if len(texto) > max_long:
        return texto[:max_long - len(sufijo)] + sufijo
    return texto

def UITFinalizarProceso(data, currentStatus):
    grouped = data['num_agrupados'][0]
    childs = data['childs'][0]
    
    order_date = data['post_date'][0]
    customer_name = data['name'][0]

    if childs == grouped and childs == 1:
        text = 'Es pedido único, ahora debes imprimir bitácora y empaquetar'
        
    elif childs == grouped and childs > 1:
        text = 'Es el último pedido, ahora debes Agrupar y Empaquetar'
    elif grouped < childs and grouped > 0 and grouped != 1:
        text = 'Este pedido ya tiene órdenes en agrupar, ahora debes Agruparlo'
    else:
        text = 'Este es el primer pedido, ahora debes imprimir bitácora y abrir espacio para orden completa'

    st.markdown(f'## Se actualizó el pedido con número {data["id"][0]} al estado "{currentStatus}"')
    st.write('---')

    if currentStatus == 'Pedidos por agrupar':
        st.markdown(f'### {text}')
        
        # 🔹 Mostrar el botón solo si el texto contiene "imprimir"
        if "imprimir" in text.lower():
            if st.button('Generar PDF'):
                # Crear el PDF con el tamaño personalizado (102mm x 152mm)
                # Crear el PDF con tamaño 102mm x 152mm (ancho x alto)
                pdf = FPDF(orientation='L', unit='mm', format=(102, 152))  
                pdf.set_margins(5, 5, 5)
                pdf.add_page()

                # 2. (Opcional) Logo en la parte superior izquierda
                #    Si necesitas que aparezca, ajusta x, y, w, h
                pdf.image("imagen/rintin_logo.png", x=5, y=5, w=40, h=20)

                # 3. "Pedido" en la mitad superior, centrado y grande
                pdf.set_font("Arial", "B", 130)
                pdf.set_text_color(255, 0, 0)  # Texto en rojo para destacar
                # Mover la posición vertical (en este ejemplo cerca del centro superior)
                pdf.set_y(35)  
                # Ancho 0 = ocupa todo el espacio horizontal
                pdf.cell(0, 15, f"{str(data['post_parent'][0])}", ln=True, align='C')
                pdf.set_text_color(0, 0, 0)    # Restaurar color de texto a negro

                # 4. En la mitad inferior, dos textos: "Fecha" a la izquierda y "Nombre" a la derecha
                pdf.ln(10)  # Salto (puedes ajustar según tu diseño)
                

                # Fecha en la primera fila, alineada a la izquierda
                pdf.set_font("Arial", "", 18)
                fecha_sin_hora = str(order_date).split(" ")[0]  
                pdf.cell(0, 10, fecha_sin_hora, border=0, ln=1, align='L')

                # Nombre en la segunda fila, alineado a la derecha
                pdf.set_font("Arial", "", 12)
                nombre_corto = truncar_texto(customer_name, max_long=50)
                pdf.cell(0, 10, nombre_corto, border=0, ln=1, align='L')

            

            
                # Generar enlace de descarga del PDF
                html = create_download_link(pdf.output(dest="S").encode("latin-1"), 
                                            f'Bitacora auditoria pedido {data["post_parent"][0]}')
                st.markdown(html, unsafe_allow_html=True)

        
    if data["post_parent"][0] != data["id"][0]:
        st.markdown(f'### Su orden padre es: {data["post_parent"][0]}')
        st.write('---')
    
    if st.button('Regresar'):
        st.session_state['current_view'] = 'auditoria'
        st.rerun()

def UITodosLosPedidos(data):
    df = pd.DataFrame(data)
    
    if len(df) > 0:
        global df_data
        df_data = []
        selected_value = ''

        if 'visible' not in st.session_state:
            st.session_state['visible'] = True
            st.rerun()
        if 'Order_id_auditoria' not in st.session_state:
            st.session_state['Order_id_auditoria'] = 0
            
        df['ID'] = df['ID'].astype(str)

        # Función de búsqueda
        def search_orderid(searchterm: str) -> List[any]:
            if not searchterm:
                return []
            df.set_index(['ID', 'Seller', 'Incidencias'], inplace=True)  # 🔹 Agregamos 'Incidencias'
            
            pattern = f"(?i){re.escape(searchterm)}"
            mask = (
                df.index.get_level_values('ID').str.match(pattern) | 
                df.index.get_level_values('Seller').str.match(pattern) |
                df.index.get_level_values('Incidencias').str.match(pattern)  # 🔹 Permite buscar por incidencias
            )
            return df[mask].index.get_level_values('ID').tolist()

        selected_value = st.text_input(label='Buscar por ID, Seller o Incidencias', key="search_input")
        submit = st.button("Buscar")
        
        # 🔹 Mostrar la tabla con los 3 campos
        st_mui_table(df)

        if submit:
            if selected_value is not None:
                st.session_state['Order_id_auditoria'] = int(selected_value)
                st.session_state['current_view'] = 'detalleAuditoria'
                st.rerun()
            else:
                st.info('Debes seleccionar un order_id para continuar', icon="ℹ️")
    else:
        st.write('### No hay órdenes por auditar')


def create_download_link(val, filename):

    # Generate a link to download the pdf

    # Parameters:
    # val: pdf encoded
    # filename: string with pdf file nanme

    # Returns:
    # A hyperlink with to download the file

    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Descargar PDF</a>'

def generar_mensaje_wordpress(objeto):

    incidencia = "Sin incidencia"
    piezas_faltantes = int(objeto['piezas_faltantes']) if 'piezas_faltantes' in objeto else 0
    defectuoso = objeto['defectuoso'] if 'defectuoso' in objeto and objeto['defectuoso'] else None

    if objeto['cantidad_nueva'] < objeto['cantidad_sistema']:
        incidencia = "No llegó el producto (paquetes)"
    if piezas_faltantes > 0:
        incidencia = "Llegó objeto (paquetes) con piezas faltantes"
    if objeto['razon'] == "Defectuoso":
        incidencia = "Llegó defectuoso"

    mensaje = f"""
    Producto: {objeto.get('nombre_producto', 'Desconocido')} - SKU: {objeto.get('sku', 'Desconocido')}
    Se auditó {objeto.get('cantidad_nueva', 0)} de {objeto.get('cantidad_sistema', 0)}
    Razón de diferencia: {incidencia}
    """

    # Si el producto es defectuoso, agregar descripción
    if objeto.get('razon') == "Defectuoso" and objeto.get('defectuoso'):
        mensaje += f"\n    Descripción del defecto: {objeto['defectuoso']}"

    # Si hay piezas faltantes, agregar la cantidad
    if objeto.get('faltan_piezas', False) and objeto.get('piezas_faltantes', 0) > 0:
        mensaje += f"\n    Se recibieron solo {objeto['piezas_faltantes']} piezas."

    return mensaje.strip()  # Elimina espacios extra al inicio y final

def generar_mensaje_seller(producto):
    """
    Genera un mensaje para el seller basado en la incidencia y si hay productos extra.

    :param producto: Diccionario con los datos del pedido y el producto afectado.
    :param link_cambio: Link para que el seller acepte el cambio.
    :return: Mensaje formateado.
    """

    # Calcular la incidencia
    incidencia = "Sin incidencia"
    piezas_faltantes = int(producto['piezas_faltantes']) if 'piezas_faltantes' in producto else 0
    defectuoso = producto['defectuoso'] if 'defectuoso' in producto and producto['defectuoso'] else None

    if producto['cantidad_nueva'] < producto['cantidad_sistema']:
        incidencia = "No llegó el producto (paquetes)"
    if piezas_faltantes > 0:
        incidencia = "Llegó producto (paquetes) con piezas faltantes"
    if producto['razon'] == "Defectuoso":
        incidencia = "Llegó defectuoso"

    # Generar el mensaje según el tipo de incidencia y si hay producto extra
    mensaje = f"Tuvimos una incidencia en el pedido: {producto['order_id']}\n"

    if incidencia != "Sin incidencia" and not producto.get('producto_extra'):
        # Caso 1: Incidencia sin producto extra
        mensaje += (f"Con el producto {producto['nombre_producto']} "
                    f" {incidencia} {defectuoso or ''} con {producto['cantidad_nueva']} {producto.get('unidad', 'Unidad')}.\n")
    elif incidencia != "Sin incidencia" and producto.get('producto_extra'):
        # Caso 2: Incidencia con producto extra  
        mensaje += (f"Con el producto {producto['nombre_producto']} "
                    f" {incidencia} {defectuoso or ''}.\n"
                    f"Y recibimos el producto extra: {producto['producto_extra']} - {producto.get('cantidad_extra', 0)} {producto.get('unidad_extra', 'Unidad')}.\n")
    elif producto.get('producto_extra'):
        # Caso 3: Solo producto extra sin incidencia
        mensaje += (f"Recibimos el producto extra: {producto['producto_extra']} - {producto.get('cantidad_extra', 0)} {producto.get('unidad_extra', 'Unidad')}.\n")

    # Agregar el link al mensaje
    mensaje += f"Necesitamos que lo revises aquí:\n https://mitienda.rintin.mx/order/{producto['order_id']}"
    

    return mensaje.strip()



            



