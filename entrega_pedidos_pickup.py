import streamlit as st

from interface.ui_entrega_pedidos_pickup import ui_pendiente_entrega_pickup, ui_descargar_bitacora, ui_validacion_entrega, ui_finalizar_entrega
from db.db_entrega_pedidos_pickup import get_fees_bitacora, get_lista_ordenes_padre, get_order_items
from db.db_user_interaction_events import event_instert
from db.db_generar_bitacora import get_order_bitacora, get_suborders_bitacora

def app():
    if 'username' in st.session_state:
        data=[]
        if 'current_view' not in st.session_state:
                st.session_state['current_view'] = 'pendiente_entrega_pickup'
        if 'visible' not in st.session_state:
            st.session_state['visible'] = False
        if st.session_state.current_view in ('showroom','visualizar_showroom','actualizar_showroom','finalizar_actualizacion','confirmacion','detalleConfirmacion','finalProcesoConfirmacion','bitacora','detalle_bitacora','confirmar_baja_proveedor', 'detalle_ordenes_por_seller', 'conteo_stock_por_seller', 'finalizar_manejo_stock','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
                st.session_state['current_view'] = 'pendiente_entrega_pickup'

        if st.session_state.current_view == 'pendiente_entrega_pickup':
             if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='pendiente_entrega_pickup','acceso a las vista pendiente_entrega_pickup',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)  
                data=get_lista_ordenes_padre() 
                ui_pendiente_entrega_pickup(data)
        if st.session_state.current_view == 'bitacora_pickup':
             if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='bitacora_pickup','acceso a las vista bitacora_pickup',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                data_general=get_order_bitacora(st.session_state['order_id_pickup'])
                data_detalle=get_suborders_bitacora(data_general['pedidos_hijos'][0])
                fees = get_fees_bitacora(int(st.session_state['order_id_pickup']))
                ui_descargar_bitacora(data_general,data_detalle, fees)
        if st.session_state.current_view == 'validar_entrega':
             if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='validar_entrega','acceso a las vista validar_entrega',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                data = get_order_items(st.session_state['order_id_pickup'])
                ui_validacion_entrega(st.session_state['order_id_pickup'], st.session_state['phone_pickup'], st.session_state['addres'], data, st.session_state['pay_method'], st.session_state['discount'])
        if st.session_state.current_view == 'finalizar_entrega':
             if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='finalizar_entrega','acceso a las vista finalizar_entrega',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                ui_finalizar_entrega(st.session_state['order_id_pickup'], st.session_state['children_id_pickup'])