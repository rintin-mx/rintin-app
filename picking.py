import streamlit as st
from interface.UIpicking import UITodosLosPedidos,UIDetallePedido
from db.db_order import get_order,get_seller
from db.db_UserInteractionEvents import event_instert


def app():
        if 'username' in st.session_state:
                data=[]
                if 'current_view' not in st.session_state:
                    st.session_state['current_view'] = 'pick'

                if st.session_state.current_view== 'pick' or st.session_state.current_view== 'auditoria' or  st.session_state.current_view== 'detalleAuditoria' or st.session_state.current_view== 'ordenesAgrupar' or st.session_state.current_view== 'agrupacion' or st.session_state.current_view== 'detalleAgrupacion':
                    st.session_state['current_view'] = 'recolect'

                if st.session_state.current_view== 'recolect' or st.session_state.current_view== 'recoleccion' or st.session_state.current_view== 'pendiente' or st.session_state.current_view== 'detalle' :
                       if st.session_state['current_view'] == 'detalle':
                             st.session_state['current_view'] = 'detalle'
                       else:
                             st.session_state['current_view'] = 'pick'
                if st.session_state.current_view == 'pick':
                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','acceso a las vista pick',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    st.header("Todo los Pedidos")
                    data=get_seller()
                    UITodosLosPedidos(data)
                elif st.session_state.current_view == 'detalle':
                    data=[]
                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','acceso a las vista detalle',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    st.header("Orden ID:"+ str(st.session_state.orderId))
                    st.session_state.mostrar_elemento=True
                    data=get_order(st.session_state.orderId)
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


