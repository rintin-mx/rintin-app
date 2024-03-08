
import sys
sys.path.append('..')
from typing import List
import streamlit as st
from st_mui_dialog import st_mui_dialog
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productos_validados import insert_productos_validados,update_order_product_status
from db.db_user_interaction_events import event_instert
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_searchbox import st_searchbox
from db.db_auditoria import get_order_auditoria, get_product_changes
import random
from st_material_table import st_material_table
from st_mui_table import st_mui_table

noAuditoriaOpt = ['No llego', 'Llego otro producto']

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

async def update_order_note__wordpress(order_id, order_notes):
    result = await endpoint_write_order_note(order_id, order_notes)
    return result

def ver_detalle(order_id,seller_id,seller_name,num_paquetes,estado):
    #'order_id','seller_id','seller_name', 'num_paquetes','estado'
    st.session_state.orderId = order_id
    st.session_state.sellerid = seller_id
    st.session_state.nombreSeller = seller_name
    st.session_state.estadoPedido = estado
    st.session_state.num_paquetes =num_paquetes
    st.session_state.current_view = 'detalleAuditoria'
    st.session_state['estadoUITP']=True
    st.session_state.disabled = True
    st.rerun()

def orderMsjString(objeto, status):
    linea=''
    ahora = datetime.now()
    fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
    fuente='auditoria-wc-recolectar-2'
    insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'],fuente,st.session_state.useremail, 'wc-auditoria-2', 'wc-' + status, objeto['razon'])
    if objeto['otro_producto'] == '':
        linea = f"Producto: {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe audito {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}\nRazón de diferencia: {objeto['razon']}"
    else:
        linea = f"Producto: {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe audito {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}\nRazón de diferencia: {objeto['razon']}\nProducto que llegó: {objeto['otro_producto']}"
    return linea

def UIDetallePedido(data_deta,idPedido):
    st.subheader(f"Detalle de la orden: {idPedido}")
    if st.button("Regresar la lista de auditoría"):
            st.session_state.current_view = 'auditoria'
            st.rerun()
    #estilos en los textos
    st.write("---")
    # Inicializar una lista para los estados
    estados = []
    cantidad_pickeada =0
    bodega = data_deta['bodega'][0]
    
    if bodega == 'centro_cdmx':
        banner_text = 'Recolectar'
        banner_status = 'recolectar-2'
    else:
        banner_text = 'Recolección con problemas'
        banner_status = 'rec-problem-2'
    df = pd.DataFrame(data_deta)
    objArry=[]

    # agrupa los order_item_id de los productos
    order_item_ids = ''
    for id in df["order_item_id"]:
        order_item_ids += f"{id}, "
    order_item_ids = order_item_ids[:-2]

    # obtiene la lista de los productos con reemplazo
    changed_list = get_product_changes(order_item_ids)

    for i, pedido in df.iterrows():
        #col1, col2, col3, col4, col5 = st.columns(5)
        has_substitute = False
        substitute = ''
        for prod in changed_list.iterrows():
            if(prod[1].order_item_id == pedido.order_item_id):
                has_substitute = True
                substitute = prod[1].nuevo_producto_sku

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
            if has_substitute:
                st.warning(f'##### SKU de reemplazo: {substitute}')
            
            st.write("")  # Espacio extra

        with col4:
            cantidad_pickeada = st.number_input(f"Auditado", key=f"cantidad_{i}", value=0,min_value=0, max_value=int(pedido.Cantidad))
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
            otro_producto = ''
            razon = None
            if cantidad_pickeada < int(pedido.Cantidad):
                razon= st.selectbox('Razon no auditoria', options=noAuditoriaOpt ,key=str(pedido.product_id) + '_select')
                if razon == 'Llego otro producto':
                    otro_producto = st.text_input('Producto que ingresó', key=str(pedido.product_id) + '_nuevo_producto')


        estados.append(estado)
        objArry.append({"order_id":pedido.order_id,"nombre_producto":pedido.Producto,"producto_id":pedido.product_id,
                            "sku":pedido.SKU,
                            "cantidad_sistema":int(pedido.Cantidad),"cantidad_nueva":cantidad_pickeada,"estado":estado,"seller_id":pedido.seller_id,"razon": razon, "otro_producto": otro_producto})
        st.write('---')
    agrupacion=[]
    recolec=[]
    for i in range(len(objArry)):
        if objArry[i]['estado'] =='OK':
            agrupacion.append(objArry[i]['order_id'])
        else:
            recolec.append(objArry[i]['order_id'])
    trigger_btn = ui.button(text="Auditar", key="trigger_btn")
    respuesta = False
    if len(agrupacion)==len(objArry):
        banner_text = 'Pedidos por agrupar'
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Auditoría", description=f'Enviaremos el pedido #{str(idPedido)} a "{banner_text}"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner(f'Actualizando estado del pedido a "Pedidos por agrupar"'):
                if st.session_state.useremail is not None:
                    EventName,EventAction,EventUser='picking','Se envio el pedido a "Pedidos agrupar"',st.session_state.useremail
                    event_instert(EventName,EventAction,EventUser)
                banner_status='agrupar-pedidos'
                r = asyncio.run(update_status_wordpress(idPedido, banner_status))
            st.session_state.current_view = 'finalProceso'
            st.session_state.current_status = banner_text
            st.rerun()
           
    else:
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Auditoría", description=f'Enviaremos el pedido #{idPedido} a "{banner_text}"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order_2")
        if respuesta:
            with st.spinner(f'Actualizando estado del pedido a "{banner_text}"'):
                lineasProblemas = []
                i=0
                for objeto in objArry:
                    if objeto['estado'] == 'NO OK':
                        lineasProblemas.append(orderMsjString(objeto, banner_status))
                if len(lineasProblemas) > 0:
                    order_notes = "\n".join(lineasProblemas)
                    with st.spinner(f'Actualizano las notas del pedido para auditoria  en las bodegas CDMX'):
                        asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                r = asyncio.run(update_status_wordpress(idPedido, banner_status))
            st.session_state.current_view = 'finalProceso'
            st.session_state.current_status = banner_text
            st.rerun()

def UITFinalizarProceso(data, currentStatus):
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
    
    if currentStatus == 'Pedidos por agrupar':
        st.markdown(f'### {text}')
    if data["post_parent"][0] != data["id"][0]:
        st.markdown(f'### Su orden padre es: {data["post_parent"][0]}')
        st.write('---')
    
    if st.button('Regresar'):
        st.session_state['current_view'] = 'auditoria'
        st.rerun()

def UITodosLosPedidos(data):
    
    df = pd.DataFrame(data)
    if len(df) > 0:
        global df_data
        df_data=[]
        selected_value = ''
        if 'visible' not in st.session_state:
            st.session_state['visible'] = True
            st.rerun()
        if 'Order_id_auditoria' not in st.session_state:
            st.session_state['Order_id_auditoria'] = 0
            
        df['ID'] = df['ID'].astype(str)
        # function with list of labels
        def search_orderid(searchterm: str) -> List[any]:
            df_filtrado = df[df['ID'].str.contains(searchterm)|(df['Seller'].str.contains(searchterm))]
            st.session_state['visible']=False
    
            return df_filtrado['ID'] if searchterm else []

        # pass search function to searchbox
        selected_value = st_searchbox(
            label='Buscar por ID o Seller',
            search_function=search_orderid,
            key=f"search_orderid",
            rerun_on_update=True
        )
        submit = st.button("Buscar")
        st_mui_table(df)
        

        if submit:
            if selected_value is not None:
                st.session_state['Order_id_auditoria'] =int(selected_value)
                st.session_state['current_view'] = 'detalleAuditoria'
                st.rerun()
            else:
                st.info('Debes seleccionar un order_id para continuar', icon="ℹ️")
    else:
        st.write('### No hay ordenes por auditar')

            



