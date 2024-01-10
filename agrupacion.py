
import streamlit as st
from interface.UIAgrupacion import UIOrdenesAgrupar,UIOrdenesAgruparDetalle
from db.db_UserInteractionEvents import event_instert   
from db.db_agrupacion import get_seller_centro_padre,get_order_detalle_agrupacion


def app():
    if 'username' in st.session_state:
        
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'agrupacion'
        print(st.session_state.current_view)
        if st.session_state.current_view in ('pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','detalleAgrupacion','ordenesCompra','auditoria'):
            st.session_state['current_view'] = 'agrupacion'
        if st.session_state.current_view == 'agrupacion':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista agrupacion',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            data=get_seller_centro_padre()
            UIOrdenesAgrupar(data)
        if st.session_state.current_view == 'detalleAgrupacion':
            print(st.session_state.orderId)
            print(st.session_state.pedidos_activos)
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista detalleAgrupacion',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            st.session_state['current_view'] = 'detalleAgrupacion'
            data=get_order_detalle_agrupacion(st.session_state.orderId)
            UIOrdenesAgruparDetalle(data,st.session_state.orderId)
