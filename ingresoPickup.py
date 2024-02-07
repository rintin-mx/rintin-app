import streamlit as st
import pandas as pd
from db.db_ingreso_pickup import get_seller_centro_padre
from interface.UIingreso_pickup import ingresoPickup, finalizarProceso

def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'ingresoPickup'
        if st.session_state.current_view in('final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv', 'ingresoOrdenesDetalle'):
            st.session_state['current_view'] = 'ingresoPickup'
        if st.session_state['current_view'] == 'ingresoPickup':
            orders = get_seller_centro_padre()
            ingresoPickup(orders)
        elif st.session_state['current_view'] == 'ingresoPickupFinal':
            parentId = st.session_state.parentId
            childList = st.session_state.orderList
            childListString = st.session_state.orderListStr
            finalizarProceso(parentId, childList, childListString)