import streamlit as st
from streamlit_searchbox import st_searchbox

def ui_entregas():
    if 'visible' not in st.session_state:
        st.session_state['visible'] = True
        st.rerun()
    
    st.header("Herramientas Operaciones")
    st.divider()

    if st.button('Entregas Oaxaca'):
        st.session_state['current_view'] = 'pendiente_entrega_pickup'
        st.rerun()


def search_by_order(searchterm: str):
    
    # Search for the order_id given

    # Parameters:
    # searchterm: a order_id where order is going to be picked (str)
    # parent_order_id or children_order_id

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['order_id'].str.contains(searchterm)|(data['children_orders'].str.contains(searchterm))]
    st.session_state['visible']=False

    return data_filtrado['order_id'] if searchterm else []

def search_bodega(searchterm: str):
    
    # Search for the bodega given

    # Parameters:
    # searchterm: a bodega where order is going to be picked (str)
    # 'Recoleccion Oaxaca'

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['shipping_method'].str.contains(searchterm)]
    st.session_state['visible']=False

    return data_filtrado['shipping_method'] if searchterm else []

def search_cliente(searchterm: str):
    
    # Search for the cliente given

    # Parameters:
    # searchterm: a full_name of the person who's going to pick up the order (str)
    # 'Juan Pablo Jimenez'

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['full_name'].str.lower().str.contains(searchterm.lower())]
    st.session_state['visible']=False

    return data_filtrado['full_name'] if searchterm else []

def search_phone(searchterm: str):
    
    # Search for the phone given

    # Parameters:
    # searchterm: a phone of the person who's going to pick up the order (str)
    # '549485624'

    # Returns:
    # A dataframe with the rows including the term searched

    data = st.session_state['data']
    data_filtrado = data[data['phone'].str.contains(searchterm)]
    st.session_state['visible']=False

    return data_filtrado['phone'] if searchterm else []

def search_by_filters(order_id: str, full_name: str, bodega: str, phone: str):
    
    # Search for the order_info with the parameters given

    # Parameters:
    # searchterm: a phone, full_name, bodega or children/parent_order_id of the order to being picked up (str)
    # '549485624', 'Juan Pablo Jimenez', 'Recoleccion Oaxaca', parent_order_id or children_order_id

    # Returns:
    # A dataframe with the rows including the terms searched

    data = st.session_state['data']
    if order_id != '' and order_id != None:
        data = data[data['order_id'].str.contains(order_id)|(data['children_orders'].str.contains(order_id))]
    if full_name != '' and full_name != None:
        data = data[data['full_name'].str.contains(full_name)]
    if phone != '' and phone != None:
        data = data[data['phone'].str.contains(phone)]
    if bodega != '' and bodega != None:
        data = data[data['shipping_method'].str.contains(bodega)]

    st.session_state['visible']=False

    return data

def ui_pendiente_entrega_pickup(data):
    if 'order_id_pendiente_entrega_pickup' not in st.session_state:
        st.session_state['order_id_pendiente_entrega_pickup'] = 0
    
    data['order_id'] = data['order_id'].astype(str)
    st.session_state['data'] = data
    filtro_orden = ''
    filtro_bodega = ''
    filtro_cliente = ''
    filtro_phone = ''

    st.header('Pendiente entrega en Pickup')
    st.divider()

    filtro_bodega = st_searchbox(
        label='Bodega a recolectar:',
        search_function=search_bodega,
        key=f"search_bodega",
        rerun_on_update=True
    )

    filtro_orden = st_searchbox(
        label='Número de pedido:',
        search_function=search_by_order,
        key=f"search_orderid",
        rerun_on_update=True
    )

    filtro_cliente = st_searchbox(
        label='Nombre Cliente:',
        search_function=search_cliente,
        key=f"search_cliente",
        rerun_on_update=True
    )

    filtro_phone = st_searchbox(
        label='Teléfono Cliente:',
        search_function=search_phone,
        key=f"search_phone",
        rerun_on_update=True
    )

    col1, col2 = st.columns([3, 3])

    with col1:
        find = st.button('Filtrar')

        if find:
            st.session_state['data'] = search_by_filters(filtro_orden, filtro_cliente, filtro_bodega, filtro_phone)
    
    st.write('#')

    st.subheader('Pedidos a entregar:')
    st.write('#')
    col3, col4, col5, col6, col12 = st.columns([4, 2, 5, 2, 2])

    with col3:
        st.markdown("<h5 style='color: black;'>CLIENTE</h5>", unsafe_allow_html=True)

    with col4:
        st.markdown("<h5 style='color: black;'>ID PEDIDO</h5>", unsafe_allow_html=True)

    with col5:
        st.markdown("<h5 style='color: black;'>ID PEDIDOS HIJOS</h5>", unsafe_allow_html=True)

    with col6:
        st.markdown("<h5 style='color: black;'>TELÉFONO</h5>", unsafe_allow_html=True)

    data = st.session_state['data']

    if not data.empty:
        for i, orden in data.iterrows():
            st.divider()
            col7, col8, col9, col10, col11 = st.columns([4,2,5,2,2])
            with col7:
                st.markdown(orden['full_name'])
            with col8:
                st.markdown(orden['order_id'])
            with col9:
                st.markdown(orden['children_orders'])
            with col10:
                st.markdown(orden['phone'])
            with col11:
                st.button('Entrega', key=f'entregar_{i}')
