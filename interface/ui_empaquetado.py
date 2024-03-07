
import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from db.db_user_interaction_events import event_instert


async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

def ver_detalle(id,pedidos_activos,pedidos_agrupados,en_proceso,estado):

    st.session_state.orderId = id
    st.session_state.pedidos_activos = pedidos_activos
    st.session_state.pedidos_agrupados = pedidos_agrupados
    st.session_state.en_proceso = en_proceso
    st.session_state.estado_agrupacion = estado
    st.session_state.current_view = 'detalleEmpaquetado'
    st.rerun()

def UIOrdenesEmpaquetar(data, orders_for_filter):
    st.header("Ordenes a empaquetar")
    df_data=[]
    df = pd.DataFrame(data)

    filter_value = st.selectbox(
    'Selecciona el número de orden',
     options=orders_for_filter,
     key='centro_padre',
     index=None)

    if filter_value is not None:
        df_data = df[(df['order_id'] == int(filter_value)) | (df['hijos_agrupados'].str.contains(filter_value)) | (df['hijos_en_proceso'].str.contains(filter_value))]
    else:
        df_data = df

    if len(df_data) > 0:
        for i, ordenes in df_data.iterrows():
            st.write("---")
            with st.container():
                col1, col3 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**Orden Padre:** {ordenes.order_id}")
                    st.markdown(f"**Pedidos Activas:** {int(ordenes.ordenes_activas)}")
                    st.markdown(f"**Pedidos Agrupados:** {int(ordenes.pedidos_agrupados)}")
                    st.markdown(f'**Hijos Agrupados:** {ordenes.hijos_agrupados}')
                    st.markdown(f"**En proceso:** {int(ordenes.en_proceso)}")
                    st.markdown(f'**Hijos en proceso:** {ordenes.hijos_en_proceso}')
                    st.markdown(f"**Estado:** {ordenes.estado}")
                with col3:
                    if ordenes.estado == 'Empaquetar':
                        if st.button("Empaquetado", key=i):
                            EventName,EventAction,EventUser='empaquetado','Se pulso en botón Iniciar Empaquetado',st.session_state.useremail
                            event_instert(EventName,EventAction,EventUser)
                            ver_detalle(ordenes.order_id,ordenes.ordenes_activas,ordenes.pedidos_agrupados,ordenes.en_proceso,ordenes.estado) 
    else:
        st.markdown('### No hay ordenes.')

def UITFinalizarProceso(parentId, childList, childListString):
    if len(childList) == 1:
        st.markdown(f'## Se actualizó el pedido #{parentId} al estado "Generar Guía"')
    elif len(childList) > 1:
        st.markdown(f'## Se actualizaron los pedidos con número {childListString} al estado "Generar Guía"')
        st.markdown(f'### Su orden padre es: {parentId}')
    st.write('---')
    if st.button('Regresar'):
        st.session_state['current_view'] = 'empaquetado'
        st.rerun()

def UIOrdenesEmpaquetarDetalle(data,idPedido):
    st.header(f"Pedidos a empaquetar: {st.session_state.orderId}")
    st.markdown(
    """
    <style>
    .stButton>button {
        height: 3em;     /* Ajusta la altura del botón */
    }
    .stSelectbox {
        height: 3em; /* Ajusta la altura del selectbox para que coincida con el botón */
    }
    /* Ajustes adicionales de CSS aquí si es necesario */
    </style>
    """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 2])
    option=''
    # En la primera columna, puedes colocar un elemento
    with col1:
        if st.button("Regresar la lista de empaquetado"):
            st.session_state.current_view = 'empaquetado'
            st.rerun()
    
    # Espacio entre secciones
    st.write("---")
    # Inicializar una lista para los estados
    df = pd.DataFrame(data)
    objArry=[]
    estadoSeleccion=''
    for i, pedido in df.iterrows():
        col1, col2, col4, col5 = st.columns([2, 2, 3, 2])
        with col1:
            st.write("**Pedido**")
            st.write(pedido.order_id)
        with col2:
            st.write("**Seller**")
            st.write(pedido.seller_name)         
        with col4:
            st.write("**Número Paquetes**") 
            st.text(int(pedido.num_paquetes))
        with col5:
            st.write("**Ingresado**") 
            agrupadoSeleccion = st.toggle('',key=f'recolectado{i}')
            if agrupadoSeleccion:
                estadoSeleccion='empaquetado'
            else:
                estadoSeleccion='noempaquetado'
            objArry.append({"order_id":pedido.order_id,"seller_name":pedido.seller_name,
                            "num_paquetes":pedido.num_paquetes,
                            "agrupadoSeleccion":estadoSeleccion})
        st.write('---')
        
    empaquetado=[]
    no_empaquetado=[]
    empaquetado_str = ''
    for i in range(len(objArry)):
        if objArry[i]['agrupadoSeleccion'] =='empaquetado':
            empaquetado.append(objArry[i]['order_id'])
            empaquetado_str += str(objArry[i]['order_id']) + ', '
        else:
            no_empaquetado.append(objArry[i]['order_id'])
    #proceos para los ids Padres

    
    respuesta = False
    if (len(empaquetado) == len(objArry)):
        trigger_btn = ui.button(text="Empaquetar", key="trigger_btn")
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de empaquetado", description=f'Enviaremos a "Generar Guía" \n Padre: {str(idPedido)} \n Hijos: {empaquetado_str}', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        empaquetado_str = empaquetado_str[:-2]


    if respuesta:
        if len(empaquetado)>0:
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='empaquetado','Se envio el pedido a "Generar Guía"',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            with st.spinner(f'Actualizando estatus de los pedidos a Generar Guía...'):
                order_status='generar_guia'
                for order_id in empaquetado:
                    r = asyncio.run(update_status_wordpress(order_id, order_status))
                st.session_state['orderList'] = empaquetado
                st.session_state['orderListStr'] = empaquetado_str
            st.session_state.current_view = 'finalProcesoEmpaquetado'
            st.rerun()
        else:
            st.warning('No se ha empaquetado ningún pedido.')

