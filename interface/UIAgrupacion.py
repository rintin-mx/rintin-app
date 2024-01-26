
import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from db.db_UserInteractionEvents import event_instert
from db.db_productosValidados import update_order_product_status
from db.db_order import insert_order_metadata
from st_mui_dialog import st_mui_dialog

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

def ver_detalle(id,pedidos_activos,pedidos_auditados,en_proceso,estado):

    st.session_state.orderId = id
    st.session_state.pedidos_activos = pedidos_activos
    st.session_state.pedidos_auditados = pedidos_auditados
    st.session_state.en_proceso = en_proceso
    st.session_state.estado_agrupacion = estado
    st.session_state.current_view = 'detalleAgrupacion'
    st.rerun()

def UIOrdenesAgrupar(data):
    st.header("Ordenes a agrupar")
    df_data=[]
    df = pd.DataFrame(data)
    print("df")
    print(df)
    options = st.multiselect(
    'Selecciones el estado',
     options=df['estado'].unique(),
     key='centro_padre')
    
    print("options")
    print(options)
    if len(options)>0:
        df_data =df[df['estado'].isin(options)]
    else:
        df_data = df

    for i, ordenes in df_data.iterrows():
        st.write("---")
        with st.container():
            col1, col3 = st.columns([5, 1])
            with col1:
                st.markdown(f"**Orden Padre:** {ordenes.order_id}")
                st.markdown(f"**Pedidos Activas:** {int(ordenes.ordenes_activas)}")
                st.markdown(f"**Pedidos Agrupados:** {int(ordenes.pedidos_auditados)}")
                st.markdown(f'**Hijos Agrupados:** {ordenes.hijos_auditados}')
                st.markdown(f"**En proceso:** {int(ordenes.en_proceso)}")
                st.markdown(f'**Hijos en proceso:** {ordenes.hijos_en_proceso}')
                st.markdown(f"**Estado:** {ordenes.estado}")
            with col3:
                if ordenes.estado == 'Agrupar':
                    if st.button("Agrupación", key=i):
                        EventName,EventAction,EventUser='agrupacion','Se pulso en botón Iniciar Agrupación',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                        ver_detalle(ordenes.order_id,ordenes.ordenes_activas,ordenes.pedidos_auditados,ordenes.en_proceso,ordenes.estado) 

def UITFinalizarProceso(parentId, childList, childListString):
    if len(childList) == 1:
        st.markdown(f'## Se actualizó el pedido #{parentId} al estado "Empaquetar"')
    elif len(childList) > 1:
        st.markdown(f'## Se actualizaron los pedidos con número {childListString} al estado "Empaquetar"')
        st.markdown(f'### Su orden padre es: {parentId}')
    st.write('---')
    if st.button('Regresar'):
        st.session_state['current_view'] = 'agrupacion'
        st.rerun()

def UIOrdenesAgruparDetalle(data,idPedido):
    st.header(f"Pedidos a agrupar: {st.session_state.orderId}")
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
        if st.button("Regresar la lista de agrupación"):
            st.session_state.current_view = 'agrupacion'
            st.rerun()
    
    # Espacio entre secciones
    st.write("---")
    # Inicializar una lista para los estados
    df = pd.DataFrame(data)
    objArry=[]
    estadoSeleccion=''
    for i, pedido in df.iterrows():
        col1, col2, col4, col5 = st.columns([2, 2, 3, 2])
        print(pedido)
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
                estadoSeleccion='agrupado'
            else:
                estadoSeleccion='noagrupado'
            objArry.append({"order_id":pedido.order_id,"seller_name":pedido.seller_name,
                            "num_paquetes":pedido.num_paquetes,
                            "agrupadoSeleccion":estadoSeleccion})
        st.write('---')
        
    agrupado=[]
    no_agrupado=[]
    agrupado_str = ''
    for i in range(len(objArry)):
        if objArry[i]['agrupadoSeleccion'] =='agrupado':
            agrupado.append(objArry[i]['order_id'])
            agrupado_str += str(objArry[i]['order_id']) + ', '
        else:
            no_agrupado.append(objArry[i]['order_id'])
    #proceos para los ids Padres
    respuesta = False
    if len(agrupado) == len(objArry):
        trigger_btn = ui.button(text="Empaquetar", key="trigger_btn")
        
        agrupado_str = agrupado_str[:-2]
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de agrupación", description=f'Enviaremos a "Empaquetar" \n Padre: {str(idPedido)} \n Hijos: {agrupado_str}', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")

    
    if respuesta:
        if len(agrupado)>0:
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='Agrupación','Se envio el pedido a "Empaquetar"',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            with st.spinner(f'Actualizando estatus de los pedidos a Empaquetar...'):
                order_status='empaquetar'
                for order_id in agrupado:
                    r = asyncio.run(update_status_wordpress(order_id, order_status))
                st.session_state['orderList'] = agrupado
                st.session_state['orderListStr'] = agrupado_str
            st.session_state.current_view = 'finalProcesoAgrupacion'
            st.rerun()
        else:
            print('+++++++++++++++++++++++++++++++++++++++')
            print('No se encontraron pedidos para agrupar')
            print('+++++++++++++++++++++++++++++++++++++++')  
            st.warning('No a agrupado ningun pedido, por esta razon no se actualizo el estatus del pedido a wc-embarque')

