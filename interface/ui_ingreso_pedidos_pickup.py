import asyncio
import time
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from fpdf import FPDF
import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_searchbox import st_searchbox
import base64
import pandas as pd
from db.db_ingreso_pedidos_pickup import ingreso_inconveniente, ingreso_entrega

async def update_status_wordpress(order_id, order_status):

    # function to update status of an order

    # Parameters:
    # order_id: str, order_id
    # order_status: str, new status you want to give to order

    # Returns:
    # the results of the operation

    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

def create_download_link(val, filename):

    # Generate a link to download the pdf

    # Parameters:
    # val: pdf encoded
    # filename: string with pdf file nanme

    # Returns:
    # A hyperlink with to download the file

    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Descargar PDF</a>'

def ui_entregas():
    if 'visible' not in st.session_state:
        st.session_state['visible'] = True
        st.rerun()
    
    st.header("Herramientas Operaciones")
    st.divider()

    if st.button('Entregas Oaxaca'):
        st.session_state['current_view'] = 'pendiente_entrega_pickup'
        st.rerun()


def search_by_order(searchterm: str):
    
    # Search for the order_id given

    # Parameters:
    # searchterm: a order_id where order is going to be picked (str)
    # parent_order_id or children_order_id

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['order_id'].str.contains(searchterm)|(data['children_orders'].str.contains(searchterm))]
    st.session_state['visible']=False

    return data_filtrado['order_id'] if searchterm else []

def search_bodega(searchterm: str):
    
    # Search for the bodega given

    # Parameters:
    # searchterm: a bodega where order is going to be picked (str)
    # 'Recoleccion Oaxaca'

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['shipping_method'].str.contains(searchterm)]
    st.session_state['visible']=False

    return data_filtrado['shipping_method'] if searchterm else []

def search_cliente(searchterm: str):
    
    # Search for the cliente given

    # Parameters:
    # searchterm: a full_name of the person who's going to pick up the order (str)
    # 'Juan Pablo Jimenez'

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['full_name'].str.lower().str.contains(searchterm.lower())]
    st.session_state['visible']=False

    return data_filtrado['full_name'] if searchterm else []

def search_phone(searchterm: str):
    
    # Search for the phone given

    # Parameters:
    # searchterm: a phone of the person who's going to pick up the order (str)
    # '549485624'

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['phone'].str.contains(searchterm)]
    st.session_state['visible']=False

    return data_filtrado['phone'] if searchterm else []

def search_by_filters(order_id: str, full_name: str, bodega: str, phone: str):
    
    # Search for the order_info with the parameters given

    # Parameters:
    # searchterm: a phone, full_name, bodega or children/parent_order_id of the order to being picked up (str)
    # '549485624', 'Juan Pablo Jimenez', 'Recoleccion Oaxaca', parent_order_id or children_order_id

    # Returns:
    # A dataframe with the rows including the terms searched

    data = st.session_state['data']
    if order_id != '' and order_id != None:
        data = data[data['order_id'].str.contains(order_id)|(data['children_orders'].str.contains(order_id))]
    if full_name != '' and full_name != None:
        data = data[data['full_name'].str.contains(full_name)]
    if phone != '' and phone != None:
        data = data[data['phone'].str.contains(phone)]
    if bodega != '' and bodega != None:
        data = data[data['shipping_method'].str.contains(bodega)]

    st.session_state['visible']=False

    return data

def ui_pendiente_entrega_pickup(data):
    
    data['order_id'] = data['order_id'].astype(str)
    st.session_state['data'] = data
    filtro_orden = ''
    filtro_bodega = ''
    filtro_cliente = ''
    filtro_phone = ''

    st.header('Pendiente entrega en Pickup')
    st.divider()

    filtro_bodega = st_searchbox(
        label='Bodega a recolectar:',
        search_function=search_bodega,
        key=f"search_bodega",
        rerun_on_update=True
    )

    filtro_orden = st_searchbox(
        label='Número de pedido:',
        search_function=search_by_order,
        key=f"search_orderid",
        rerun_on_update=True
    )

    filtro_cliente = st_searchbox(
        label='Nombre Cliente:',
        search_function=search_cliente,
        key=f"search_cliente",
        rerun_on_update=True
    )

    filtro_phone = st_searchbox(
        label='Teléfono Cliente:',
        search_function=search_phone,
        key=f"search_phone",
        rerun_on_update=True
    )

    col1, col2 = st.columns([3, 3])

    with col1:
        find = st.button('Filtrar')

        if find:
            st.session_state['data'] = search_by_filters(filtro_orden, filtro_cliente, filtro_bodega, filtro_phone)
    
    st.write('#')

    st.subheader('Pedidos a entregar:')
    st.write('#')
    col3, col4, col5, col6, col12 = st.columns([4, 2, 5, 2, 2])

    with col3:
        st.markdown("<h5 style='color: black;'>CLIENTE</h5>", unsafe_allow_html=True)

    with col4:
        st.markdown("<h5 style='color: black;'>ID PEDIDO</h5>", unsafe_allow_html=True)

    with col5:
        st.markdown("<h5 style='color: black;'>ID PEDIDOS HIJOS</h5>", unsafe_allow_html=True)

    with col6:
        st.markdown("<h5 style='color: black;'>TELÉFONO</h5>", unsafe_allow_html=True)

    data = st.session_state['data']

    if not data.empty:
        for i, orden in data.iterrows():
            st.divider()
            col7, col8, col9, col10, col11 = st.columns([4,2,5,2,2])
            with col7:
                st.markdown(orden['full_name'])
            with col8:
                st.markdown(orden['order_id'])
            with col9:
                st.markdown(orden['children_orders'])
            with col10:
                st.markdown(orden['phone'])
            with col11:
                if st.button('Entrega', key=f'entregar_{i}'):
                    st.session_state['order_id_pickup'] = orden['order_id']
                    st.session_state['phone_pickup'] = orden['phone']
                    st.session_state['current_view'] = 'bitacora_pickup'
                    st.rerun()
    
    if st.button('Regresar'):
        if 'data' in st.session_state:
            del st.session_state['data']
        if 'order_id_pickup' in st.session_state:
            del st.session_state['order_id_pickup']
        if 'children_id_pickup' in st.session_state:
            del st.session_state['children_id_pickup']
        if 'phone_pickup' in st.session_state:
            del st.session_state['phone_pickup']
        st.session_state.current_view = 'ingreso_pedidos_pickups'
        st.rerun()

def ui_descargar_bitacora(data_general, data_detalle):

    # Show a second UI where user can download the pdf file of the "bitacora"

    # Parameters:
    # data_general: A Dataframe with all the information needed of the parent order
    # ['order_id','full_name','phone','fecha_orden','sub_total','discount','shipping','total', 'shipping_addres', 'comentarios_entrega', 'pay_method', 'zona', 'destino', 'comments', 'metodo_de_envio', 'num_subpedidos', 'pedidos_hijos']
    # data_detalle: A Dataframe with all the information needed of each product of each children order
    # ['estado','suborder','shop','product_name','changes','units_per_pack','qty_of_packs','pack_price', 'discount', 'subtotal']

    # Returns:
    # A UI with the parent_order_id and children_order_id's, and a button to get the link to download the pdf file of the "bitacora"

    st.header(f"Bitácora orden {data_general['order_id'][0]}")
    st.subheader(f"Ordenes hijas: {data_general['pedidos_hijos'][0]}")

    # Indexes to divide the directions fields on the "bitacora" pdf
    partition_index = str(data_general['shipping_addres'][0]).rfind('xico') + 4
    partition_index_comentarios = str(data_general['comentarios_entrega'][0]).lower().rfind(' se') + 1

    if st.button('Generar PDF'):
        pdf = FPDF(orientation='L')
        pdf.add_page()
        pdf.image("imagen/rintin_logo.png", x = 10, y = 0, w = 60, h = 25)
        pdf.image("imagen/frase_resalto_mitad.png", x = 100, y = 7, w = 230, h = 10)
        pdf.set_font('Arial', 'B', 85)
        pdf.cell(1, 10, '')
        pdf.ln()
        pdf.cell(150, 27, str(data_general['order_id'][0]), align='C',border=1)
        pdf.set_font('Arial', '', 18)
        pdf.multi_cell(125, 9, f"Destino:       {str(data_general['destino'][0])}" 
                    + "\n" + f"Zona:         {str(data_general['zona'][0])}" 
                    + "\n" + f"Fecha orden:  {str(data_general['fecha_orden'][0])[0:10]}", align='L',border=1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(20, 10, f"Cliente: ",border=1)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(70, 10, f"{str(data_general['full_name'][0])}",border=1,align='C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(35, 10, f"Dirección cliente: ",border=1)
        pdf.set_font('Arial', '', 8)
        pdf.multi_cell(150, 5, f"{str(data_general['shipping_addres'][0])[:partition_index]}"
                        + "\n" + f"{str(data_general['shipping_addres'][0])[partition_index:]}",border=1,align='C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 10, f"Teléfono del cliente: ",border=1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 10, f"{str(data_general['phone'][0])}",border=1,align='C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(45, 10, f"Comentarios de entrega: ",border=1)
        pdf.set_font('Arial', '', 8)
        pdf.multi_cell(150, 5, f"{str(data_general['comentarios_entrega'][0])[:partition_index_comentarios]}"
                        + "\n" + f"{str(data_general['comentarios_entrega'][0])[partition_index_comentarios:]}",border=1,align='C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 10, f"Método de pago: ",border=1)
        pdf.set_font('Arial', 'B', 10)
        if data_general['pay_method'][0] == 'Prepaid':
            pdf.set_fill_color(79, 79, 79)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(40, 10, f"{str(data_general['pay_method'][0])}",border=1,align='C', fill=True)
        else:
            pdf.cell(40, 10, f"{str(data_general['pay_method'][0])}",border=1,align='C', fill=False)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(45, 10, f"Metodo de envío: ",border=1)
        pdf.set_font('Arial', 'B', 8)
        if str(data_general['metodo_de_envio'][0]).startswith('Recolección'):
            pdf.set_fill_color(79, 79, 79)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(150, 10, f"{str(data_general['metodo_de_envio'][0])}", align="C",border=1, fill = True)
        else:
            pdf.cell(150, 10, f"{str(data_general['metodo_de_envio'][0])}", align="C",border=1, fill = False)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln()
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 10, f"Cantidad de pedidos: ",border=1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 10, f"{str(data_general['num_subpedidos'][0])}",border=1,align='C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(45, 10, f"Comentarios internos: ",border=1)
        pdf.set_font('Arial', '', 8)
        pdf.cell(150, 10, f"{str(data_general['comments'][0])}", align="C",border=1)
        pdf.ln()
        pdf.set_font('Arial', 'B', 7)
        pdf.cell(20, 10, f"Estado", align="C")
        pdf.cell(20, 10, f"Suborden", align="C")
        pdf.cell(25, 10, f"Tienda elegida", align="C")
        pdf.cell(60, 10, f"Nombre del producto", align="C")
        pdf.cell(20, 10, f"Cambios", align="C")
        pdf.cell(30, 10, f"Piezas por paquete", align="C")
        pdf.cell(30, 10, f"Cantidad paquetes", align="C")
        pdf.cell(30, 10, f"Precio paquetes", align="C")
        pdf.cell(20, 10, f"Descuento", align="C")
        pdf.cell(20, 10, f"Sub Total", align="C")
        pdf.set_font('Arial', '', 10)
        for i in range(len(data_detalle['suborder'])):
            pdf.ln()

            # Where the text starts, also where to start the strikethrough line.
            x = pdf.get_x()
            y = pdf.get_y()

            pdf.cell(20, 5, f"{str(data_detalle['estado'][i])}", align="C")
            pdf.cell(20, 5, f"{str(data_detalle['suborder'][i])}", align="C")
            pdf.cell(25, 5, f"{str(data_detalle['shop'][i])}", align="C")
            pdf.multi_cell(60, 5, f"{str(data_detalle['product_name'][i])}", align="C")
            y_2 = pdf.get_y()
            # reposition of cursor to write after a multicell
            pdf.set_xy(x + 125, y)
            pdf.multi_cell(20, 5, f"{str(data_detalle['changes'][i])}", align="C")
            y_3 = pdf.get_y()
            # reposition of cursor to write after a multicell
            pdf.set_xy(x + 145, y)
            pdf.cell(30, 5, f"{str(int(data_detalle['units_per_pack'][i]))}", align="C")
            pdf.cell(30, 5, f"{str(data_detalle['qty_of_packs'][i])}", align="C")
            pdf.cell(30, 5, f"${str(data_detalle['pack_price'][i])}", align="C")
            pdf.cell(20, 5, f"${str(data_detalle['discount'][i])}", align="C")
            pdf.cell(20, 5, f"${str(data_detalle['subtotal'][i])}", align="C")
            if y_2 > y_3:
                pdf.set_y(y_2)
            else:
                pdf.set_y(y_3)

            if data_detalle['estado'][i] == 'Cancelado':
                # values to draw a line where suborder is cancelled
                pdf.set_line_width(0.25)
                width = 275
                lineHt = 8
                # Then draw the line
                pdf.line(x, y + (lineHt / 4), x+width, y)
        
        pdf.ln()
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Subtotal: ", align='L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"${str(data_general['sub_total'][0])}", align='R')
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Descuentos: ", align='L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"${str(data_general['discount'][0])}", align='R')
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Envío: ", align='L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"${str(data_general['shipping'][0])}", align='R')
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Total a Pagar: ", align='L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"${str(data_general['total'][0])}", align='R')
        pdf.ln()
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.set_xy(50, 180)
        pdf.cell(100,5, 'Este detalle NO es referencia de lo que contiene el paquete ni del total a pagar', align='C')
        pdf.image("imagen/frase_resalto_inicial.png", x = 10, y = 200, w = 200, h = 10)
        pdf.image("imagen/rintin_telefono.png", x = 230, y = 190, w = 60, h = 28)

        html = create_download_link(pdf.output(dest="S").encode("latin-1"), 'Bitacora pedido ' + str(data_general['order_id'][0]))
        st.markdown(html, unsafe_allow_html=True)

    if st.button('Validar entrega'):
        st.session_state['children_id_pickup'] = data_general['pedidos_hijos'][0]
        st.session_state.current_view = 'validar_entrega'

    # limpieza de estado dataframe
        if 'data' in st.session_state:
                del st.session_state['data']
        st.rerun()
    
    if st.button('Regresar'):
        if 'children_id_pickup' in st.session_state:
            del st.session_state['children_id_pickup']

        st.session_state.current_view = 'pendiente_entrega_pickup'
        st.rerun()

def ui_validacion_entrega(order_id, phone, data: pd.DataFrame):
    st.header(f"Pedido: {order_id}")
    st.header(f"Teléfono: {phone}")
    st.write('##')
    st.write('##')

    st.header("Detalle de orden:")
    st.write('##')
    
    estados = []
    objArry=[]
    total_parcial = 0
    total_esperado = 0
    for i, pedido in data.iterrows():
        col1, col2, col3, col4 = st.columns([3, 3, 6, 4])
        with col1:
            if pedido.img_url is not None:
                st.image(pedido.img_url, use_column_width=True)
            else:
                st.write("Sin imagen")

        with col2:
            st.markdown(f'##### Nombre: {pedido.order_item_name}')
            st.markdown(f'##### SKU: {pedido.sku}')         
        with col3:
            st.markdown(f'##### Cantidad: {pedido.line_qty}')
        
            cantidad_pickeada = st.number_input(f"Confirmados", key=f"cantidad_{i}", value=0,min_value=0, max_value=int(pedido.line_qty))
        
        with col4:
            # Comparar si la cantidad ingresada es igual a la cantidad requerida
            if cantidad_pickeada == int(pedido.line_qty):
                estado = 'OK'
                st.success(estado)
            elif cantidad_pickeada > int(pedido.line_qty):
                cantidad_pickeada=0
                estado = 'NO OK'
                st.error(estado)
            else:
                estado = 'NO OK'                    
                st.error(estado)
            estados.append(estado)

            if estado == 'NO OK':
                dif = st.selectbox('Razon diferencias',
                            options=[
                                 'Faltante producto',
                                 'Producto con falla?',
                                 'Cliente no tiene dinero'
                                 ],
                            key=f"diferencia_{i}"
                            )
        st.divider()
        total_parcial += cantidad_pickeada * float(pedido.unit_price)
        total_esperado += int(pedido.line_qty) * float(pedido.unit_price)

        if estado == 'NO OK':
            objArry.append(
                {
                    "order_item_id": int(pedido.order_item_id),
                    "cantidad_no_entregada": int(pedido.line_qty) - cantidad_pickeada,
                    "razon_no_entrega": dif,
                    "fecha": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            )

    col6, col7, col8, col9 = st.columns([5,4,4,3])

    with col7:
        st.markdown('##### Total a cobrar: ')
    
    with col8:
        st.markdown(total_parcial)

    with col9:
        estado_entrega = True
        if len(objArry) > 0:
            estado_entrega = False
            
        if estado_entrega:
            st.success(estado)
        else:
            st.error(estado)
    
    trigger_btn = st.button(label="Confirmar", key="trigger_btn")
    respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Entrega", description=f'Confirmemos entrega del pedido padre #{str(order_id)} y los hijos {st.session_state.children_id_pickup}', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
    if respuesta:
        razon_dif = ''
        print(f"----- {len(objArry)}")
        for objeto in objArry:
            ingreso_inconveniente(objeto['order_item_id'], objeto['cantidad_no_entregada'], objeto['razon_no_entrega'], objeto['fecha'])
            razon_dif = "item_order_id: " + str(objeto['order_item_id']) + " y razon_no_entrega: " + str(objeto['razon_no_entrega'])
        
        ingreso_entrega(int(order_id), float(total_esperado), float(total_parcial), razon_dif)
        with st.spinner('Actualizando estado de orden a "Entregado"'):
            r = asyncio.run(update_status_wordpress(order_id, 'delivered'))
        st.session_state.current_view = 'finalizar_entrega'
        st.rerun()
    
    if st.button('Regresar'):
        st.session_state.current_view = 'bitacora_pickup'
        st.rerun()

def ui_finalizar_entrega(order_id, children_order_id):
    st.markdown(f'## Se actualizaró el pedido con número {order_id} e hijos {children_order_id} al estado Entregado')
    st.write('---')
    
    if st.button('Regresar'):
        st.session_state['current_view'] = 'ingreso_pedidos_pickups'
        if 'data' in st.session_state:
            del st.session_state['data']
        if 'order_id_pickup' in st.session_state:
            del st.session_state['order_id_pickup']
        if 'children_id_pickup' in st.session_state:
            del st.session_state['children_id_pickup']
        if 'phone_pickup' in st.session_state:
            del st.session_state['phone_pickup']
        st.rerun()