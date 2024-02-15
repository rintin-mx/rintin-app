import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id

def UIentregas_oax(data):
    st.write('# Pedidos a entregar')
    st.write('---')
    orders_for_route_list = []
    for i in range(len(data["order_id"])):
        st.write('### Cliente:')
        st.write(f'{data["name"][i]}')
        st.write('### Número de pedido:')
        st.write(f'{data["order_id"][i]}')
        st.write('### Número de contacto:')
        st.write(f'{data["number_unified"][i]}')
        st.write('### Dirección:')
        st.write(f'{data["address"][i]}')
        st.write('### Número de paquetes:')
        st.write(f'{data["num_paquetes"][i]}')
        checked = st.checkbox('Ingresar a ruta', key=i)
        if checked:
            orders_for_route_list.append({
                "order_id": data["order_id"][i],
                "name": data["name"][i],
                "number_unified": data["number_unified"][i],
                "address": data["address"][i]
            })
        st.write('---')
        
    trigger_btn = ui.button(text="Empaquetar", key="trigger_btn")
    respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de ruta", description=f'Se creará una ruta con {len(orders_for_route_list)} ordenes distintas.', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
    if respuesta:
        # Escribir en tabla de bd
        st.session_state['current_view'] = 'ruta_envios'
        st.rerun()
        
    