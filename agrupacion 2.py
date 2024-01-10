
import streamlit as st
from interface.UIAgrupacion import UIOrdenesAgrupar
from db.db_UserInteractionEvents import event_instert    


def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'auditoria'
        if st.session_state.current_view == 'auditoria':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista pick',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            #data=get_seller_centro()
            data=[]
            UIOrdenesAgrupar(data)