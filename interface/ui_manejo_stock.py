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
                    "proveedor_name": product.proveedor_name,
                    "seller_id": product.seller_id,
                    "proveedor_id": product.proveedor_id
                }
                st.session_state['current_view'] = 'conteo_stock_por_seller'
                st.rerun()
        st.write('---')

def check_box_change_handler(index, check_box_value):
    '''
    Function for updating the checked attribute of a product in the all_seller_products DataFrame
    
    Parameters:
    index (int): Product index in all_seller_products DataFrame
    checked (boolean): Checkbox value
    '''
    seller_products = st.session_state['all_seller_products']
    seller_products.at[index, 'checked'] = check_box_value
    st.session_state['all_seller_products'] = seller_products

def conteo_stock_por_seller(seller_products, active_order_products):
    '''
    Front end view for detalle ordenes por seller page
    
    Parameters:
    seller_products (list): Product list
    active_order_products (dict): Dictionary containing the products in active orders
    '''
    if 'all_seller_products' not in st.session_state:
        st.session_state['all_seller_products'] = seller_products
    current_group_info = st.session_state['current_group_info']
    if st.button('Regresar'):
        st.session_state['current_view'] = 'detalle_ordenes_por_seller'
        st.rerun()
    st.markdown(f'### Seller: {current_group_info["seller_name"]}')
    st.markdown(f'### Proveedor: {current_group_info["proveedor_name"]}')
    conteo_filter = st.selectbox('Estado de conteo', options=['Contado', 'No contado'], index=None)
    if conteo_filter is not None and conteo_filter == 'Contado':
        df = st.session_state['all_seller_products']
        filtered_products = df[df['checked']]
    elif conteo_filter is not None and conteo_filter == 'No contado':
        df = st.session_state['all_seller_products']
        filtered_products = df[~df['checked']]
    else:
        filtered_products = st.session_state['all_seller_products']
    for i, product in filtered_products.iterrows():
        # Try catch in case product_id is not in active_order_products list
        try:
            product_index = active_order_products['product_id'].index(product['product_id'])
            active_product_stock = active_order_products['stock_count'][product_index]
        except ValueError:
            active_product_stock = 0
        web_stock = int(active_product_stock) + int(product['stock'])
        st.write('---')
        if product["img_url"] is not  None:
            st.image(product["img_url"], use_column_width=True )
        else:
            st.markdown('Sin imagen')
        st.markdown(f'Nombre: {product["post_title"]}')
        st.markdown(f'SKU: {product["sku"]}')
        st.markdown(f'Unidades: {product["units_per_pack"]}')
        st.markdown(f'Estado del producto: {product["post_status"]}')
        st.markdown(web_stock)
        
        is_checked = st.checkbox('Conteo completado', key=f'{i}_checkbox', value=st.session_state['all_seller_products'].at[i, 'checked'])
        seller_products_temp = st.session_state['all_seller_products']
        seller_products_temp.at[i, 'checked'] = is_checked
        st.session_state['all_seller_products'] = seller_products_temp
        inserted_stock = st.number_input('Conteo físico', min_value=0, step=1, key=f'{i}_number_input')
        if int(inserted_stock) != web_stock:
            st.error('Validacion')