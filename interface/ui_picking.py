
import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productos_validados import insert_productos_validados,update_order_product_status
from db.db_user_interaction_events import event_instert
from db.db_auditoria import get_product_changes
from datetime import datetime
import streamlit.components.v1 as components

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

async def update_order_note__wordpress(order_id, order_notes):
    result = await endpoint_write_order_note(order_id, order_notes)
    return result

def ver_detalle(id,nombre,estado):

    st.session_state.orderId = id
    st.session_state.nombreSeller = nombre
    st.session_state.estadoPedido = estado
    st.session_state.current_view = 'detalle'
    st.session_state['estadoUIP']=True
    st.session_state.disabledUIP = True
    st.rerun()

def UITodosLosPedidos(data, proveedores):
    df = pd.DataFrame(data)
    unique_proveedores_list = proveedores
    unique_values = df['Seller'].unique()
    unique_values_list = unique_values.tolist()
    if 'sellersPickearIndex' not in st.session_state:
        st.session_state['sellersPickearIndex'] = None
    if 'optionsPickearIndex' not in st.session_state:
        st.session_state['optionsPickearIndex'] = None
    option = st.selectbox(
            "Seller",
            unique_values_list,
            key="selectboxOption",
            index=st.session_state['sellersPickearIndex']
        )
    proveedor_select = st.selectbox(
            "Proveedor",
            unique_proveedores_list,
            key="selectboxPckerar",
            index=st.session_state['optionsPickearIndex']
        )
        
        
    if "optionsPickear" not in st.session_state:
        st.session_state['optionsPickear']=None
        st.session_state['optionsPickearIndex'] = None
    if "sellersPickear" not in st.session_state:
        st.session_state['sellersPickear'] = None
        st.session_state['sellersPickearIndex'] = None
    if proveedor_select is not None:
        st.session_state['optionsPickear'] = proveedor_select
        st.session_state['optionsPickearIndex'] = unique_proveedores_list.index(proveedor_select)
    else:
        st.session_state['optionsPickear'] = None
    if option is not None:
        st.session_state['sellersPickear'] = option
        st.session_state['sellersPickearIndex'] = unique_values_list.index(option)
    else:
        st.session_state['sellersPickear'] = None
    
    if st.session_state['sellersPickear'] is None:
        df_data = df
    else:
        df_data = df[df['Seller'].isin([st.session_state['sellersPickear']])]
        
    if st.session_state['optionsPickear'] is None:
        df_data = df_data
    else:
        df_data = df_data[df_data['proveedor'].str.contains(str(st.session_state['optionsPickear']))]
    if st.button('Limpiar filtros'):
        st.session_state['sellersPickear'] = None
        st.session_state['sellersPickearIndex'] = None
        st.session_state['optionsPickear']=None
        st.session_state['optionsPickearIndex'] = None
        st.rerun()
    for i in range(len(df_data)):
        st.write("---")
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 4])
            # Usar la primera columna para mostrar la información
            with col1:
                st.markdown(f"**Order_id:** {df_data.iloc[i, 0]}")
                st.markdown(f"**Proveedor:** {df_data.iloc[i, 2]}")
                st.markdown(f"**Seller:** {df_data.iloc[i, 1]}")
                st.markdown(f"**Estado:** {df_data.iloc[i, 3]}")
            with col2:
                if df_data.iloc[i, 4] > 0:
                    st.warning('Pedido pasó por recolección con problema')
                if df_data.iloc[i, 5] > 0:
                    st.warning('Pedido pasó por validación de stock')
            with col3:
                if st.button("Pickear", key=i):
                     EventName,EventAction,EventUser='picking','Se pulso en botón Pickear',st.session_state.useremail
                     event_instert(EventName,EventAction,EventUser)
                     ver_detalle(df_data.iloc[i, 0],df_data.iloc[i, 1],df_data.iloc[i, 2])
                
                    



def UIDetallePedido(data_deta,idPedido):
    #estilos en los textos


    # Título de la tabla
    st.subheader(f"Nombre del seller: {st.session_state.nombreSeller}")
    # Botón para finalizar la recolección
    if st.button("Regresar la lista de pedidos"):
        #del st.session_state['data_deta']
        st.session_state.current_view = 'pick'
        st.rerun()
    # Espacio entre secciones
    st.write("---")
    # Inicializar una lista para los estados
    estados = []
    cantidad_pickeada =0

    df = pd.DataFrame(data_deta)
    objArry=[]

    # Extrae los ids de las ordenes para buscar cambios en productos
    order_item_ids = ''
    for id in df["order_item_id"]:
        order_item_ids += f"{id}, "
    order_item_ids = order_item_ids[:-2]
    changed_list = get_product_changes(order_item_ids)

    for i, pedido in df.iterrows():
        st.write(f'### Proveedor: {pedido.proveedor}')
        #col1, col2, col3, col4, col5 = st.columns(5)
        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 2])

        # Busca si el producto tiene un sustituto
        has_substitute = False
        substitute = ''
        for prod in changed_list.iterrows():
            if(prod[1].order_item_id == pedido.order_item_id):
                has_substitute = True
                substitute = prod[1].nuevo_producto_sku

        with col1:
            if pedido.Imagen is not  None:
                st.image(pedido.Imagen, use_column_width=True)
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
            if pedido.Stock_Showroom != None:
                st.warning(f"**Stock en showroom:** {pedido.Stock_Showroom}")  #--------------

        with col4:
            cantidad_pickeada = st.number_input(f"Cantidad pickeada", key=f"cantidad_{i}", value=0,min_value=0, max_value=int(pedido.Cantidad))
        with col5:
            # Comparar si la cantidad ingresada es igual a la cantidad requerida
            if cantidad_pickeada == int(pedido.Cantidad):
                estado = 'Pedidos por auditar'
                st.success(estado)
            elif cantidad_pickeada > int(pedido.Cantidad):
                cantidad_pickeada=0
                estado = 'Validacion'
                st.error(estado)
            else:
                estado = 'Validacion'
                st.error(estado)
            estados.append(estado)
            objArry.append({"order_id":pedido.order_id,"nombre_producto":pedido.Producto,"producto_id":pedido.product_id,
                            "sku":pedido.SKU,
                            "cantidad_sistema":int(pedido.Cantidad),"cantidad_nueva":cantidad_pickeada,"estado":estado})
        st.write('---')
    auditoria=[]
    validacion=[]
    for i in range(len(objArry)):
        if objArry[i]['estado'] =='Pedidos por auditar':
            auditoria.append(objArry[i]['order_id'])
        else:
            validacion.append(objArry[i]['order_id'])
    valor_estado_esperado = "Validacion"
    lineasTest = []
    
    for objeto in objArry:
        if objeto['estado'] == valor_estado_esperado:
            linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe pickeo {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
            lineasTest.append(linea)
    
    
    order_notes = "\n".join(lineasTest)
    trigger_btn = ui.button(text="Confirmar Pickeo", key="trigger_btn")
    respuesta_auditoria=False
    respuesta_validacion=False
    if len(auditoria)==len(objArry):
        respuesta_auditoria=ui.alert_dialog(show=trigger_btn, title="Confirmemos el pickeo", description=f'Enviaremos el pedido #{str(idPedido)} a "Pedidos por auditar"\nConfirma si es lo que quisieras', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_auditoria")
        if respuesta_auditoria:
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','Se envio el pedido a "Pedidos por auditar"',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            with st.spinner(f'Actualizando estatus del pedido de {st.session_state.nombreSeller}'):
                order_status='pedidos_auditar'
                #idPedido
                #para test '281660'
                r = asyncio.run(update_status_wordpress(idPedido, order_status))
                st.session_state.current_view = 'pickFinal'
                st.session_state['currentOrderId'] = idPedido
                st.session_state['currentStatus'] = 'Pedidos por auditar'
                st.rerun()
    else:
        respuesta_validacion=ui.alert_dialog(show=trigger_btn, title="Confirmemos el pickeo", description=f'Enviaremos el pedido #{str(idPedido)} a "Validacion de Stock"\nConfirma si es lo que quisieras', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_validacion")
        if respuesta_validacion:
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','Se envio el pedido a "Validacion de Stock"',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            with st.spinner(f'Actualizando estatus del pedido de {st.session_state.nombreSeller}'):
                lineasTest = []
                for objeto in objArry:
                    if objeto['estado'] == valor_estado_esperado:
                        ahora = datetime.now()
                        fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
                        fuente='picking'
                        #descomentar para guardar en la base de datos
                        insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'],fuente, st.session_state.useremail, 'wc-recolectar-2', 'wc-stock-2', 'No hay stock')
                        update_order_product_status(objeto['sku'], 'validacion_stock')
                        linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe pickeo {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
                        lineasTest.append(linea)
                
                order_notes = "\n".join(lineasTest)
                order_status='stock-2'
                #idPedido
                #para test '281660'
                asyncio.run(update_status_wordpress(idPedido, order_status))
                st.snow()
            with st.spinner(f'Actualizano las notas del pedido de {st.session_state.nombreSeller}'):
                #idPedido
                #para test '281660'
                asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                st.snow()
                st.session_state.current_view = 'pickFinal'
                st.session_state['currentOrderId'] = idPedido
                st.session_state['currentStatus'] = 'Validacion de Stock'
                st.rerun()

def pickFinal(orderId, status):
    st.markdown(f'## Se actualizó el pedido #{orderId} al estado "{status}"')
    st.write('---')
    if st.button('Regresar'):
        st.session_state['current_view'] = 'pick'
        st.rerun()


    
