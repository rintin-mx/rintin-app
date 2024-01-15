
import sys
sys.path.append('..')
from typing import List
import streamlit as st
from st_mui_dialog import st_mui_dialog
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productosValidados import insert_productos_validados,update_order_product_status
from db.db_UserInteractionEvents import event_instert
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_searchbox import st_searchbox
from db.db_auditoria import get_order_auditoria
import random
from st_material_table import st_material_table
from st_mui_table import st_mui_table

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

def BodegaCDMX(objeto):
    print("---------------")
    print("es de bodega CDMX")
    print("---------------")
    linea=''
    ahora = datetime.now()
    fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
    fuente='auditoria-wc-recolectar-2'
    insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'],fuente,st.session_state.useremail)
    update_order_product_status(objeto['producto_id'],'wc-recolectar-2')
    linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe audito {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
    return linea
def problemasRecoleccion(objeto):
    print("---------------")
    print("es de problemas Recoleccion")
    print("---------------")
    linea=''
    ahora = datetime.now()
    fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
    fuente='auditoria-wc-recolectar-2'
    insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'],fuente,st.session_state.useremail)
    update_order_product_status(objeto['producto_id'],'rec-problem-2')
    linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe audito {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
    return linea

def UIDetallePedido(data_deta,idPedido):
    st.subheader(f"Detalle de la orden: {idPedido}")
    if st.button("Regresar la lista de auditoría"):
            st.session_state.current_view = 'agrupacion'
            st.rerun()
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
                estado = 'OK'
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
        if objArry[i]['estado'] =='OK':
            auditoria.append(objArry[i]['order_id'])
        else:
            validacion.append(objArry[i]['order_id'])
    print("auditoria")
    print(auditoria)
    print("validacion")
    print(validacion)
    valor_estado_esperado = "Validacion"
    lineasTest = []
    for objeto in objArry:
        if objeto['estado'] == valor_estado_esperado:
            linea = f"Productos {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe pickeo {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
            lineasTest.append(linea)
    answer=None
    answer_else=None
    if len(auditoria)==len(objArry):
        answer = st_mui_dialog(title="Confirmemos audotoria", 
                            content="Enviaremos el pedido a 'AUDITAR'", 
                            button_txt = "Auditar",
                            agreelabel="Confirmar",
                            abortlabel = "Volver",
                            transition_mode = "slide", 
                            slide_direction = "up",
                            adapt_width_dialog = True,
                            fullscreen = True,
                            width_dialog = "xl",
                            key='button_if'
                            )
        if answer!=None:
            if answer:
                with st.spinner(f'Actualizando estatus del pedido'):
                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','Se envio el pedido a "Pedidos agrupar"',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    order_status='agrupar-pedidos'
                    #idPedido
                    #para test '281660'
                    r = asyncio.run(update_status_wordpress(idPedido, order_status))
                    print("r")
                    print(r)
                    answer=None
                    if st.session_state['visible'] == True:
                        st.session_state['visible'] = False
                        st.session_state['current_view'] = 'detalleAuditoria'
                        st.rerun()
                        
                        #st.rerun()
        
    else:
        answer_else = st_mui_dialog(title="Confirmemos audotoria", 
                            content="Enviaremos el pedido a 'RECOLETAR' y a 'RECOLECCIÓN CON PROBLEMAS'", 
                            button_txt = "Auditar",
                            agreelabel="Confirmar",
                            abortlabel = "Volver",
                            transition_mode = "slide", 
                            slide_direction = "up",
                            key='button_else'
                            )
        if answer_else!=None:
            if answer_else:
                with st.spinner(f'Actualizando estatus del pedido'):
                    answer_else=None
                    lineasCDMX = []
                    lineasProblemas = []
                    i=0
                    for objeto in objArry:
                        print("---------------")
                        print(objeto['producto_id'])
                        print("---------------")
                        print(objeto['estado'])
                        print("---------------")
                        if objeto['estado'] == valor_estado_esperado:
                            print("---------------")
                            print(objeto['seller_id'])
                            print("---------------")
                            if objeto['seller_id'] in ('3587', '998', '1352', '2636', '3759', '2751', '2166', '1663',  '7180', '7201', '7202', '6927'):
                                lineasCDMX.append(BodegaCDMX(objeto))
                            else:
                                lineasProblemas.append(problemasRecoleccion(objeto))
                        else:
                            print("-----------------------------------------------------------------------------------")
                            print('aca va el else por que al mensi una item no viene con conel estado de la validacion')
                            print("-----------------------------------------------------------------------------------")
                            print("***************")
                            print(objeto)
                            print("***************")
                            if objeto['seller_id'] in ('3587', '998', '1352', '2636', '3759', '2751', '2166', '1663',  '7180', '7201', '7202', '6927'):
                                lineasCDMX.append(BodegaCDMX(objeto))
                            else:
                                lineasProblemas.append(problemasRecoleccion(objeto))


                    print('len(lineasCDMX)')
                    print(len(lineasCDMX))
                    print('len(lineasProblemas)')
                    print(len(lineasProblemas))
                    if len(lineasCDMX)>0:
                        print("lineasCDMX")
                        print(lineasCDMX)
                        order_notes = "\n".join(lineasCDMX)
                        with st.spinner(f'Actualizano las notas del pedido para auditoria  en las bodegas CDMX'):
                            print("bodegas CDMX")
                            #idPedido
                            #para test '281660'
                            asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                            st.snow()
                    if len(lineasProblemas)>0:
                        print("lineasProblemas")
                        print(lineasProblemas)
                        order_notes = "\n".join(lineasProblemas)
                        with st.spinner(f'Actualizano las notas del pedido para auditoria  que tiene problemas de recolección'):
                            print("problemas de recolección")
                            #idPedido
                            #para test '281660'
                            asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                            st.snow()

                    #if st.session_state['visible'] == True:
                    #    st.session_state['visible'] = False
                    #    st.session_state['current_view'] = 'detalleAuditoria'
                    #    st.rerun()
                    st.session_state['visible'] = False
                    st.session_state['current_view'] = 'detalleAuditoria'
                    st.rerun()



def UITodosLosPedidos(data):
    df = pd.DataFrame(data)
    global df_data
    df_data=[]
    selected_value = ''
    if 'visible' not in st.session_state:
        print("visible")
        st.session_state['visible'] = True
        st.rerun()
    if 'Order_id_auditoria' not in st.session_state:
        st.session_state['Order_id_auditoria'] = 0
        
    df['ID'] = df['ID'].astype(str)
    # function with list of labels
    def search_orderid(searchterm: str) -> List[any]:
        df_filtrado = df[df['ID'].str.contains(searchterm)|(df['Seller'].str.contains(searchterm))]
        print(df_filtrado)
        st.session_state['visible']=False
  
        return df_filtrado['ID'] if searchterm else []

    # pass search function to searchbox
    print("selected_value")
    print(selected_value)
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

            



