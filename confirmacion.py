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
                if st.session_state.current_view in ('ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
                      st.session_state['current_view'] = 'confirmacion'

                if st.session_state.current_view == 'confirmacion':
                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='confirmacion','acceso a las vista confirmacion',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    data=get_seller_centro()
                    UITodosLosPedidos(data)      
                if st.session_state.current_view == 'detalleConfirmacion':
                      if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='confirmacion','acceso a las vista detalleConfirmacion',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)  
                        data=get_order_auditoria(int(st.session_state['Order_id_confirmacion'])) 
                        UIDetallePedido(data,int(st.session_state['Order_id_confirmacion']))
                if st.session_state.current_view == 'finalProcesoConfirmacion':
                    data = checkForChildStatusses(st.session_state['Order_id_confirmacion'])
                    productList = st.session_state.productos_validacion
                    UITFinalizarProceso(data, productList)
        else:
                st.image("imagen/logo_imagen_no_loguado.png", width=300)
                st.markdown("### Por favor, inicia sesión para continuar")


