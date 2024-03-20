import streamlit as st
import pandas as pd
from db.db_ingreso_pickup import get_orders
from interface.ui_ingreso_pickup import ingresoPickup, finalizarProceso

def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'ingresoPickup'
        if st.session_state.current_view in('ingreso_pedidos_pickups','pendiente_entrega_pickup','bitacora_pickup','validar_entrega','finalizar_entrega','confirmar_baja_proveedor', 'detalle_ordenes_por_seller', 'conteo_stock_por_seller', 'finalizar_manejo_stock','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv', 'ingresoOrdenesDetalle'):
            st.session_state['current_view'] = 'ingresoPickup'
        if st.session_state['current_view'] == 'ingresoPickup':
            orders = get_orders()
            orders_dict = orders.to_dict(orient='list')
            orders_for_filter = set(orders_dict['order_id'] + orders_dict['post_parent'])
            ingresoPickup(orders, orders_for_filter)
        elif st.session_state['current_view'] == 'ingresoPickupFinal':
            parentId = st.session_state.parentId
            childList = st.session_state.orderList
            childListString = st.session_state.orderListStr
            finalizarProceso(parentId, childList, childListString)