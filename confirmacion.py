import streamlit as st
from interface.UIconfirmacion import UITodosLosPedidos,UIDetallePedido,UITFinalizarProceso
from db.db_confirmacion import get_seller_centro,get_order_auditoria, checkForChildStatusses
from db.db_UserInteractionEvents import event_instert
def app():
        if 'username' in st.session_state:
                data=[]
                if 'current_view' not in st.session_state:
                       st.session_state['current_view'] = 'confirmacion'
                if 'visible' not in st.session_state:
                    st.session_state['visible'] = False
                if st.session_state.current_view in ('empaquetado','pick','recolect','recoleccion','pendiente','ordenesAgrupar','agrupacion','detalleAgrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'currentOrder'):
                      st.session_state['current_view'] = 'confirmacion'

                if st.session_state.current_view == 'confirmacion':
                    print('confirmacion')

                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='confirmacion','acceso a las vista confirmacion',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    data=get_seller_centro()
                    UITodosLosPedidos(data)      
                if st.session_state.current_view == 'detalleConfirmacion':
                      if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='confirmacion','acceso a las vista detalleConfirmacion',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)  
                        print("st.session_state['Order_id_confirmacion']")
                        print(st.session_state['Order_id_confirmacion'])
                        data=get_order_auditoria(int(st.session_state['Order_id_confirmacion'])) 
                        UIDetallePedido(data,int(st.session_state['Order_id_confirmacion']))
                if st.session_state.current_view == 'finalProcesoConfirmacion':
                    data = checkForChildStatusses(st.session_state['Order_id_confirmacion'])
                    current_status = st.session_state.current_status
                    UITFinalizarProceso(data, current_status)
        else:
                st.image("imagen/logo_imagen_no_loguado.png", width=300)
                st.markdown("### Por favor, inicia sesión para continuar")


