import streamlit as st
from interface.ui_generacion_guias_oax import UIgeneracion_guias_oax, UIgenerar_guias_final_oax
from db.db_generacion_guias_oax import get_ordenes_generar_guia
def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'generar_guias_oax'
        if st.session_state.current_view in ('finalizar_manejo_stock_unitario','manejo_stock_unitario','showroom','visualizar_showroom','actualizar_showroom','finalizar_actualizacion','ingreso_pedidos_pickups','pendiente_entrega_pickup','bitacora_pickup','validar_entrega','finalizar_entrega','bitacora','detalle_bitacora','confirmar_baja_proveedor', 'detalle_ordenes_por_seller', 'conteo_stock_por_seller', 'finalizar_manejo_stock','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_final','generar_guias','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','ordenesCompraMenu','detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu','auditoria', 'ingresoOrdenesCompra'):
            st.session_state['current_view'] = 'generar_guias_oax'
        if st.session_state.current_view == 'generar_guias_oax':
            order_list = get_ordenes_generar_guia()
            if order_list:
                order_parents_string = [str(element) for element in order_list['order_id']]
                order_ids_temp_list = order_parents_string
                complete_array = order_list['hijos_guia']
                for orders in complete_array:
                    if orders is not None and orders != 'N/A':
                        order_ids_temp_list = order_ids_temp_list + (orders.split(', '))
                zone_filter = set(order_list['zona_entrega'])
                UIgeneracion_guias_oax(order_list, order_ids_temp_list, zone_filter)
            else:
                st.header('Generar numeros de guia Oaxaca', divider='rainbow')
                st.header('No hay ordenes :blue[en este momento] :sunglasses:')

        elif st.session_state.current_view == 'generar_guias_oax_final':
            order_string = st.session_state['orders_string']
            child_list = st.session_state['child_list']
            UIgenerar_guias_final_oax(order_string, child_list)

