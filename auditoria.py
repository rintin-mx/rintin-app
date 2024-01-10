import streamlit as st
from interface.UIauditoria import UITodosLosPedidos,UIDetallePedido
from db.db_auditoria import get_seller_centro,get_order_auditoria
from db.db_UserInteractionEvents import event_instert
def app():
        if 'username' in st.session_state:
                data=[]
                if 'current_view' not in st.session_state:
                       st.session_state['current_view'] = 'auditoria'
                if 'visible' not in st.session_state:
                    st.session_state['visible'] = False
                if st.session_state.current_view== 'pick' or st.session_state.current_view== 'recolect'  or st.session_state.current_view== 'ordenesAgrupar' or st.session_state.current_view== 'agrupacion' or st.session_state.current_view== 'detalleAgrupacion' or st.session_state.current_view=='ordenesCompra':
                      st.session_state['current_view'] = 'auditoria'

                if st.session_state.current_view == 'auditoria':
                    print('auditoria')

                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','acceso a las vista pick',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    data=get_seller_centro()
                    UITodosLosPedidos(data)      
                if st.session_state.current_view == 'detalleAuditoria':
                      if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','acceso a las vista pick',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)  
                        print("st.session_state['Order_id_auditoria']")
                        print(st.session_state['Order_id_auditoria'])
                        data=get_order_auditoria(int(st.session_state['Order_id_auditoria']))     
                        UIDetallePedido(data,int(st.session_state['Order_id_auditoria']))
        else:
                st.image("imagen/logo_imagen_no_loguado.png", width=300)
                st.markdown("### Por favor, inicia sesión para continuar")


