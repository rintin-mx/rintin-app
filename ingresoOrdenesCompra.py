import streamlit as st
from db.db_ingresoOrdenesCompra import get_live_sellers, get_products, get_pending_products
from interface.UIingresoOrdenesCompra import orderSelector, orderDetail

def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'ingresoOrdenesCompra'
        if st.session_state.current_view in('generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'ingresoOrdenesCompra'
        if st.session_state['current_view'] == 'ingresoOrdenesCompra':
            if 'currentOrder' in st.session_state:
                del st.session_state['currentOrder']
            sellers = get_live_sellers()
            if sellers is not None:
                sellers = sellers['seller_name']
            orderSelector(sellers)
        if st.session_state['current_view'] == 'ingresoOrdenesDetalle':
            if st.session_state['currentOrder']['estado'] == 'ingresado_bodega_pendientes':
                products = get_pending_products(str(st.session_state['currentOrder']['id_orden_compra']))
            else:
                products = get_products(str(st.session_state['currentOrder']['id_orden_compra']))
            orderDetail(products)
            
        