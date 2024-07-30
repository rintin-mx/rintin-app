import sys
import time

from integration.cache_api import update_stock_by_sku
sys.path.append('..')
from typing import List
import streamlit as st
from st_mui_dialog import st_mui_dialog
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productos_validados import insert_productos_validados
from db.db_user_interaction_events import event_instert
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_searchbox import st_searchbox
from db.db_auditoria import get_order_auditoria, get_order_status, product_confirm_change
from db.db_confirmacion import get_seller_en_bodega
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
    st.session_state.current_view = 'detalleConfirmacion'
    st.session_state['estadoUITP']=True
    st.session_state.disabled = True
    st.rerun()

def orderMsjString(objeto):
    linea=''
    ahora = datetime.now()
    fecha_formato_mysql = ahora.strftime('%Y-%m-%d %H:%M:%S')
    fuente='confirmacion-validacion'
    insert_productos_validados(objeto['producto_id'], objeto['sku'], fecha_formato_mysql, objeto['order_id'], objeto['cantidad_sistema'], objeto['cantidad_nueva'],fuente,st.session_state.useremail, 'wc-prepara_pedido', 'wc-stock-2', 'No hay stock')
    linea = f"Producto: {objeto['nombre_producto']} - SKU: {objeto['sku']}\nSe confirmó {objeto['cantidad_nueva']} de {objeto['cantidad_sistema']}"
    return linea

def UIDetallePedido(data_deta,idPedido):
    st.subheader(f"Detalle de la orden: {idPedido}")
    st.info(f"Estado de la orden: {get_order_status(idPedido)}")
    if st.button("Regresar la lista de confirmación"):
            st.session_state.current_view = 'confirmacion'
            st.rerun()
    #estilos en los textos
    st.write("---")
    # Inicializar una lista para los estados
    estados = []
    cantidad_pickeada =0
    df = pd.DataFrame(data_deta)
    objArry=[]
    seller = ''
    seller_open = True

    for i, pedido in df.iterrows():
        cambio_prod = ''
        producto_reemplazo = ''
        #col1, col2, col3, col4, col5 = st.columns(5)
        col1, col2, col3, col4, col5 = st.columns([3, 3, 3, 3, 2])
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
            st.write("")  # Espacio extra

        with col4:
            cantidad_pickeada = st.number_input(f"Confirmados", key=f"cantidad_{i}", value=0,min_value=0, max_value=int(pedido.Cantidad))
            if(cantidad_pickeada != int(pedido.Cantidad)):    
                cambio_prod = st.selectbox(f"Opcion de reemplazo", ('No reemplazar', 'Reemplazar'), key=f"opcion_{i}")
                if(cambio_prod == 'Reemplazar'):
                    producto_reemplazo = st.text_input('Product_SKU', key=f"prod_reemplazo_{i}")

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
            if(cambio_prod == 'Reemplazar' and producto_reemplazo != ''):
                objArry.append({"order_id":pedido.order_id,"nombre_producto":pedido.Producto,"producto_id":pedido.product_id,
                            "sku":pedido.SKU,
                            "cantidad_sistema":int(pedido.Cantidad),"cantidad_nueva":cantidad_pickeada,"estado":estado,"seller_id":pedido.seller_id,
                            "producto_nuevo_sku":producto_reemplazo, "cantidad_reemplazada":int(pedido.Cantidad), "order_item_id":pedido.order_item_id})
            else:
                objArry.append({"order_id":pedido.order_id,"nombre_producto":pedido.Producto,"producto_id":pedido.product_id,
                            "sku":pedido.SKU,
                            "cantidad_sistema":int(pedido.Cantidad),"cantidad_nueva":cantidad_pickeada,"estado":estado,"seller_id":pedido.seller_id})
            
            if seller_open:
                seller = pedido.seller_id
                seller_open = False
        
        st.write('---')

    agrupacion=[]
    validacion=[]
    validacionStr = ''
    for i in range(len(objArry)):
        if objArry[i]['estado'] =='OK' or (objArry[i]['estado'] =='NO OK' and len(objArry[i]) > 8):
            agrupacion.append(objArry[i]['order_id'])
        else:
            validacion.append(objArry[i]['producto_id'])
            validacionStr = validacionStr + str(objArry[i]['sku']) + ', '
    trigger_btn = ui.button(text="Confirmar", key="trigger_btn")
    respuesta = False
    if len(agrupacion)==len(objArry):
        banner_text = 'Pedidos por agrupar'
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Auditoría", description=f'Todos los productos de la orden #{str(idPedido)} estan completos', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            st.toast('¡Orden guardada con éxito!')
            st.session_state.current_view = 'confirmacion'
            st.session_state.current_status = banner_text

            lineasProblemas = []
            i=0
            mssg = ''

            for objeto in objArry:
                    if objeto['estado'] == 'NO OK':
                        lineasProblemas.append(orderMsjString(objeto))
                        update_stock_by_sku(objeto['sku'], '0','validacion_stock')

                        # Si el producto es reemplazado, tiene más de 8 atributos al guardarlo en el ObjArray, 
                        # este condicional me permite identificar los reemplazados

                        if(len(objeto) > 8):
                            mssg += f"\nCambio SKU: {objeto['sku']} por {objeto['producto_nuevo_sku']}"
                            product_confirm_change(objeto['order_item_id'], objeto['producto_nuevo_sku'],objeto['cantidad_reemplazada'], time.strftime('%Y-%m-%d %H:%M:%S'))

            if len(lineasProblemas) > 0:
                    order_notes = "\n".join(lineasProblemas) + mssg
                    print(order_notes)
                    with st.spinner(f'Actualizano las notas del pedido para confirmación de seller  en las bodegas CDMX'):
                        asyncio.run(update_order_note__wordpress(idPedido, order_notes))

            sellers_in_bodega = get_seller_en_bodega(seller)

            print(f"------------{sellers_in_bodega['bodega'][0]}")
            if sellers_in_bodega['bodega'][0] == None:
                with st.spinner('Actualizando estado de orden a "preparacion pedidos unificados"'):
                        r = asyncio.run(update_status_wordpress(idPedido, 'prepara_pedido'))

            st.session_state.current_view = 'finalProcesoConfirmacion'
            st.session_state.productos_validacion = validacionStr
            st.rerun()
           
    else:
        validacionStr = validacionStr[:-2]
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de seller", description=f'Enviaremos los productos {validacionStr} de la orden #{idPedido} a validación de stock', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order_2")
        if respuesta:
            with st.spinner(f'Actualizando estado de los productos del pedido pedido a "Validación Stock"'):
                lineasProblemas = []
                i=0
                mssg = ''
                faltante_no_reemplazo = False       #Hay algun faltante que no necesita reemplazo? Empieza en F y se vuelve T si existe
                for objeto in objArry:
                    if objeto['estado'] == 'NO OK':
                        lineasProblemas.append(orderMsjString(objeto))
                        update_stock_by_sku(objeto['sku'], '0','validacion_stock')

                        # Si el producto es reemplazado, tiene más de 8 atributos al guardarlo en el ObjArray, 
                        # este condicional me permite identificar los reemplazados

                        if(len(objeto) > 8):
                            mssg += f"\nCambio SKU: {objeto['sku']} por {objeto['producto_nuevo_sku']}"
                            product_confirm_change(objeto['order_item_id'], objeto['producto_nuevo_sku'],objeto['cantidad_reemplazada'], time.strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            faltante_no_reemplazo = True

                if len(lineasProblemas) > 0:
                    order_notes = "\n".join(lineasProblemas) + mssg
                    print(order_notes)
                    with st.spinner(f'Actualizano las notas del pedido para confirmación de seller  en las bodegas CDMX'):
                        asyncio.run(update_order_note__wordpress(idPedido, order_notes))
                
                # if (Faltante no reemplazo/Faltante reemplazo)
                if(faltante_no_reemplazo):
                    with st.spinner('Actualizando estado de orden a "Validacion stock"'):
                        r = asyncio.run(update_status_wordpress(idPedido, 'stock-2'))
                else: 
                    with st.spinner('Actualizando estado de orden a "Recolectar"'):
                        r = asyncio.run(update_status_wordpress(idPedido, 'recolectar-2'))
                
            st.session_state.current_view = 'finalProcesoConfirmacion'
            st.session_state.productos_validacion = validacionStr
            st.rerun()

def UITFinalizarProceso(data, productList):
    
    st.markdown(f'## Se actualizaron algunos productos del pedido con número {data["id"][0]} al estado {get_order_status(data["id"][0])}')
    st.write('---')
    
    st.markdown(f'### Los productos son los siguientes: {productList}')

    if data["post_parent"][0] != data["id"][0]:
        st.markdown(f'### Su orden padre es: {data["post_parent"][0]}')
        st.write('---')
    
    if st.button('Regresar'):
        st.session_state['current_view'] = 'confirmacion'
        st.rerun()

def UITodosLosPedidos(data):
    df = pd.DataFrame(data)
    global df_data
    df_data=[]
    selected_value = ''
    if 'visible' not in st.session_state:
        st.session_state['visible'] = True
        st.rerun()
    if 'Order_id_confirmacion' not in st.session_state:
        st.session_state['Order_id_confirmacion'] = 0
        
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
            st.session_state['Order_id_confirmacion'] =int(selected_value)
            st.session_state['current_view'] = 'detalleConfirmacion'
            st.rerun()
        else:
            st.info('Debes seleccionar un order_id para continuar', icon="ℹ️")

            



