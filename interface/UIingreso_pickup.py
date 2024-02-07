import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from db.db_ingreso_pickup import get_orders
from integration.endpoint_wordpress import endpoint_update_status_by_order_id

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

def ingresoPickup(orders, orders_for_filter):
    st.write('## Pedidos a ingresar')
    orderParent = st.selectbox('Número de orden', options=orders_for_filter, index=None)
    if orderParent is not None:
        orders = orders[(orders['order_id'] == orderParent) | (orders['post_parent'] == orderParent)]
        print()
    orderArray = []
    order_str = ''
    print(orders)
    for i, order in orders.iterrows():
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write('**Order ID**')
            st.text(order['order_id'])
        with col2:
            st.write('**Seller ID**')
            st.text(order['seller_name'])
        with col3:
            st.write('**Status ID**')
            st.text(order['post_status'])
        with col4:
            st.write('**Paquetes**')
            st.text(order['num_paquetes'])
        with col5:
            st.write('**Ingresado**')
            agrupadoSeleccion = st.toggle('',key=f'recolectado{i}')
            if agrupadoSeleccion:
                orderArray.append(order['order_id'])
                order_str = order_str + str(order['order_id']) + ', '
        st.write('---')
    if len(orderArray) > 0:
        trigger_btn = ui.button(text="Ingresar", key="trigger_btn")
        order_str = order_str[:-2]
        respuesta = False
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de ingreso de pedidos", description=f'Enviaremos a "Recepción" \n Padre: {str(order["post_parent"])} \n Hijos: {order_str}', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner('Actualizando estado de las ordenes'):
                for order_id in orderArray:
                    r = asyncio.run(update_status_wordpress(order_id, 'recepcion-2'))
                st.session_state['orderList'] = orderArray
                st.session_state['orderListStr'] = order_str
                st.session_state['parentId'] = order['post_parent']
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
            
