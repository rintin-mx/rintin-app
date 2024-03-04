
import streamlit as st
from interface.ui_agrupacion import UIOrdenesAgrupar,UIOrdenesAgruparDetalle, UITFinalizarProceso
from db.db_user_interaction_events import event_instert   
from db.db_agrupacion import get_seller_centro_padre,get_order_detalle_agrupacion


def app():
    if 'username' in st.session_state:
        
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'agrupacion'
        if st.session_state.current_view in ('ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal' ,'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'agrupacion'
        if st.session_state.current_view == 'agrupacion':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista agrupacion',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            
            data=get_seller_centro_padre()
            order_parents_string = [str(element) for element in data['order_id']]
            order_ids_temp_list = order_parents_string
            complete_array = data['hijos_auditados'] + data['hijos_en_proceso']
            for orders in complete_array:
                if orders is not None and orders != 'N/A':
                    order_ids_temp_list = order_ids_temp_list + (orders.split(', '))
        
            if len(data)>0:
                UIOrdenesAgrupar(data, order_ids_temp_list)
            else:
                st.header('Agrupar pedidos', divider='rainbow')
                st.header('No hay ordenes para agrupar :blue[en este momento] :sunglasses:')
        if st.session_state.current_view == 'detalleAgrupacion':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista detalleAgrupacion',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            st.session_state['current_view'] = 'detalleAgrupacion'
            data=get_order_detalle_agrupacion(st.session_state.orderId)
            UIOrdenesAgruparDetalle(data,st.session_state.orderId)
        if st.session_state.current_view == 'finalProcesoAgrupacion':
                UITFinalizarProceso(st.session_state.orderId, st.session_state['orderList'], st.session_state['orderListStr'])
