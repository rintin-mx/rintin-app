import streamlit as st
import pandas as pd

from interface.ui_creacion_producto_ia import ingreso_imagenes, revision_info

def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'creacion_producto_ia'
        if 'show_info_stock_unitario' not in st.session_state:
            st.session_state['show_info_stock_unitario'] = False
        if st.session_state.current_view in ('bitacora','finalizar_manejo_stock_unitario','manejo_stock_unitario','conteo_stock_por_seller','detalle_ordenes_por_seller','showroom','visualizar_showroom','actualizar_showroom','finalizar_actualizacion','ingreso_pedidos_pickups','pendiente_entrega_pickup','bitacora_pickup','validar_entrega','finalizar_entrega','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'generar_guias_oax', 'generar_guias_oax_final', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_final','generar_guias','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','ordenesCompraMenu','detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu','auditoria', 'ingresoOrdenesCompra'):
            st.session_state['show_info_stock_unitario'] = False
            st.session_state['current_view'] = 'creacion_producto_ia'

        if st.session_state.current_view == 'creacion_producto_ia':
            ingreso_imagenes()

        if st.session_state.current_view == 'revision_de_informacion':
            revision_info(st.session_state['creacion_productos_urls'])