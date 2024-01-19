
import sys
sys.path.append('..')

import streamlit as st
import streamlit_shadcn_ui as ui
from db.db_ingresoOrdenesCompra import get_ordenes_compra, updateOrdenCompraStatus, insertFaults


def orderDetail(products):
    objArry=[]
    if st.button('Volver'):
        st.session_state['current_view'] = 'ingresoOrdenesCompra'
        st.rerun()
    ordenCompra = st.session_state['currentOrder']
    noIngresioOpt = ['No llego', 'Fallas']
    st.markdown('### Orden de Compra #' + str(ordenCompra['id_orden_compra']))
    st.markdown('### Seller: ' + str(ordenCompra['seller_name']))
    st.markdown('### Fecha de Creación: ' + str(ordenCompra['fecha_creacion']))
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 2, 2])
    with col1:
        st.markdown('Foto')
    with col2:
        st.markdown('Producto')
    with col3:
        st.markdown('Cantidad')
    with col4:
        st.markdown('Ingresados')
    with col5:
        st.markdown('Razón')
    for i in range(len(products['product_id'])):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 2, 2])
        with col1:
            if products['foto'][i] != '':
                st.image(products['foto'][i])
            else:
                st.text('Sin Imagen')
        with col2:
            st.text(products['nombre_producto'][i])
            st.text(products['sku_producto_wp'][i])
            st.text(products['units_per_pack'][i])
        with col3:
            st.markdown(f"### {products['line_paquetes'][i]}")
        with col4:
            number = st.number_input('Ingresados', key=str(products['product_id'][i]) + '_number', step=1)
            razon = None
            if number != products['line_paquetes'][i]:
                razon= st.selectbox('Ingresados', options=noIngresioOpt ,key=str(products['product_id'][i]) + '_select')
        with col5:
            if number != products['line_paquetes'][i]:
                st.error('Validacion')
            else:
                st.success('OK')
            objArry.append({'product_id': products['product_id'][i], 'validacion': number != products['line_paquetes'][i], 'qty': number, 'original_qty': products['line_paquetes'][i], 'razon': razon})
    products_validacion = []
    print(objArry)
    for i in range(len(objArry)):
        if objArry[i]['validacion']:
            products_validacion.append({
                'product_id': objArry[i]['product_id'],
                'razon': objArry[i]['razon'],
                'qty': objArry[i]['original_qty'] - objArry[i]['qty']
            })
    trigger_btn = ui.button(text="Confirmar Pickeo", key="trigger_btn")
    respuesta = False
    if len(products_validacion) > 0:
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Ingreso", description='Enviaremos la orden de compra a "Ingresado a bodega con faltantes"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner(f'Actualizando estado'):
                updateOrdenCompraStatus('ingresado_bodega_faltantes', ordenCompra['id_orden_compra'])
                insertFaults(products_validacion, ordenCompra['id_orden_compra'])
                st.session_state['current_view'] = 'ingresoOrdenesCompra'
                st.rerun()

    else:
        respuesta = ui.alert_dialog(show=trigger_btn, title="Confirmación de Ingreso", description='Enviaremos la orden de compra a "Ingresado a bodega"', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            with st.spinner(f'Actualizando estado'):
                updateOrdenCompraStatus('ingresado_bodega', ordenCompra['id_orden_compra'])
                st.session_state['current_view'] = 'ingresoOrdenesCompra'
                st.rerun()


        
    st.write(
            """<style>
            [data-testid="stHorizontalBlock"] {
                align-items: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )        
    
def orderSelector(sellers):
    st.markdown('### Ingreso Ordenes de Compra')
    if sellers is not None:
        currentSeller = st.selectbox('Selecciona el seller', sellers)
        orders = get_ordenes_compra(currentSeller)
        col1, col2, col3, col4= st.columns([1, 2, 2, 2])
        with col1:
            st.markdown('#### ID')
        with col2:
            st.markdown('#### Fecha creación')
        with col3:
            st.markdown('#### Costo Total')
        st.write('---')
        for i in range(len(orders['id_orden_compra'])):
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            with col1:
               st.text(str(orders['id_orden_compra'][i]))
            with col2:
                st.text(orders['fecha_creacion'][i])
            with col3:
                st.text(str(orders['total_cost'][i]))
            with col4:
                if st.button('Ingresar', key=orders['id_orden_compra'][i]):
                    tempOrder = {
                        'id_orden_compra': orders['id_orden_compra'][i],
                        'seller_name': orders['seller_name'][i],
                        'fecha_creacion': orders['fecha_creacion'][i],
                        'total_cost': orders['total_cost'][i],
                        'total_paquetes': orders['total_paquetes'][i]
                    }
                    st.session_state['currentOrder'] = tempOrder
                    st.session_state['current_view'] = 'ingresoOrdenesDetalle'
                    st.rerun()
            st.write('---')

        st.write(
            """<style>
            [data-testid="stHorizontalBlock"] {
                align-items: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.text('No hay ordenes de compra en este momento')
    