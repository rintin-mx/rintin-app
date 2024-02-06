
import streamlit as st
from interface.UIEmpaquetado import UIOrdenesEmpaquetar,UIOrdenesEmpaquetarDetalle, UITFinalizarProceso
from db.db_UserInteractionEvents import event_instert   
from db.db_empaquetado import get_seller_centro_padre,get_order_detalle_empaquetado


def app():
    if 'username' in st.session_state:
        
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'empaquetado'
        if st.session_state.current_view in ( 'final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'empaquetado'
        if st.session_state.current_view == 'empaquetado':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista empaquetado',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            
            data=get_seller_centro_padre()
            order_parents_string = [str(element) for element in data['order_id']]
            order_ids_temp_list = order_parents_string
            complete_array = data['hijos_agrupados'] + data['hijos_en_proceso']
            for orders in complete_array:
                if orders is not None and orders != 'N/A':
                    order_ids_temp_list = order_ids_temp_list + (orders.split(', '))
            if len(data)>0:
                UIOrdenesEmpaquetar(data,order_ids_temp_list)
            else:
                st.header('Empaquetar pedidos', divider='rainbow')
                st.header('No hay ordenes para empaquetar :blue[en este momento] :sunglasses:')
                
        if st.session_state.current_view == 'detalleEmpaquetado':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista detalleEmpaquetado',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            st.session_state['current_view'] = 'detalleEmpaquetado'
            data=get_order_detalle_empaquetado(st.session_state.orderId)
            UIOrdenesEmpaquetarDetalle(data,st.session_state.orderId)
        if st.session_state.current_view == 'finalProcesoEmpaquetado':
                UITFinalizarProceso(st.session_state.orderId, st.session_state['orderList'], st.session_state['orderListStr'])
