
import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productosValidados import insert_productos_validados,update_order_product_status
from db.db_UserInteractionEvents import event_instert
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
    st.session_state.current_view = 'detalleAuditoria'
    st.session_state['estadoUITP']=True
    st.session_state.disabled = True
    st.rerun()

def UITodosLosPedidos(data):
    df = pd.DataFrame(data)
    global df_data
    unique_values = df['Seller'].unique()
    unique_values_list = unique_values.tolist()
    unique_values_list.insert(0, "Todos los seller")
    if "estadoUITP" not in st.session_state:
        st.session_state['estadoUITP']=False
    
    if "disabled" not in st.session_state:
        st.session_state['disabled']=False
    if st.session_state.disabled == False:
        option = st.selectbox(
                "How would you like to be contacted?",
                unique_values_list,
                label_visibility="hidden",
                disabled=st.session_state.disabled,
                key="selectboxUITP",
            )

    if "optionsAuditoria" not in st.session_state:
        st.session_state['optionsAuditoria']="Todos los seller"
    else:
        if st.session_state['estadoUITP']==False:
            st.session_state['optionsAuditoria']=option
        else:
            if st.session_state['estadoUITP']==True:
                option=st.session_state['optionsAuditoria']

    if st.session_state['optionsAuditoria']=="Todos los seller" and st.session_state['estadoUITP']==False:
        st.session_state['optionsAuditoria']="Todos los seller"
        df_data = df
    else:
        options=[st.session_state['optionsAuditoria']]
        df_data = df[df['Seller'].isin([st.session_state['optionsAuditoria']])]
    
    st.header("Detalle ordenenes por Seller: "+st.session_state['optionsAuditoria'])
    if st.session_state.disabled == True:
        if st.button("Limpiar Filtro", key="habilitarOpcionesAuditoria"):
            st.session_state['estadoUITP']=False
            st.session_state.disabled = False
            st.session_state['optionsAuditoria']="Todos los seller"
            st.rerun()
    for i in range(len(df_data)):
        st.write("---")
        with st.container():
            col1, col2 = st.columns([4, 1])
            # Usar la primera columna para mostrar la información
            with col1:
                st.markdown(f"**Seller:** {df_data.iloc[i, 1]}")
                st.markdown(f"**Cantidad:** {int(df_data.iloc[i, 2])}")
                st.markdown(f"**Estado:** {df_data.iloc[i, 3]}")
            with col2:
                if st.button("Iniciar Auditoria", key=i):
                     EventName,EventAction,EventUser='picking','Se pulso en botón Iniciar Auditoria',st.session_state.useremail
                     event_instert(EventName,EventAction,EventUser)
                     ver_detalle(df_data.iloc[i, 0],df_data.iloc[i, 1],df_data.iloc[i, 2])



def UIDetallePedido(data_deta,idPedido):
    #estilos en los textos
    st.markdown("""
        <style>
        .flex-container {
            display: flex;
            align-items: center; /* Alinea los items verticalmente */
            justify-content: space-between; /* Espacio entre los elementos */
        }
        .nombre-producto {
            font-size:12px !important; 
            font-weight: bold; 
        }
        .sku-producto {
            font-size:12px !important;
            font-weight: bold; 
        }
        .cantidad{
            font-size:20px !important;
            font-weight: bold; 
        }
        .number-input-container > div {
            margin-top: 0px; /* Ajusta este valor según sea necesario */
        }
        </style>
        """, unsafe_allow_html=True)
    components.html(
            """
        <script>
        const elements = window.parent.document.querySelectorAll('.stNumberInput div[data-baseweb="input"] > div')
        console.log(elements)
        elements[1].display: none;
        </script>
        """,
            height=0,
            width=0,
        )
    # Título de la tabla
    st.subheader(f"Nombre del Seller: {st.session_state.nombreSeller}")
    # Botón para finalizar la recolección
    if st.button("Regresar la lista de pedidos"):
        #del st.session_state['data_deta']
        st.session_state.current_view = 'auditoria'
        st.rerun()
    # Espacio entre secciones
    st.write("---")
    # Inicializar una lista para los estados
    estados = []
    cantidad_pickeada =0

    df = pd.DataFrame(data_deta)
    objArry=[]
    header_col1, header_col2, header_col3, header_col4,header_col5 = st.columns([2, 3, 1, 1, 2])
    header_col1.write("")
    header_col2.write("**Producto**")
    header_col3.write("**Cantidad**")
    header_col4.write("**Auditado**") 
    header_col5.write("**Estado**") 
    for i, pedido in df.iterrows():
        print(pedido.Imagen)
        #col1, col2, col3, col4, col5 = st.columns(5)
        col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 2])

        with col1:
            if pedido.Imagen is not  None:
                st.image(pedido.Imagen, use_column_width=True)
            else:
                st.write("Sin imagen")

        with col2:
            st.markdown(f'<div class="flex-container"><div class="nombre-producto">Nombre: {pedido.Producto}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="flex-container"><div class="sku-producto">SKU: {pedido.SKU}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="flex-container"><div class="sku-producto">{pedido.units_per_pack}</div></div>', unsafe_allow_html=True)            
        with col3:
            st.markdown(f'<div class="flex-container"><div class="cantidad">{pedido.Cantidad}</div></div>', unsafe_allow_html=True)
            st.write("")  # Espacio extra

        with col4:
            #st.markdown('<div class="flex-container">', unsafe_allow_html=True)
            cantidad_pickeada = st.number_input(f"holwwwa", key=f"cantidad_{i}", value=0,min_value=0, max_value=int(pedido.Cantidad),label_visibility='hidden')
            #st.markdown('</div>', unsafe_allow_html=True)
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
                            "cantidad_sistema":int(pedido.Cantidad),"cantidad_nueva":cantidad_pickeada,"estado":estado,"seller_id":pedido.seller_id})

    auditoria=[]
    validacion=[]
    validacionSeller=[]
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
    print("len(objArry)")
    print(len(objArry))
    print(objArry)
    print("len(auditoria)")
    print(len(auditoria))
    print("len(validacion)")
    print(len(validacion))
    if len(auditoria)==len(objArry):
        respuesta_auditoria=ui.alert_dialog(show=trigger_btn, title="Confirmemos auditoría", description='Enviaremos el pedido a "Pedidos agrupar"\nConfirma si es lo que quisieras', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_auditoria")
        if respuesta_auditoria:
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','Se envio el pedido a "Pedidos agrupar"',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            with st.spinner(f'Actualizando estatus del pedido de {st.session_state.nombreSeller}'):
                order_status='agrupar-pedidos'
                #idPedido
                #para test '281660'
                r = asyncio.run(update_status_wordpress(idPedido, order_status))
                print("r")
                print(r)
                st.session_state.current_view = 'auditoria'
                st.rerun()
    else:
        respuesta_validacion=ui.alert_dialog(show=trigger_btn, title="Confirmemos auditoria", description='Enviaremos el pedido a "RECOLECTAR" cuando sea seller de bodega CDMX y en caso de no serlo enviaremos a "RECOLECCIÓN CON PROBLEMAS"\nConfirma si es lo que quisieras', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_validacion")
        if respuesta_validacion:
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','Se envio el pedido a "Validacion de Stock"',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            with st.spinner(f'Actualizando estatus del pedido de {st.session_state.nombreSeller}'):
                lineasCDMX = []
                lineasProblemas = []
                for objeto in objArry:
                    if objeto['estado'] == valor_estado_esperado:
                        if objeto['seller_id'] in ('3587', '998', '1352', '2636', '3759', '2751', '2166', '1663',  '7180', '7201', '7202', '6927'):
                            print("es de bodega CDMX")
                            #print(objeto['seller_id'])
                            ahora = datetime.now()
                            fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
                            insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'])
                            update_order_product_status(objeto['producto_id'],'wc-recolectar-2')
                            linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe audito {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
                            lineasCDMX.append(linea)
                        else:
                            print("recolección con problemas")
                            #print(objeto['seller_id'])
                            print("es de bodega CDMX")
                            #print(objeto['seller_id'])
                            ahora = datetime.now()
                            fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
                            insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'])
                            update_order_product_status(objeto['producto_id'],'rec-problem-2')
                            linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe audito {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
                            lineasProblemas.append(linea)

                        
                        if len(lineasCDMX)>0:
                            with st.spinner(f'Actualizano las notas del pedido para auditoria  en las bodegas CDMX {st.session_state.nombreSeller}'):
                                #idPedido
                                #para test '281660'
                                asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                                st.snow()
                        if len(lineasProblemas)>0:
                            with st.spinner(f'Actualizano las notas del pedido para auditoria  que tiene problemas de recolección {st.session_state.nombreSeller}'):
                                print("eneee")
                                #idPedido
                                #para test '281660'
                                asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                                st.snow()

                st.session_state.current_view = 'auditoria'
                st.rerun()
        

    
