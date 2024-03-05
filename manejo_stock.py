import streamlit as st
import pandas as pd
from db.db_manejo_stock import get_products_grouped_by_seller, get_products_by_proveedor_seller
from interface.ui_manejo_stock import detalle_ordenes_por_seller

def app():
    if 'username' in st.session_state:
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'detalle_ordenes_por_seller'
        if st.session_state.current_view in ('generar_guias_oax', 'generar_guias_oax_final', 'ingreso_entregador_oax', 'route_order_detail', 'confirmacion_route_order', 'entregas_oax', 'entrega_order_detail', 'generar_guias_final','generar_guias','pickFinal', 'recoleccionFinal', 'ingresoPickup', 'ingresoPickupFinal','final_proceso_picking_pickups','picking_pickups_detalle','picking_pickups','ordenesCompraMenu','detalleOrdenCompra', 'ingresoOrdenesCompra', 'ordenesCompraCsv','confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu','auditoria', 'ingresoOrdenesCompra'):
            st.session_state['current_view'] = 'detalle_ordenes_por_seller'
        if st.session_state['current_view'] == 'detalle_ordenes_por_seller':
            data = get_products_grouped_by_seller()
            if data is not None:
                data_pd = pd.DataFrame(data)
                grouped_by_seller_proveedor = data_pd.groupby(['seller_name', 'proveedor_name', 'seller_id', 'proveedor_id']).agg(sku_count=('id', 'count')).reset_index()
                sellers = list(data_pd['seller_name'].unique())

                detalle_ordenes_por_seller(grouped_by_seller_proveedor, sellers)
        elif st.session_state['current_view'] == 'conteo_stock_por_seller':
            data = get_products_by_proveedor_seller()