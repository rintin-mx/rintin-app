import streamlit as st
from interface.UIauditoria import UITodosLosPedidos,UIDetallePedido
from db.db_auditoria import get_seller_centro,get_order_auditoria
from db.db_UserInteractionEvents import event_instert
def app():
        if 'username' in st.session_state:
                data=[]
                if 'current_view' not in st.session_state:
                       print("entre al if")
                       st.session_state['current_view'] = 'auditoria'
                if st.session_state.current_view== 'pick' or st.session_state.current_view== 'recolect' or st.session_state.current_view== 'ordenesAgrupar':
                      st.session_state['current_view'] = 'auditoria'

                if st.session_state.current_view == 'auditoria':
                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','acceso a las vista pick',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    data=get_seller_centro()
                    UITodosLosPedidos(data)
                elif st.session_state.current_view == 'detalleAuditoria':
                    print("entre al detalleeeeee")
                    data=[]
                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','acceso a las vista detalle',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    st.header("Orden ID:"+ str(st.session_state.orderId))
                    st.session_state.mostrar_elemento=True
                    data=get_order_auditoria(st.session_state.orderId)
                    length = len(data)
                    print("length")
                    print(length)
                    #if length>0:
                    UIDetallePedido(data,st.session_state.orderId)
                    #else:
                    #    st.header("No se encontraron productos asosciados a la orden")
               
        else:
                st.image("imagen/logo_imagen_no_loguado.png", width=300)
                st.markdown("### Por favor, inicia sesión para continuar")


