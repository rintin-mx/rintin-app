import streamlit as st

from db.db_stock_showroom import get_products, get_products_sku_list
from db.db_user_interaction_events import event_instert
from interface.ui_stock_showroom import UIactualizarShowroom, UIfinalizarActualizacion, UIstartPage, UIvisualizarShowroom


def app():
    if 'username' in st.session_state:
        data=[]
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'showroom'
        if 'visible' not in st.session_state:
            st.session_state['visible'] = False
        if st.session_state.current_view in ('validacion_detalle_ordenes_por_seller','validacion_conteo_stock_por_seller','detalle_ordenes_por_seller','conteo_stock_por_seller','bitacora','detalle_bitacora','ingreso_pedidos_pickups','pendiente_entrega_pickup','bitacora_pickup','validar_entrega','finalizar_entrega','confirmacion','detalleConfirmacion','finalProcesoConfirmacion','ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
                st.session_state['current_view'] = 'showroom'
        
        if st.session_state.current_view == 'showroom':
             if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='showroom','acceso a las vista showroom',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                UIstartPage()
        if st.session_state.current_view == 'visualizar_showroom':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='visualizar_showroom','acceso a las vista visualizar_showroom',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                data = get_products()
                UIvisualizarShowroom(data)
        
        if st.session_state.current_view == 'actualizar_showroom':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='actualizar_showroom','acceso a las vista actualizar_showroom',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                lista = get_products_sku_list()
                UIactualizarShowroom(lista)
        
        if st.session_state.current_view == 'finalizar_actualizacion':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='finalizar_actualizacion','acceso a las vista finalizar_actualizacion',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                UIfinalizarActualizacion(st.session_state.shr_prod_sku, st.session_state.shr_new_stock)