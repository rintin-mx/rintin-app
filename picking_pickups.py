import streamlit as st

from db.db_picking_pickups import get_ordenes_pickup, get_orders_for_filter, get_order_detail, checkForChildStatusses
from interface.ui_picking_pickups import UIpicking_pickups, UIpicking_detalle, UIpicking_final

def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'picking_pickups'
        if st.session_state.current_view in ('confirmar_baja_proveedor', 'detalle_ordenes_por_seller', 'conteo_stock_por_seller', 'finalizar_manejo_stock','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu','auditoria', 'ingresoOrdenesCompra', 'ordenesCompra', 'detalleOrdenCompra', 'ordenesCompraCsv', 'editOrdenesCompra', 'terminar_orden_compra'):
            st.session_state['current_view'] = 'picking_pickups'
        if st.session_state.current_view == 'picking_pickups':
            data = get_ordenes_pickup()
            order_ids = get_orders_for_filter()
            UIpicking_pickups(data, order_ids)
        elif st.session_state.current_view == 'picking_pickups_detalle':
            order_id = st.session_state.current_id
            parent_id = st.session_state.current_parent
            data = get_order_detail(order_id)
            UIpicking_detalle(data, order_id, parent_id)
        elif st.session_state.current_view == 'final_proceso_picking_pickups':
            order_id = st.session_state.current_id
            current_status = st.session_state.current_status
            data = checkForChildStatusses(order_id)
            UIpicking_final(data, current_status)
            
        