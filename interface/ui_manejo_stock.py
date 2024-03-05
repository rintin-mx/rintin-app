import sys
sys.path.append('..')
import streamlit as st

def handle_select_change(select_value, sellers):
    '''
    Handles select filter value change by setting the needed states
    
    Parameters:
    select_value (string | None): selected value in the selectbox
    sellers (list): Unique seller list
    '''
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
    grouped_by_seller_proveedor
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
    st.selectbox('Sellers', options=sellers, index=st.session_state['current_seller_index'], on_change=handle_select_change)
    print(grouped_by_seller_proveedor)
    