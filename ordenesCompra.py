
import streamlit as st
from interface.UIordenesCompra import UITOrdenesCompra
from db.db_UserInteractionEvents import event_instert   
from db.db_agrupacion import get_seller_centro_padre,get_order_detalle_agrupacion


def app():
    if 'username' in st.session_state:
        print(st.session_state.current_view)
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'ordenesCompra'
        if st.session_state.current_view== 'pick' or st.session_state.current_view== 'auditoria' or st.session_state.current_view== 'recolect' or st.session_state.current_view== 'ordenesAgrupar' or st.session_state.current_view=='ordenesCompra' or st.session_state.current_view=='agrupacion':
            st.session_state['current_view'] = 'ordenesCompra'
        if st.session_state.current_view == 'ordenesCompra':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista ordenesCompra',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            UITOrdenesCompra()