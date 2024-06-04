import streamlit as st

from interface.ui_generar_bitacora import UITodosLosPedidos, UIdetalleBitacora
from db.db_generar_bitacora import get_lista_ordenes_padre, get_fees_bitacora, get_order_bitacora, get_suborders_bitacora
from db.db_user_interaction_events import event_instert

def app():
    if 'username' in st.session_state:
        data=[]
        if 'current_view' not in st.session_state:
                st.session_state['current_view'] = 'bitacora'
        if 'visible' not in st.session_state:
            st.session_state['visible'] = False
        if st.session_state.current_view in ('revision_de_informacion','creacion_producto_ia','finalizar_manejo_stock_unitario','manejo_stock_unitario','showroom','visualizar_showroom','actualizar_showroom','finalizar_actualizacion','ingreso_pedidos_pickups','pendiente_entrega_pickup','bitacora_pickup','validar_entrega','finalizar_entrega','confirmacion','detalleConfirmacion','finalProcesoConfirmacion','ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups', 'generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
                st.session_state['current_view'] = 'bitacora'

        if st.session_state.current_view == 'bitacora':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='bitacora','acceso a las vista bitacora',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            data=get_lista_ordenes_padre()
            UITodosLosPedidos(data)
        if st.session_state.current_view == 'detalle_bitacora':
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='bitacora','acceso a las vista detalleBitacora',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                data_general=get_order_bitacora(int(st.session_state['Order_id_bitacora']))
                data_detalle=get_suborders_bitacora(data_general['pedidos_hijos'][0])
                fees = get_fees_bitacora(int(st.session_state['Order_id_bitacora']))
                UIdetalleBitacora(data_general,data_detalle, fees)
    
    else:
                st.image("imagen/logo_imagen_no_loguado.png", width=300)
                st.markdown("### Por favor, inicia sesión para continuar")