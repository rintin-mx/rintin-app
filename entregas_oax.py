import streamlit as st
from db.db_entregas_oax import get_orders
from interface.UIentregas_oax import UIentregas_oax


def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'entregas_oax'
        if st.session_state.current_view in ('generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal', 'final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'entregas_oax'
        if st.session_state.current_view == 'entregas_oax':
            data = get_orders()
            if data:
                UIentregas_oax(data)    
            else:
                st.header('No hay ordenes para entregar', divider='rainbow')
                st.header('No hay ordenes para entregar :blue[en este momento] :sunglasses:')
  