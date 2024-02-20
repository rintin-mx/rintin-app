import streamlit as st
from interface.UIrecoleccion import UIpendienteRecoleccion, UIrecoleccionFinal, UIpendienteRecoleccionSeleccion,UIagrerPedidoSellerSeleccion
from db.db_recoleccion import get_seller_recollection,get_data_seller_by_name
import pandas as pd


def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'recolect'
        if st.session_state.current_view in ('ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_oax', 'generar_guias_oax_final','pickFinal', 'ingresoPickup', 'ingresoPickupFinal', 'final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','generar_guias', 'generar_guias_final','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','ordenesAgrupar','agrupacion','ordenesCompraMenu', 'editOrdenesCompra', 'terminar_orden_compra', 'ordenesCompra','auditoria', 'detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv'):
            st.session_state['current_view'] = 'recolect'
        # Mostrar la vista correspondiente
        if st.session_state.current_view == 'recolect':

            total_pedidos, total_paquetes , total_registros, data =get_seller_recollection()
            UIpendienteRecoleccion(total_pedidos, total_paquetes , total_registros, data)
              
        elif st.session_state.current_view == 'recoleccion':
        
            total_pedidos, total_paquetes , total_registros, data =get_seller_recollection()
            UIpendienteRecoleccionSeleccion(total_pedidos, total_paquetes , total_registros, data)
            
        elif st.session_state.current_view == 'pendiente':
  
            total_pedidos, total_paquetes , total_registros, dataBase =get_seller_recollection()
            data=get_data_seller_by_name(st.session_state.Seller_name)
            
            dataBase_df = pd.DataFrame(dataBase)
            data_df = pd.DataFrame(data)
            print('seller name')
            print(st.session_state.Seller_name)
            print('dataBase_df')
            print(dataBase_df)
            print('data_df')
            print(data_df)
            # Realizamos el inner join
            df_merged = pd.merge(dataBase_df, data_df, left_on='Seller', right_on='seller_name')
            df_final=df_merged[["Seller","#Pedidos","num_paquetes","recolectado","order_id"]]
            df_final.columns = ['seller_name', 'num_pedidos','num_paquetes','recolectado','order_id']
            df_final_dict = df_final.to_dict(orient='list')
            if st.button("regresar a recoleccion"):
                st.session_state.current_view = 'recoleccion'
                st.rerun()
            UIagrerPedidoSellerSeleccion(df_final)
        elif st.session_state.current_view == 'recoleccionFinal':
            orderList = st.session_state['orderList']
            orderStr = st.session_state['orderStr']
            UIrecoleccionFinal(orderList, orderStr)
    else:
        st.markdown(st.session_state.username)
        st.image("imagen/logo_imagen_no_loguado.png", width=300)
        st.markdown("## Por favor, inicia sesión para continuar")