import sys
sys.path.append('..')
import streamlit as st

def handle_select_change():
    '''
    Handles select filter value change by setting the needed states
    
    Parameters:
    select_value (string | None): selected value in the selectbox
    sellers (list): Unique seller list
    '''
    sellers = st.session_state['unique_sellers']
    select_value = st.session_state['filter_select']
    st.session_state['current_seller'] = select_value
    if select_value is not None:
        st.session_state['current_seller_index'] = sellers.index(select_value)

def detalle_ordenes_por_seller(grouped_by_seller_proveedor, sellers):
    '''
    Front end view for detalle ordenes por seller page
    
    Parameters:
    grouped_by_seller_proveedor (DataFrame): Grouped products by proveedor and seller.
    sellers (list): Unique sellers of grouped_by_seller_proveedor
    '''
    seller_proveedor_to_disable = []
    if 'unique_selelrs' not in st.session_state:
        st.session_state['unique_sellers'] = sellers
    if 'current_seller' not in st.session_state:
        st.session_state['current_seller'] = None
        st.session_state['current_seller_index'] = None
    current_seller_for_title = None
    if st.session_state['current_seller'] is not None:
        current_seller_for_title = st.session_state['current_seller']
        grouped_by_seller_proveedor = grouped_by_seller_proveedor[(grouped_by_seller_proveedor['seller_name'] == st.session_state['current_seller'])]
    else:
        current_seller_for_title = 'Todos los sellers'
    st.markdown(f'### Detalle de ordenes por seller: {current_seller_for_title}')
    st.selectbox('Sellers', key='filter_select', options=sellers, index=st.session_state['current_seller_index'], on_change=handle_select_change)
    st.write('---')
    for i, product in grouped_by_seller_proveedor.iterrows():
        st.markdown(f'#### Seller: {product.seller_name}')
        st.markdown(f'#### Proveedor: {product.proveedor_name}')
        st.markdown(f'#### Total skus: {product.sku_count}')
        st.write('')
        st.checkbox('Bajar productos', key=f'{i}_checkbox')
        st.button('Stock', key=f'{i}_button')
        st.write('---')