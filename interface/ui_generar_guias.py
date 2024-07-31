import sys

from integration.cache_api import update_order_metadata
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_order_meta_data, endpoint_update_status_by_order_id
#from db.db_numeros_guia import update_order_metadata

operadores_list = [
    'estafeta',
    '99 minutos',
    'ogramak',
    'redpack',
    'fedex',
    'tiui',
    'klozer'
]

def UIgenerar_guias_final(order_string, child_list):
    if len(child_list) == 1:
        st.write(f'## Se actualizó el pedido {order_string} al estado "Embarque" y se actualizó su número de guía y operador logístico')
    elif len(child_list) > 1:
        st.write(f'## Se actualizaron los pedidos {order_string} al estado "Embarque" y se actualizaron sus números de guía y operadores logísticos')
    st.write('---')
    if st.button('Regresar'):
        st.session_state['current_view'] = 'generar_guias'
        st.rerun()

def UIgenerar_guias(data):
    st.write('### Ordenes empaquetadas')
    st.write('---')
    new_data = []
    order_id_string = ''
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.write('**ID Orden**')
    with col2:
        st.write('**Estado a enviar**')
    with col3:
        st.write('**Código postal**')
    with col4:
        st.write('**Paquetería**')
    with col5:
        st.write('**Número de guía**')
    st.write('---')
    for i in range(len(data['order_id'])):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(data['order_id'][i])
        with col2:
            st.text(data['state'][i])
        with col3:
            st.text(data['postcode'][i])
        with col4:
            index = None
            if data['logis_op'][i] is not None:
                index = operadores_list.index(data['logis_op'][i])
            paqueteria = st.selectbox('Paquetería', options=operadores_list, label_visibility='collapsed', key=str(i)+'_paqueteria', index=index)
        with col5:
            num_guia_value = ''
            num_guia_value = data['numero_guia'][i]
            num_guia = st.text_input('Número de guía', label_visibility='collapsed', key=str(i)+'_num_guia', value=num_guia_value)
        if (paqueteria != data['logis_op'][i] or num_guia != data['numero_guia'][i]):
            order_id_string += str(data['order_id'][i]) + ', '
            new_data.append({"order_id": data['order_id'][i], "numero_guia": num_guia, "paqueteria": paqueteria, "childs": data['hijos_guia'][i]})
        if(data['ordenes_activas'][i] != data['num_hijos_guia'][i]):
            st.warning('No todos los hijos estan en el estado "Generar numeros de guia"')
        st.write('---')
    
    if len(new_data) > 0:
        order_id_string = order_id_string[:-2]
        respuesta = False
        trigger_btn = ui.button(text="Actualizar", key="trigger_btn")
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de actualización para los pedidos", description=order_id_string, confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner('Actualizando ordenes'):
                for value in new_data:
                    temp_arr = [
                        {"key": '_numero_guia', "value": value['numero_guia']},
                        {"key": '_logis_op', "value": value['paqueteria']}
                    ]
                    
                    update_order_metadata([str(value['order_id'])], '_numero_guia', value['numero_guia'])
                    update_order_metadata([str(value['order_id'])], '_logis_op', value['paqueteria'])
                    if value['childs'] is None:
                        r2 = asyncio.run(endpoint_update_status_by_order_id(value['order_id'], 'embarque'))
                    else:
                        childs_array = value['childs'].split(', ')
                        if len(childs_array) > 0:
                            for order_id in childs_array:
                                
                                update_order_metadata([str(value['order_id'])], '_numero_guia', value['numero_guia'])
                                update_order_metadata([str(value['order_id'])], '_logis_op', value['paqueteria'])
                                r2 = asyncio.run(endpoint_update_status_by_order_id(int(order_id), 'embarque'))
            st.session_state['orders_string'] = order_id_string
            st.session_state['child_list'] = new_data
            st.session_state['current_view'] = 'generar_guias_final'
            st.rerun()
