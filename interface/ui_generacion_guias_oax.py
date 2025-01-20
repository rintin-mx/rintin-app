import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
from datetime import datetime
import asyncio
from integration.endpoint_wordpress import endpoint_update_order_meta_data, endpoint_update_status_by_order_id
from integration.cache_api import update_order_metadata


operadores_list = [
    'estafeta',
    '99 minutos',
    'ogramak',
    'redpack',
    'fedex',
    'tiui',
    'chavobus'
]

def UIgeneracion_guias_oax(data, order_filter, zone_filter):
    order_list = pd.DataFrame(data)
    st.write('## Pedidos a ingresar en guia Pickup')
    filter_col1, filter_col2 = st.columns(2)
    objArray= []

    order_id_string = ''
    
    with filter_col1:
        order_filter_input = st.selectbox('Busqueda por orden', options=order_filter, index= None)
    with filter_col2:
        zone_filter_input = st.selectbox('Busqueda por zona de entrega', options=zone_filter, index= None)
    
    if order_filter_input is not None and zone_filter_input is not None:
        order_list_filtered =  order_list[((order_list['order_id'] == int(order_filter_input)) | (order_list['hijos_guia'].str.contains(order_filter_input))) & (order_list['zona_entrega'] == zone_filter_input)]
    elif zone_filter_input is not None and order_filter_input is None:
        order_list_filtered =  order_list[(order_list['zona_entrega'] == zone_filter_input)]
    elif order_filter_input is not None and zone_filter_input is None:
        order_list_filtered =  order_list[(order_list['order_id'] == int(order_filter_input)) | (order_list['hijos_guia'].str.contains(order_filter_input))]
    else:
        order_list_filtered = order_list
    

    st.write('### Datos para guia interna')
    guia_col1, guia_col2 = st.columns(2)
    numero_guia = ''
    with guia_col1:
        origin = st.selectbox('Origen', options=['CDMX', 'OAX', 'MIAH'], index=None)
    with guia_col2:
        destiny = st.selectbox('Destino', options=['CDMX', 'OAX', 'MIAH'], index=None)
    day = st.date_input('Ingresa la fecha de envío', format="DD/MM/YYYY")

    if origin is not None and destiny is not None and day is not None:
        date = datetime.strptime(str(day), "%Y-%m-%d")
        formatted_day = date.strftime("%d%m%Y")
        numero_guia = f'{origin}-{destiny}-{day}'
        st.write(f'**GUIA:** {origin}-{destiny}-{formatted_day}')
    sender = st.selectbox('Paqueteria interna', options=operadores_list)
    header_col1, header_col2, header_col3, header_col4 = st.columns(4)
    with header_col1:
        st.write('**ID orden**')
    with header_col2:
        st.write('**Zona de entrega**')
    with header_col3:
        st.write('**Hijos**')
    with header_col4:
        st.write('**Ingresado en la guía**')
    st.write('---')
    if len(order_list_filtered) > 0:
        for i, value in order_list_filtered.iterrows():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.text(value.order_id)
            with col2:
                st.text(value.zona_entrega)
            with col3:
                st.text(value.hijos_guia)
            with col4:
                agrupadoSeleccion = st.toggle('',key=f'recolectado{i}')
                if agrupadoSeleccion:
                    objArray.append({"order_id":value.order_id,
                                "zona_entrega":value.zona_entrega,
                                "hijos":value.hijos_guia,
                                'paqueteria': sender,
                                'numero_guia': numero_guia,
                                })
                    order_id_string += str(value.order_id) + ', '
            if(value.ordenes_activas != value.num_hijos_guia):
                st.warning('No todos los hijos estan en el estado "Generar numeros de guia"')
            st.write('---')
    else:
        st.write('### No hay ordenes que cumplan con estos parametros')
    if len(objArray) > 0 and numero_guia != '':
        order_id_string = order_id_string[:-2]
        trigger_btn = ui.button(text="Actualizar", key="trigger_btn")
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de actualización para los pedidos", description=order_id_string, confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner('Actualizando ordenes'):
                for value in objArray:
                    update_order_metadata([str(value['order_id'])], '_numero_guia_interno', value['numero_guia'])
                    update_order_metadata([str(value['order_id'])], '_logis_op_interno', value['paqueteria'])
                    if value['hijos'] is None:
                        r2 = asyncio.run(endpoint_update_status_by_order_id(value['order_id'], 'embarque'))
                    else:
                        childs_array = value['hijos'].split(', ')
                        if len(childs_array) > 0:
                            for order_id in childs_array:
                                update_order_metadata([str(order_id)], '_numero_guia_interno', value['numero_guia'])
                                update_order_metadata([str(order_id)], '_logis_op_interno', value['paqueteria'])
                                r2 = asyncio.run(endpoint_update_status_by_order_id(int(order_id), 'embarque'))
            st.session_state['orders_string'] = order_id_string
            st.session_state['child_list'] = objArray
            st.session_state['current_view'] = 'generar_guias_oax_final'
            st.rerun()
        

def UIgenerar_guias_final_oax(order_string, child_list):
    if len(child_list) == 1:
        st.write(f'## Se actualizó el pedido {order_string} al estado "Embarque" y se actualizó su número de guía y operador logístico')
    elif len(child_list) > 1:
        st.write(f'## Se actualizaron los pedidos {order_string} al estado "Embarque" y se actualizaron sus números de guía y operadores logísticos')
    st.write('---')
    if st.button('Regresar'):
        st.session_state['current_view'] = 'generar_guias_oax'
        st.rerun()
    