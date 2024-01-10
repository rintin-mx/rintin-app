
import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productosValidados import insert_productos_validados,update_order_product_status
from db.db_UserInteractionEvents import event_instert
from datetime import datetime
import streamlit.components.v1 as components

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

async def update_order_note__wordpress(order_id, order_notes):
    result = await endpoint_write_order_note(order_id, order_notes)
    return result

def UITOrdenesCompra():

    # Título de la página
    st.title('Ordenes de compra')

    # Selector para el vendedor
    seller = st.selectbox('Seller', ['Vendedor A', 'Vendedor B', 'Vendedor C'])

    # Sección de detalle de orden
    st.subheader('Detalle orden')
    # Columnas para Producto, Cantidad, Costo y Total
    col1, col2, col3, col4 , col5 = st.columns(5)
    with col1:
        producto = st.text_input('Producto')
    with col2:
        cantidad = st.number_input('Cantidad', min_value=0)
    with col3:
        costo = st.number_input('Costo', min_value=0.0)
    with col4:
        # Se asume que el total es calculado automáticamente multiplicando cantidad por costo
        total = cantidad * costo
        st.text('Total')
        st.write(total)
    with col5:
        # Botón para agregar productos
        st.text('')
        st.text('')
        if st.button('Editar Orden'):
            st.write('Editar Orden')

    # Botón para agregar productos
    if st.button('Agregar Productos'):
        st.write('Producto agregado!')

    # Código para ejecutar la aplicación:
    # streamlit run tu_archivo.py
