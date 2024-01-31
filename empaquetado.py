
import streamlit as st
from interface.UIEmpaquetado import UIOrdenesEmpaquetar,UIOrdenesEmpaquetarDetalle, UITFinalizarProceso
from db.db_UserInteractionEvents import event_instert   
from db.db_empaquetado import get_seller_centro_padre,get_order_detalle_empaquetado


def app():
    if 'username' in st.session_state:
        
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'empaquetado'
        print(st.session_state.current_view)
        if st.session_state.current_view in ( 'generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'empaquetado'
        if st.session_state.current_view == 'empaquetado':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista empaquetado',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            
            data=get_seller_centro_padre()
        
            print(data)
            if len(data)>0:
                UIOrdenesEmpaquetar(data)
            else:
                st.header('Empaquetar pedidos', divider='rainbow')
                st.header('No hay ordenes para empaquetar :blue[en este momento] :sunglasses:')
                
        if st.session_state.current_view == 'detalleEmpaquetado':
            print(st.session_state.orderId)
            print(st.session_state.pedidos_activos)
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista detalleEmpaquetado',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            st.session_state['current_view'] = 'detalleEmpaquetado'
            data=get_order_detalle_empaquetado(st.session_state.orderId)
            UIOrdenesEmpaquetarDetalle(data,st.session_state.orderId)
        if st.session_state.current_view == 'finalProcesoEmpaquetado':
                UITFinalizarProceso(st.session_state.orderId, st.session_state['orderList'], st.session_state['orderListStr'])
