import streamlit as st
from db.db_ingreso_entregador_oax import get_routes, get_route_orders
from interface.ui_ingreso_entregas_oax import UIingreso_entregador_oax, UIorder_detail, UIconfirmacion


def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'ingreso_entregador_oax'
        if st.session_state.current_view in ('revision_de_informacion','creacion_producto_ia','finalizar_manejo_stock_unitario','manejo_stock_unitario','showroom','visualizar_showroom','actualizar_showroom','finalizar_actualizacion','ingreso_pedidos_pickups','pendiente_entrega_pickup','bitacora_pickup','validar_entrega','finalizar_entrega','bitacora','detalle_bitacora','confirmar_baja_proveedor', 'detalle_ordenes_por_seller', 'conteo_stock_por_seller', 'finalizar_manejo_stock','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'entregas_oax', 'entrega_order_detail','generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal', 'final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'ingreso_entregador_oax'
        if st.session_state.current_view == 'ingreso_entregador_oax':
            data = get_routes()
            if data:
                UIingreso_entregador_oax(data)
            else:
                st.header('No hay rutas para ingresar', divider='rainbow')
        elif st.session_state.current_view == 'route_order_detail':
            id_ruta = st.session_state.current_route
            data = get_route_orders(id_ruta)
            if data:
                UIorder_detail(data, id_ruta)
            else:
                st.header('No hay ordenes para ingresar', divider='rainbow')
        elif st.session_state.current_view == 'confirmacion_route_order':
            id_ruta = st.session_state.current_route
            UIconfirmacion(id_ruta)
