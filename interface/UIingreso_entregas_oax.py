import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from db.db_ingreso_entregador_oax import update_route

def UIingreso_entregador_oax(data):
    st.write('## Pendientes Ingreso')
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write('**Ruta**')
    with col2:
        st.write('**Entregador**')
    with col3:
        st.write('**Fecha de creación**')
    for i in range(len(data['id_ruta'])):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"{data['id_ruta'][i]}")
        with col2:
            st.write(f"{data['responsable'][i]}")
        with col3:
            st.write(f"{data['fecha_creacion'][i]}")
        with col4:
            if st.button('Ingresar', key=i):
                st.session_state.current_route = data['id_ruta'][i]
                st.session_state.current_view = 'route_order_detail'
                st.rerun()

def UIconfirmacion(id_ruta):
    st.write(f'## Se ingresó correctamente la ruta {id_ruta}')
    if st.button('Regresar'):
        st.session_state.current_view = 'ingreso_entregador_oax'
        st.rerun()

def UIorder_detail(data, id_ruta):
    if st.button('Regresar'):
        st.session_state.current_view = 'ingreso_entregador_oax'
        st.rerun()
    st.write('## Pendientes Ingreso')
    ordenes = []
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.write('**Cliente**')
    with col2:
        st.write('**Pedido**')
    with col3:
        st.write('**Dinero a recibir**')
    with col4:
        st.write('**Dinero recibido**')
    with col5:
        st.write('**Status**')
    for i in range(len(data['order_id'])):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(f"{data['name'][i]}")
        with col2:
            st.write(f"{data['order_id'][i]}")
        with col3:
            st.write(f"{data['total_recibido'][i]}")
        with col4:
            ingresado = st.number_input('', min_value=0.00, label_visibility="collapsed", key=f"number_{i}")
        with col5:
            if float(data['total_recibido'][i]) != ingresado:
                st.error('Validacion')
                razon = st.text_input('Razón diferencia', key=f"text_{i}")
            else:
                st.success('OK')
                razon = 'NULL'
        ordenes.append({"order_id": data['order_id'][i], "total": data['total_recibido'][i], "ingresado": ingresado, "razon": razon})
    confirm = st.button('Recibir')
    respuesta = ui.alert_dialog(show=confirm, title="Confirmación de ingreso", description=f'Se ingresará la ruta {id_ruta}.', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
    if respuesta:
        update_route(id_ruta, ordenes, 'Ingresado a bodega')
        st.session_state.current_view = 'confirmacion_route_order'
        st.rerun()