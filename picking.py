import streamlit as st
from interface.ui_picking import UITodosLosPedidos,UIDetallePedido,pickFinal
from db.db_order import get_order,get_seller, get_proveedores
from db.db_user_interaction_events import event_instert


def app():
        if 'username' in st.session_state:
                data=[]
                if 'current_view' not in st.session_state:
                    st.session_state['current_view'] = 'pick'
                
                if st.session_state.current_view in ('showroom','visualizar_showroom','actualizar_showroom','finalizar_actualizacion','ingreso_pedidos_pickups','pendiente_entrega_pickup','bitacora_pickup','validar_entrega','finalizar_entrega','bitacora','detalle_bitacora','confirmar_baja_proveedor', 'detalle_ordenes_por_seller', 'conteo_stock_por_seller', 'finalizar_manejo_stock','validacion_detalle_ordenes_por_seller', 'validacion_conteo_stock_por_seller', 'validacion_finalizar_manejo_stock', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
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
                    proveedores=get_proveedores()
                    UITodosLosPedidos(data, proveedores['proveedor'])
                elif st.session_state.current_view == 'detalle':
                    data=[]
                    if st.session_state.useremail is not None:
                        EventName,EventAction,EventUser='picking','acceso a las vista detalle',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                    st.header("Orden ID:"+ str(st.session_state.orderId))
                    st.session_state.mostrar_elemento=True
                    data=get_order(st.session_state.orderId)
                    length = len(data)
                    #if length>0:
                    UIDetallePedido(data,st.session_state.orderId)
                    #else:
                    #    st.header("No se encontraron productos asosciados a la orden")
                elif st.session_state.current_view == 'pickFinal':
                    orderId = st.session_state['currentOrderId']
                    status = st.session_state['currentStatus']
                    pickFinal(orderId, status)
               
        else:
                st.image("imagen/logo_imagen_no_loguado.png", width=300)
                st.markdown("### Por favor, inicia sesión para continuar")


