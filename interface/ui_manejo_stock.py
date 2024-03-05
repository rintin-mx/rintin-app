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
        disable_products = st.checkbox('Bajar productos', key=f'{i}_checkbox')
        if disable_products:
            seller_proveedor_to_disable.append({
                "seller_id": product.seller_id,
                "proveedor_id": product.proveedor_id
            })
        if st.button('Stock', key=f'{i}_button'):
            if disable_products:
                print('Eliminar producto')
            else:
                st.session_state['current_group_info'] = {
                    "seller_name": product.seller_name, 
                    "proveedor_name": product.proveedor_name
                }
                st.session_state['current_view'] = 'conteo_stock_por_seller'
                st.rerun()
        st.write('---')
        
def conteo_stock_por_seller(seller_products):
    current_group_info = st.session_state['current_group_info']
    if st.button('Regresar'):
        st.session_state['current_view'] = 'detalle_ordenes_por_seller'
        st.rerun()
    st.markdown(f'### Seller: {current_group_info["seller_name"]}')
    st.markdown(f'### Proveedor: {current_group_info["proveedor_name"]}')
    