import streamlit as st
from db.db_ingresoOrdenesCompra import get_live_sellers, get_products
from interface.UIingresoOrdenesCompra import orderSelector, orderDetail

def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'ingresoOrdenesCompra'
        if st.session_state.current_view in('empaquetado','pick', 'auditoria', 'recolect', 'ordenesAgrupar', 'ordenesCompraMenu', 'agrupacion', 'ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra', 'detalleOrdenCompra'):
            st.session_state['current_view'] = 'ingresoOrdenesCompra'
        if st.session_state['current_view'] == 'ingresoOrdenesCompra':
            if 'currentOrder' in st.session_state:
                del st.session_state['currentOrder']
            sellers = get_live_sellers()
            if sellers is not None:
                sellers = sellers['seller_name']
            orderSelector(sellers)
        if st.session_state['current_view'] == 'ingresoOrdenesDetalle':
            products = get_products(str(st.session_state['currentOrder']['id_orden_compra']))
            orderDetail(products)
            
        