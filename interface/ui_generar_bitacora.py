from typing import List
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
from streamlit_searchbox import st_searchbox
from st_mui_table import st_mui_table
import asyncio

import base64
from fpdf import FPDF

def create_download_link(val, filename):

    # Generate a link to download the pdf

    # Parameters:
    # val: pdf encoded
    # filename: string with pdf file nanme

    # Returns:
    # A hyperlink with to download the file

    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Descargar PDF</a>'

def search_orderid(searchterm: str) -> List[any]:
    
    # Search for the parent_order_id of the order given

    # Parameters:
    # searchterm: a parent_order_id or children_order_id (str)
    # Parent_order_id/child_order_id

    # Returns:
    # A string with the parent_order_id

    data = st.session_state['data']
    data_filtrado = data[data['order_id'].str.contains(searchterm)|(data['hijos'].str.contains(searchterm))]
    print(data_filtrado)
    st.session_state['visible']=False

    return data_filtrado['order_id'] if searchterm else []

def UITodosLosPedidos(data):

    # Create the UI to search for the parent order to generate the "bitacora"

    # Parameters:
    # data: A Dataframe containing 2 columns (parent_order_id, children_order_id's)
    # [Parent_order_id, child_order_id, child_order_id, ..., child_order_id]

    # Returns:
    # A UI with a table showing the dataframe received, and a searchbar to select the parent order by writing the parent_order_id
    # OR any children_order_id

    st.session_state['data'] = data
    selected_value = ''
    if 'visible' not in st.session_state:
        print("visible")
        st.session_state['visible'] = True
        st.rerun()

    data['order_id'] = data['order_id'].astype(str)
    print("selected_value")
    
    selected_value = st_searchbox(
        label='Buscar por ID o Seller',
        search_function=search_orderid,
        key=f"search_orderid",
        rerun_on_update=True
    )
    print(selected_value)
    submit = st.button("Buscar")
    st_mui_table(data)

    if submit:
        if selected_value is not None:
            print(selected_value)
            st.session_state['Order_id_bitacora'] =int(selected_value)
            st.session_state['current_view'] = 'detalle_bitacora'
            st.rerun()
        else:
            st.info('Debes seleccionar un order_id para continuar', icon="ℹ️")

def UIdetalleBitacora(data_general, data_detalle):

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
    partition_index_comentarios = str(data_general['comentarios_entrega'][0]).lower().rfind('. se') + 1

    if st.button('Generar PDF'):
        pdf = FPDF(orientation='L')
        pdf.add_page()
        pdf.image("imagen/rintin_logo.png", x = 10, y = 0, w = 60, h = 25)
        pdf.image("imagen/frase_resalto_mitad.png", x = 100, y = 7, w = 230, h = 10)
        pdf.set_font('Arial', 'B', 70)
        pdf.cell(1, 10, '')
        pdf.ln()
        pdf.cell(150, 27, str(data_general['order_id'][0]), align='C',border=1)
        pdf.set_font('Arial', '', 18)
        pdf.multi_cell(125, 9, f"Destino:       {str(data_general['zona'][0])}" 
                    + "\n" + f"Zona:         {str(data_general['destino'][0])}" 
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
            pdf.set_fill_color(189, 181, 179)
            pdf.cell(40, 10, f"{str(data_general['pay_method'][0])}",border=1,align='C', fill=True)
        else:
            pdf.cell(40, 10, f"{str(data_general['pay_method'][0])}",border=1,align='C', fill=False)
        pdf.set_font('Arial', '', 10)
        pdf.cell(45, 10, f"Metodo de envío: ",border=1)
        pdf.set_font('Arial', '', 8)
        pdf.cell(150, 10, f"{str(data_general['metodo_de_envio'][0])}", align="C",border=1)
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
        pdf.set_font('Arial', '', 7)
        for i in range(len(data_detalle['suborder'])):
            pdf.ln()
            pdf.cell(20, 5, f"{str(data_detalle['estado'][i])}", align="C")
            pdf.cell(20, 5, f"{str(data_detalle['suborder'][i])}", align="C")
            pdf.cell(25, 5, f"{str(data_detalle['shop'][i])}", align="C")
            pdf.cell(60, 5, f"{str(data_detalle['product_name'][i])}", align="C")
            pdf.cell(20, 5, f"{str(data_detalle['changes'][i])}", align="C")
            pdf.cell(30, 5, f"{str(data_detalle['units_per_pack'][i])}", align="C")
            pdf.cell(30, 5, f"{str(data_detalle['qty_of_packs'][i])}", align="C")
            pdf.cell(30, 5, f"${str(data_detalle['pack_price'][i])}", align="C")
            pdf.cell(20, 5, f"${str(data_detalle['discount'][i])}", align="C")
            pdf.cell(20, 5, f"${str(data_detalle['subtotal'][i])}", align="C")
        
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
        pdf.image("imagen/rintin_telefono.png", x = 230, y = 185, w = 60, h = 30)

        html = create_download_link(pdf.output(dest="S").encode("latin-1"), 'Bitacora pedido ' + str(data_general['order_id'][0]))
        st.markdown(html, unsafe_allow_html=True)

    if st.button('Regresar al Inicio'):
        st.session_state.current_view = 'bitacora'
    # limpieza de estado dataframe
        if 'data' in st.session_state:
                del st.session_state['data']
        st.rerun()