import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from db.db_ingreso_pickup import get_order_detalle
from integration.endpoint_wordpress import endpoint_update_status_by_order_id

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

def ingresoPickup(data):
    st.write('## Pedidos a ingresar')
    orderParent = st.selectbox('Orden padre', options=data['post_parent'], index=None)
    orderArray = []
    order_str = ''
    if orderParent is not None:
        orders = get_order_detalle(orderParent)
        for i in range(len(orders['order_id'])):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write('**Order ID**')
                st.text(orders['order_id'][i])
            with col2:
                st.write('**Seller ID**')
                st.text(orders['seller_name'][i])
            with col3:
                st.write('**Status ID**')
                st.text(orders['post_status'][i])
            with col4:
                st.write('**Paquetes**')
                st.text(orders['num_paquetes'][i])
            with col5:
                st.write('**Ingresado**')
                agrupadoSeleccion = st.toggle('',key=f'recolectado{i}')
                if agrupadoSeleccion:
                    orderArray.append(orders['order_id'][i])
                    order_str = order_str + str(orders['order_id'][i]) + ', '
            st.write('---')
        if len(orderArray) == len(orders['order_id']):
            trigger_btn = ui.button(text="Ingresar", key="trigger_btn")
            order_str = order_str[:-2]
            respuesta = False
            respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de ingreso de pedidos", description=f'Enviaremos a "Recepción" \n Padre: {str(orderParent)} \n Hijos: {order_str}', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
            if respuesta:
                with st.spinner('Actualizando estado de las ordenes'):
                    for order_id in orderArray:
                        r = asyncio.run(update_status_wordpress(order_id, 'recepcion-2'))
                    st.session_state['orderList'] = orderArray
                    st.session_state['orderListStr'] = order_str
                    st.session_state['parentId'] = orderParent
                st.session_state.current_view = 'ingresoPickupFinal'
                st.rerun()

def finalizarProceso(parentId, childList, childListString):
    if len(childList) == 1:
        st.markdown(f'## Se actualizó el pedido #{parentId} al estado "Recepción"')
    elif len(childList) > 1:
        st.markdown(f'## Se actualizaron los pedidos con número {childListString} al estado "Recepción"')
        st.markdown(f'### Su orden padre es: {parentId}')
    st.write('---')
    if st.button('Regresar'):
        st.session_state['current_view'] = 'ingresoPickup'
        st.rerun()
            
