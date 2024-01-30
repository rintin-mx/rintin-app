
import streamlit as st
from interface.UIordenesCompra import UITOrdenesCompra
from interface.UIordenesCompra import UITAddProduct
from db.db_UserInteractionEvents import event_instert   
from db.db_ordenesCompra import get_live_sellers, get_ordenes_compra, get_products, get_parent_orders, get_order_info
from interface.UIordenesCompra import UITOrdenesCompraCSV, UITTerminarOrdenCompra, UITOrdenesCompraMenu,UITOrdenesCompraEdit

def app():
    if 'username' in st.session_state:
        data = []
        if 'current_view' not in st.session_state:
            st.session_state['current_view'] = 'ordenesCompraMenu'
        if st.session_state.current_view in ('confirmacion','ingresoOrdenesDetalle','detalleEmpaquetado','finalProcesoEmpaquetado','detalleConfirmacion','finalProcesoConfirmacion','empaquetado', 'detalleAuditoria','finalProceso', 'detalleAgrupacion', 'finalProcesoAgrupacion','pick','recolect','detalle','recoleccion','pendiente','ordenesAgrupar','agrupacion','ordenesCompraMenu','auditoria', 'ingresoOrdenesCompra'):
            st.session_state['current_view'] = 'ordenesCompraMenu'
        if st.session_state.current_view == 'ordenesCompra':
            orderProducts = None
            if st.session_state.useremail is not None:
                EventName,EventAction,EventUser='picking','acceso a las vista ordenesCompra',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
            if 'ordenCompraId' in st.session_state:
                print('entro al fetch products')
                orderProducts = get_products(st.session_state['ordenCompraId'])
            data = get_live_sellers()
            UITOrdenesCompra(data, orderProducts)
        elif st.session_state.current_view == 'detalleOrdenCompra':
            if 'editProduct' in st.session_state:
                product = st.session_state['editProduct']
            else:
                product = None
            UITAddProduct(product)
        elif st.session_state.current_view == 'ordenesCompraCsv':
            data = get_live_sellers()
            UITOrdenesCompraCSV(data)
        elif st.session_state.current_view == 'ordenesCompraMenu':
            if 'ordenCompraId' in st.session_state:
                del st.session_state['ordenCompraId']
            if 'isEditing' in st.session_state:
                del st.session_state['isEditing']
            if 'currentSeller' in st.session_state:
                del st.session_state['currentSeller']
            if 'dictProductos' in st.session_state:
                del st.session_state['dictProductos']
            if 'isSaved' in st.session_state:
                del st.session_state['isSaved']
            if 'initialFetch' in st.session_state:
                del st.session_state['initialFetch']
            if 'deletedProducts' in st.session_state:
                del st.session_state['deletedProducts']
            UITOrdenesCompraMenu()
        elif st.session_state.current_view == 'editOrdenesCompra':
            data = get_ordenes_compra()
            if 'ordenCompraId' in st.session_state:
                del st.session_state['ordenCompraId']
            if 'isEditing' in st.session_state:
                del st.session_state['isEditing']
            UITOrdenesCompraEdit(data)
        elif st.session_state.current_view == 'terminar_orden_compra':
            data = get_parent_orders()
            
            if 'ordenCompraId' in st.session_state:
                orderData = get_order_info(st.session_state['ordenCompraId'])
            else:
                orderData = None
            UITTerminarOrdenCompra(data, orderData)
            