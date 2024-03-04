
import sys
sys.path.append('..')

from integration.insert_to_S3 import insertImage
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_user_interaction_events import event_instert
from datetime import datetime
from db.db_productos_validados import insert_productos_validados,update_order_product_status
import asyncio

import base64

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

async def update_order_note__wordpress(order_id, order_notes):
    result = await endpoint_write_order_note(order_id, order_notes)
    return result

def orderMsjString(objeto, status):
    linea=''
    ahora = datetime.now()
    fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
    fuente='auditoria-wc-recolectar-2'
    insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'],fuente,st.session_state.useremail, 'wc-auditoria-2', 'wc-' + status, 'No hay stock')
    update_order_product_status(objeto['producto_id'],'validacion')
    linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe pickeo {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
    return linea

def UIpicking_detalle(order_info, order_id, orden_padre):
    st.subheader(f"Detalle de la orden: {order_id}")
    if orden_padre != 0:
        st.subheader(f"Orden padre: {orden_padre}")
    if st.button("Regresar la lista de picking pickups"):
        st.session_state.current_view = 'auditoria'
        st.rerun()
    #estilos en los textos
    st.write("---")
    # Inicializar una lista para los estados
    estados = []
    cantidad_pickeada =0
    df = pd.DataFrame(order_info)
    objArry=[]
    for i, pedido in df.iterrows():
        #col1, col2, col3, col4, col5 = st.columns(5)
        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 3])
        with col1:
            if pedido.Imagen is not  None:
                st.image(pedido.Imagen, use_column_width=True )
            else:
                st.write("Sin imagen")

        with col2:
            st.markdown(f'##### Nombre: {pedido.Producto}')
            st.markdown(f'##### SKU: {pedido.SKU}')
            st.markdown(f'##### Unidades: {pedido.units_per_pack}')            
        with col3:
            st.markdown(f'##### Cantidad: {pedido.Cantidad}')
            st.write("")  # Espacio extra

        with col4:
            cantidad_pickeada = st.number_input(f"Validado", key=f"cantidad_{i}", value=0,min_value=0, max_value=int(pedido.Cantidad))
        with col5:
            # Comparar si la cantidad ingresada es igual a la cantidad requerida
            if cantidad_pickeada == int(pedido.Cantidad):
                estado = 'OK'
                st.success(estado)
            elif cantidad_pickeada > int(pedido.Cantidad):
                cantidad_pickeada=0
                estado = 'NO OK'
                st.error(estado)
            else:
                estado = 'NO OK'
                st.error(estado)
        estados.append(estado)
        objArry.append({"order_id":pedido.order_id,"nombre_producto":pedido.Producto,"producto_id":pedido.product_id,
                            "sku":pedido.SKU,
                            "cantidad_sistema":int(pedido.Cantidad),"cantidad_nueva":cantidad_pickeada,"estado":estado})
        st.write('---')
    recepcion=[]
    validacion=[]
    for i in range(len(objArry)):
        if objArry[i]['estado'] =='OK':
            recepcion.append(objArry[i]['order_id'])
        else:
            validacion.append(objArry[i]['order_id'])
    trigger_btn = ui.button(text="Confirmar pickeo", key="trigger_btn")
    respuesta = False
    if len(recepcion)==len(objArry):
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Recepción", description=f'Enviaremos el pedido #{str(order_id)} a "Recepción"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner(f'Actualizando estado del pedido a "Pedidos por agrupar"'):
                if st.session_state.useremail is not None:
                    EventName,EventAction,EventUser='picking_pickups','Se envio el pedido a "Recepción"',st.session_state.useremail
                    event_instert(EventName,EventAction,EventUser)
                r = asyncio.run(update_status_wordpress(order_id, 'recepcion-2'))
            st.session_state.current_view = 'final_proceso_picking_pickups'
            st.session_state.current_status = 'Recepción'
            st.rerun()
    else:
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Validación", description=f'Enviaremos el pedido #{order_id} a "Validación de stock"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order_2")
        if respuesta:
            with st.spinner(f'Actualizando estado del pedido a "Validación stock"'):
                lineasProblemas = []
                i=0
                for objeto in objArry:
                    if objeto['estado'] == 'NO OK':
                        lineasProblemas.append(orderMsjString(objeto, 'stock-2'))
                if len(lineasProblemas) > 0:
                    order_notes = "\n".join(lineasProblemas)
                    with st.spinner(f'Actualizano las notas del pedido para auditoria  en las bodegas CDMX'):
                        asyncio.run(update_order_note__wordpress(order_id, order_notes))
                r = asyncio.run(update_status_wordpress(order_id, 'stock-2'))
            st.session_state.current_view = 'final_proceso_picking_pickups'
            st.session_state.current_status = "Validación stock"
            st.rerun()

def UIpicking_final(data, currentStatus):
    grouped = data['num_agrupados'][0]
    childs = data['childs'][0]
    if childs == grouped and childs == 1:
        text = 'Es pedido único, ahora debes imprimir bitácora y empaquetar'
    elif childs == grouped and childs > 1:
        text = 'Es el último pedido, ahora debes Agrupar y Empaquetar'
    elif grouped < childs and grouped > 0 and grouped != 1:
        text = 'Este pedido ya tiene órdenes en agrupar, ahora debes Agruparlo'
    else:
        text = 'Este es el primer pedido, ahora debes imprimir bitácora y abrir espacio para orden completa'
    st.markdown(f'## Se actualizó el pedido con número {data["id"][0]} al estado "{currentStatus}"')
    st.write('---')
    
    if currentStatus == 'Recepción':
        st.markdown(f'### {text}')
    if data["post_parent"][0] != data["id"][0]:
        st.markdown(f'### Su orden padre es: {data["post_parent"][0]}')
        st.write('---')
    
    if st.button('Regresar'):
        st.session_state['current_view'] = 'picking_pickups'
        st.rerun()

def UIpicking_pickups(data, order_ids):
    print(data)
    st.write(' ## Picking - Pickups')
    if data is None:
        st.write(' ### No hay ordenes para pickear')
    else:
        filter_value = st.selectbox('Orden ID', options=order_ids['order_id'], index=None)
        if filter_value is not None:
            filtered_data = data[(data['order_id'] == filter_value) | (data['post_parent'] == filter_value)]
        else:
            filtered_data = data
        st.write('---')
        for i, pedido in filtered_data.iterrows():
            col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
            with col1:
                st.write(f'**Orden hijo:** {pedido.order_id}')
            with col2:
                st.write(f'**Estado:** {pedido.estado}')
            with col3:
                st.write(f'**Seller:** {pedido.seller_name}')
            with col4:
                if st.button('Pickear', key=i):
                    st.session_state['current_id'] = pedido.order_id
                    st.session_state['current_parent'] = pedido.post_parent
                    st.session_state['current_view'] = 'picking_pickups_detalle'
                    st.rerun()
            
            st.write('---')
                
        
        