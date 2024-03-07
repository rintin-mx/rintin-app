import streamlit as st
from db.db_entregas_oax import get_orders, get_route_orders, has_active_route, get_order_items
from interface.ui_entregas_oax import UIentregas_oax, UIroute_orders, order_detail
from streamlit_float import *

def app():
    print('cambiado')
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'entregas_oax'
        if st.session_state.current_view in ('confirmar_baja_proveedor', 'detalle_ordenes_por_seller', 'conteo_stock_por_seller', 'finalizar_manejo_stock','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal', 'final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'entregas_oax'
        if st.session_state.current_view == 'entregas_oax':
            route_id = has_active_route(st.session_state.useremail)
            if route_id != 0:
                data = get_route_orders(route_id)
                UIroute_orders(data, route_id)
            else:
                data = get_orders()
                if data:
                    UIentregas_oax(data, data['order_id'], set(data['zona_entrega']))
                else:
                    st.header('No hay ordenes para entregar', divider='rainbow')
                    st.header('No hay ordenes para entregar :blue[en este momento] :sunglasses:')
        elif st.session_state.current_view == 'entrega_order_detail':
            route_id = st.session_state.route_id
            order_id = st.session_state.current_order['order_id']
            number_unified = st.session_state.current_order['number_unified']
            address = st.session_state.current_order['address']
            total = st.session_state.current_order['total']
            estado = st.session_state.current_order['estado']
            metodo_pago = st.session_state.current_order['metodo_pago']
            order_items = get_order_items(order_id)
            child_order_list = set(order_items['order_id'])
            order_detail(order_id, number_unified, address, order_items, route_id, estado, child_order_list, metodo_pago)