import streamlit as st
from db.db_numerosGuia import get_ordenes_generar_guia
from interface.UIgenerar_guias import UIgenerar_guias, UIgenerar_guias_final

def app():
    if 'username' in st.session_state:
        data = []
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'generar_guias'
        if st.session_state.current_view in ('pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','ordenesCompraMenu','detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu','auditoria', 'ingresoOrdenesCompra'):
            st.session_state['current_view'] = 'generar_guias'
        if st.session_state['current_view'] == 'generar_guias':
            data = get_ordenes_generar_guia()
            if data is not None:
                UIgenerar_guias(data)
            else:
                st.header('Generar guías para pedidos', divider='rainbow')
                st.header('No hay ordenes en paquetería :blue[en este momento] :sunglasses:')
                
        elif st.session_state['current_view'] == 'generar_guias_final':
            order_string = st.session_state['orders_string']
            child_list = st.session_state['child_list']
            UIgenerar_guias_final(order_string, child_list)
        