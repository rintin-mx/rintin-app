
import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from db.db_UserInteractionEvents import event_instert
from db.db_productosValidados import update_order_product_status

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
            col1, col2, col3 = st.columns([4, 3, 2])
            with col1:
                st.markdown(f"**Orderid_:** {ordenes.order_id}")
                st.markdown(f"**Pedidos Activas:** {int(ordenes.ordenes_activas)}")
                st.markdown(f"**Pedidos Auditados:** {int(ordenes.pedidos_auditados)}")
                st.markdown(f"**En proceso:** {int(ordenes.en_proceso)}")
                st.markdown(f"**Estado:** {ordenes.estado}")
            with col3:
                if st.button("Agrupación", key=i):
                    EventName,EventAction,EventUser='picking','Se pulso en botón Iniciar Auditoria',st.session_state.useremail
                    event_instert(EventName,EventAction,EventUser)
                    ver_detalle(ordenes.order_id,ordenes.ordenes_activas,ordenes.pedidos_auditados,ordenes.en_proceso,ordenes.estado) 

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

    # En la segunda columna, puedes colocar otro elemento
    with col2:
        option = st.selectbox(
            'Tipos de envio',
            ('Seleccione tipo de envío','Envío a Cliente', 'Envío a Bodega'),
            label_visibility='collapsed')
    
    print("option")
    print(option)
    if option=='Envío a Bodega':
        numGuiaInterno = st.text_input('Número de guía interno', '')
        optioOperadorInterno = st.selectbox(
            'Operador logistico interno',
            ('Elije un operador', 'Estafeta', '99 MInutos', 
             'Ogramak', 'FEDEX', 'Redpack', 
             'Chavobus', 'Ogramak Caminon'), key='optioOperadorInterno')
    if option=='Envío a Cliente':
        numGuiaCliente = st.text_input('Número de guía cliente', '')
        optioOperadorCliente = st.selectbox(
            'Operador logistico cliente',
            ('Elije un operador', 'Estafeta', '99 MInutos', 
             'Ogramak', 'Redpack', 
             'FEDEX', 'Tiui'), key='optioOperadorCliente')

    # Espacio entre secciones
    st.write("---")
    # Inicializar una lista para los estados
    estados = []
    cantidad_pickeada =0

    df = pd.DataFrame(data)
    objArry=[]
    estadoSeleccion=''
    unique_values_list = ['Motivo A','Motivo B']
    header_col1, header_col2, header_col3, header_col4,header_col5 = st.columns([2, 2, 3, 3, 2])
    header_col1.write("**Pedido**")
    header_col2.write("**Seller**")
    header_col3.write("**Estado de la Orden**")
    header_col4.write("**Número Paquetes**") 
    header_col5.write("**Ingresado**") 
    for i, pedido in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 3, 2])
        print(pedido)
        with col1:
            st.write(pedido.order_id)
        with col2:
            st.write(pedido.seller_name)         
        with col3:
            st.write(pedido.estado)
        with col4:
             st.write(pedido.num_paquetes)
        with col5:
            agrupadoSeleccion = st.toggle('',key=f'recolectado{i}')
            if agrupadoSeleccion:
                estadoSeleccion='agrupado'
            else:
                estadoSeleccion='noagrupado'
            objArry.append({"order_id":pedido.order_id,"seller_name":pedido.seller_name,"estado":pedido.estado,
                            "num_paquetes":pedido.num_paquetes,
                            "agrupadoSeleccion":estadoSeleccion})
        
    agrupado=[]
    no_agrupado=[]
    for i in range(len(objArry)):
        if objArry[i]['agrupadoSeleccion'] =='agrupado':
            agrupado.append(objArry[i]['order_id'])
        else:
            no_agrupado.append(objArry[i]['order_id'])
    

    print(agrupado)
    print(no_agrupado)
    trigger_btn = ui.button(text="Agrupar", key="trigger_btn_agrupacion")
    flag=False
    if len(agrupado)>0:
        respuesta_agrupacion=ui.alert_dialog(show=trigger_btn, title="Confirmemos agrupación", description='Enviaremos el pedido a "Embarque"\nConfirma si es lo que quisieras', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_agrupacion")
        if respuesta_agrupacion:
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='Agrupación','Se envio el pedido a "Embarque"',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            with st.spinner(f'Actualizando estatus del pedido de {st.session_state.orderId} a Embarque...'):
                order_status='wc-embarque'
                for objeto in objArry:
                    print(objeto['agrupadoSeleccion'])
                    if objeto['agrupadoSeleccion']=='agrupado':
                        update_order_product_status(objeto['order_id'],order_status)
                #idPedido
                #para test '281660'
                #r = asyncio.run(update_status_wordpress(idPedido, order_status))
                #print("r")
                #print(r)
                #st.session_state.current_view = 'auditoria'
                #st.rerun()
    #if len(no_agrupado)>0:
    #if flag:
    #    st.session_state.current_view = 'auditoria'
    #    st.rerun()