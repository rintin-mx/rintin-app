
import streamlit as st
from interface.UIAgrupacion import UIOrdenesAgrupar,UIOrdenesAgruparDetalle
from db.db_UserInteractionEvents import event_instert   
from db.db_agrupacion import get_seller_centro_padre,get_order_detalle_agrupacion


def app():
    if 'username' in st.session_state:
        
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'agrupacion'
        print(st.session_state.current_view)
        if st.session_state.current_view in ('pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompra','auditoria'):
            st.session_state['current_view'] = 'agrupacion'
        if st.session_state.current_view == 'agrupacion':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista agrupacion',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            
            data=get_seller_centro_padre()
        
            print(data)
            if len(data)>0:
                UIOrdenesAgrupar(data)
            else:
                st.write("No hay pedidos para agrupar, esta es data solo de demostración")
                data=[
                    {
                        "order_id": 217024,
                        "ordenes_activas": 5,
                        "pedidos_auditados": 3,
                        "en_proceso": 2,
                        "estado": "Faltan Pedidos"
                    },
                    {
                        "order_id": 217419,
                        "ordenes_activas": 4,
                        "pedidos_auditados": 4,
                        "en_proceso": 0,
                        "estado": "Agrupar"
                    },
                    {
                        "order_id": 217426,
                        "ordenes_activas": 6,
                        "pedidos_auditados": 1,
                        "en_proceso": 5,
                        "estado": "Faltan Pedidos"
                    },
                    {
                        "order_id": 253637,
                        "ordenes_activas": 2,
                        "pedidos_auditados": 2,
                        "en_proceso": 0,
                        "estado": "Agrupar"
                    }
                ]
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
