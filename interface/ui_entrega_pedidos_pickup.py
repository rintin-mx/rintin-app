import asyncio
import time
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from fpdf import FPDF
import streamlit as st
import streamlit_shadcn_ui as ui
from streamlit_searchbox import st_searchbox
from integration.insert_to_S3 import insertOrderImage
import base64
from db.db_entrega_pedidos_pickup import ingreso_entrega, insert_item_problem, insert_product_problem

DIFF_REASONS = ['Producto faltante', 'Producto con falla', 'Cliente sin dinero']
PROBLEM_REASONS = ['Producto faltante', 'Producto con falla']
NO_ENTREGA_REASON = ['Sin contacto de cliente', 'Cliente sin dinero', 'No encuentro direccion']
NEXT_STATUS_DICT = {
	"Pendiente entrega": "Intento 1",
	"Intento 1": "Intento 2",
	"Intento 2": "Intento 3",
	"Intento 3": "Fallido"
}

PAGOS_DICT = {
	'woo-mercado-pago-basic': 'Pre-pagado',
	'cheque': 'Pago contra-entrega'
}

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

    filtro_bodega = st.selectbox('Bodega a recolectar',
        options=[
                'Recolección en bodega Ciudad de Mexico (Mixcalco)',
                'Recolección en bodega OAXACA',
                'Recolección en bodega Oaxaca Ciudad (JP Garcia)'
                ],
        index=None,
        placeholder="Search ..."
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

def ui_descargar_bitacora(data_general, data_detalle, fees):

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
        pdf.multi_cell(125, 9, f"Destino: {str(data_general['destino'][0])}" 
                    + "\n" + f"Zona: {str(data_general['zona'][0])}" 
                    + "\n" + f"Fecha orden: {str(data_general['fecha_orden'][0])[0:10]}", align='L',border=1)
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
        subtotal = 0
        adelanto = 0
        envio = float(data_general['shipping'][0])
        descuentos_totales = float(data_general['discount'][0])
        for i in range(len(fees['name'])):
            if 'descuento' in fees['name'][i].lower():
                descuentos_totales -= (float(fees['fee_amount'][i]))
            elif 'envío' in fees['name'][i].lower():
                envio += (float(fees['fee_amount'][i]))
            elif 'adelanto' in fees['name'][i].lower():
                adelanto -= (float(fees['fee_amount'][i]))
        for i in range(len(data_detalle['suborder'])):
            if (i%28 == 0 and i > 0) or i == 10:
                pdf.add_page()
                pdf.set_y(10)
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

            pdf.ln()

            # Where the text starts, also where to start the strikethrough line.
            x = pdf.get_x()
            y = pdf.get_y()

            pdf.cell(20, 5, f"{str(data_detalle['estado'][i])}", align="C")
            pdf.cell(20, 5, f"{str(data_detalle['suborder'][i])}", align="C")
            pdf.cell(25, 5, f"{str(data_detalle['shop'][i])}", align="C")
            pdf.cell(60, 5, f"{str(data_detalle['product_name'][i])[0:28]}", align="C")
            y_2 = pdf.get_y()
            # reposition of cursor to write after a multicell
            pdf.set_xy(x + 125, y)
            y_3 = 0
            if(data_detalle['changes'][i] == ''):
                pdf.cell(20, 5, f"{str(data_detalle['changes'][i])}", align="C")
            else:
                pdf.multi_cell(20, 5, f"{str(data_detalle['changes'][i])}", align="C")
                y_3 = pdf.get_y()
            # reposition of cursor to write after a multicell
            pdf.set_xy(x + 145, y)
            pdf.cell(30, 5, f"{str(int(data_detalle['units_per_pack'][i]))}", align="C")
            pdf.cell(30, 5, f"{str(data_detalle['qty_of_packs'][i])}", align="C")
            pdf.cell(30, 5, f"${str(round(data_detalle['pack_price'][i], 2))}", align="C")
            pdf.cell(20, 5, f"${str(round(data_detalle['discount'][i], 2))}", align="C")
            pdf.cell(20, 5, f"${str(round(data_detalle['subtotal'][i], 2))}", align="C")
            if y_2 > y_3:
                pdf.set_y(y_2)
            else:
                pdf.set_y(y_3)

            if data_detalle['estado'][i] != 'Cancelado':
                subtotal += round(data_detalle['pack_price'][i], 2) * int(data_detalle['qty_of_packs'][i])
            else:
                # values to draw a line where suborder is cancelled
                pdf.set_line_width(0.25)
                width = 275
                lineHt = 8
                # Then draw the line
                pdf.line(x, y + (lineHt / 4), x+width, y + (lineHt / 4))
        
        pdf.ln()
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Subtotal: ", align='R')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"${round(subtotal,2)}", align='R')
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Descuentos: ", align='R')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"$-{descuentos_totales}", align='R')
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Adelantos: ", align='R')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"$-{adelanto}", align='R')
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Envío: ", align='R')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"${envio}", align='R')
        pdf.ln()
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(205, 5, '')
        pdf.cell(30, 5, "Total a Pagar: ", align='R')
        pdf.set_font('Arial', '', 10)
        pdf.cell(30, 5, f"${round(subtotal + envio - descuentos_totales - adelanto)}", align='R')
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
        st.session_state['addres'] = data_general['shipping_addres'][0]
        st.session_state['pay_method'] = data_general['pay_method'][0]
        st.session_state.current_view = 'validar_entrega'

        # limpieza de estado dataframe
        if 'data' in st.session_state:
                del st.session_state['data']
        st.rerun()
    if st.button('Regresar al Inicio'):
        st.session_state.current_view = 'bitacora'
    # limpieza de estado dataframe
        if 'data' in st.session_state:
                del st.session_state['data']
        st.rerun()

def ui_validacion_entrega(order_id, number_unified, address, order_items, metodo_pago, descuento):
    if st.button('Regresar'):
        st.session_state.current_view = 'bitacora_pickup' 
        st.rerun()
    orders_dict = {}
    children_orders = set(order_items['order_id'])
    if len(children_orders) > 1:
        try:
            children_orders.remove(int(order_id))
        except:
            pass
    calculated_total = 0.0
    total = 0.0
    respuesta = False
    validacion = True
    st.write(f'### Pedido: {order_id}')
    st.write(f'### Telefono cliente: {number_unified}')
    st.write(f'### Dirección:')
    st.write(address)
    st.write('### Método de pago:')
    if metodo_pago.lower() == 'prepaid':
        st.write('Pre-pagado')
    else:
        st.write('Pago contra-entrega')
    st.write('#### Productos de la orden')
    order_items_con_falla = []
    for i in range(len(order_items['order_item_id'])):
        if order_items['order_item_type'][i] == 'line_item':
            st.image(order_items['img_url'][i])
            st.write('#### Nombre de producto:')
            st.write(order_items['order_item_name'][i])
            st.write('#### SKU:')
            st.write(order_items['sku'][i])
            st.write('#### Cantidad:')
            st.write(int(order_items['line_qty'][i]))
            st.write('#### Precio:')
            st.write(f"{(order_items['line_total'][i])}")
            total += (float(order_items['line_qty'][i]) * round(float(order_items['line_total'][i]),2))
            recieved = st.number_input('Cantidad recibida', min_value=0, max_value=int(order_items['line_qty'][i]), step=1, key=f'amount_{i}')
            calculated_total += (recieved * round(float(order_items['line_total'][i]),2))
            if recieved != int(order_items['line_qty'][i]):
                reason = st.selectbox('Razón diferencia', options=DIFF_REASONS, key=f'select_{i}', index=None)
                if reason is None:
                    validacion = validacion and False
                st.error('Validación')
                order_items_con_falla.append({
                    "order_item_id": order_items['order_item_id'][i],
                    "cantidad_entregada": recieved,
                    "razon_no_entrega": reason,
                    "tipo": 0
                })
            else:
                reason = ''
                st.success('OK')
            if st.checkbox('Paquete con problema', key=f'paquet_{i}'):
                units_with_problem = st.number_input('Cantidad con problema', min_value=0, max_value=int(order_items['line_qty'][i]), key=f'cantidad_{i}')
                problem_reason = st.selectbox('Razón problema', options=PROBLEM_REASONS, key=f'problem_{i}')
                order_items_con_falla.append({
                    "order_item_id": order_items['order_item_id'][i],
                    "cantidad_entregada": units_with_problem,
                    "razon_no_entrega": problem_reason,
                    "tipo": 1
                })
        else:
            st.write('### Envío: ' )
            st.write(order_items['order_item_name'][i])
            st.write('### Precio:')
            st.write(order_items['line_total'][i])
            st.write('### Descuentos:')
            st.write(descuento)
            total += round(float(order_items['line_total'][i]), 2)
            calculated_total += round(float(order_items['line_total'][i]), 2)
        if order_items['order_id'][i] in orders_dict:
            orders_dict[order_items['order_id'][i]] += recieved
        else:
            orders_dict[order_items['order_id'][i]] = recieved
    
    st.write('---')
    
    total -= float(descuento)
    if metodo_pago.lower() == 'prepaid':
        total = 0
        calculated_total = 0

    if calculated_total - float(descuento) < 0:
        calculated_total = 0
    else:
        calculated_total = calculated_total - float(descuento)

    st.write(f'Total calculado a cobrar: ${calculated_total}')
    st.write(f'Total a cobrar: ${total}')
    value = st.number_input('Total recibido: ', min_value=0.00, step=0.01)
    if value != float(total) and value != 0:
        st.error('Validacion')
    button = st.button('Confirmar entrega')
    photo = st.file_uploader('Imagen de entrega', type=['png', 'jpg'])
    if validacion:
        respuesta = ui.alert_dialog(show=button, title="Confirmación de entrega de orden", description=f'Se entrego la orden {order_id}', confirm_label="Confirmar", cancel_label="Volver", key="respuesta_entrega")
    else:
        st.error('Se deben seleccionar todas las razones de no entrega en los productos')
    if respuesta:
        last_product_fail = ''
        img_url = ''
        if photo is not None:
            img_url = insertOrderImage(photo, order_id, 'rintin-internal-apps')
        for product in order_items_con_falla:
            if product['tipo'] == 0:
                insert_item_problem(product)
            elif product['tipo'] == 1:
                insert_product_problem(product)
            if product['razon_no_entrega'] != '':
                last_product_fail = product['razon_no_entrega']
            
        ingreso_entrega(order_id, total, calculated_total, last_product_fail, img_url)
        for order in children_orders:
            r = asyncio.run(update_status_wordpress(order, 'delivered'))
        st.session_state.current_view = 'finalizar_entrega'
        st.rerun()

def ui_finalizar_entrega(order_id, children_order_id):
    st.markdown(f'## Se actualizaró el pedido con número {order_id} e hijos {children_order_id} al estado Entregado')
    st.write('---')
    
    if st.button('Regresar'):
        st.session_state['current_view'] = 'pendiente_entrega_pickup'
        if 'data' in st.session_state:
            del st.session_state['data']
        if 'order_id_pickup' in st.session_state:
            del st.session_state['order_id_pickup']
        if 'children_id_pickup' in st.session_state:
            del st.session_state['children_id_pickup']
        if 'phone_pickup' in st.session_state:
            del st.session_state['phone_pickup']
        if 'addres' in st.session_state:
            del st.session_state['addres']
        if 'pay_method' in st.session_state:
            del st.session_state['pay_method']
        if 'discount' in st.session_state:
            del st.session_state['discount']
        st.rerun()