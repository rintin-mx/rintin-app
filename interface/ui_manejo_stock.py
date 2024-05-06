import sys
sys.path.append('..')
import streamlit as st
from db.db_manejo_stock import update_product_status_bulk, update_product_stock_on_db, insert_to_stock_count_table, update_product_status
import streamlit_shadcn_ui as ui
from fpdf import FPDF
import base64
from datetime import datetime, timedelta

def handle_select_change():
    '''
    Handles select filter value change by setting the needed states
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
        if st.button('Comenzar stock', key=f'{i}_button'):
            st.session_state['current_group_info'] = {
                "seller_name": product.seller_name, 
                "proveedor_name": product.proveedor_name,
                "seller_id": product.seller_id,
                "proveedor_id": product.proveedor_id
            }
            st.session_state['current_view'] = 'conteo_stock_por_seller'
            st.rerun()
        st.write('---')

def handle_input_change(id):
    '''
    Function for updating the counted stock attribute of a product in the products_by_proveedor_seller DataFrame
    
    Parameters:
    id (int): Product id in products_by_proveedor_seller DataFrame
    '''
    if f'{id}_number_input' not in st.session_state:
        st.session_state[f'{id}_number_input'] = st.session_state['products_by_proveedor_seller'].at[id, 'counted']
    st.session_state['products_by_proveedor_seller'].at[id, 'counted'] = st.session_state[f'{id}_number_input']


def update_product_stock():
    '''
    Checks if product stock can be automatically updated or needs validation. 
    In case it can be updated, updates the stock, else sends it to validation.
    '''
    products_dict = st.session_state['products_con_validacion']
    products_ok_dict = st.session_state['products_ok']
    for product in products_dict:
        if products_dict[product]['difference'] < 0 and int(abs(products_dict[product]['difference']) * float(products_dict[product]['cost'])) >= 2000:

            update_product_status(product, 'proceso_stock')
        elif products_dict[product]['difference'] != 0:
            update_product_stock_on_db(product, products_dict[product]['stock_web'], int(products_dict[product]['stock_web'] + products_dict[product]['difference']))
            insert_to_stock_count_table(product, products_dict[product]['stock_web'], products_dict[product]['active_count'], products_dict[product]['stock_fisico'], products_dict[product]['inserted_stock'], products_dict[product]['difference'], int(products_dict[product]['stock_web'] + products_dict[product]['difference']), st.session_state.useremail)
    for product in products_ok_dict:
        if products_ok_dict[product]['stock_web'] > 0:
            update_product_status(product, 'publish')
        else:
            update_product_status(product, 'trash')
        insert_to_stock_count_table(product, products_ok_dict[product]['stock_web'], products_ok_dict[product]['active_count'], products_ok_dict[product]['stock_fisico'], products_ok_dict[product]['inserted_stock'], products_ok_dict[product]['difference'], int(products_ok_dict[product]['stock_web'] + products_ok_dict[product]['difference']), st.session_state.useremail)

def check_box_change_handler(id, cost, inserted_stock, stock_fisico, stock_web, sku, active_count):
    '''
    Function for updating the checked attribute of a product in the products_by_proveedor_seller DataFrame
    
    Parameters:
    id (int): Product id in products_by_proveedor_seller DataFrame
    cost (string): Product cost
    inserted_stock (int): Stock counted by user
    stock_fisico (int): Total stock (web_stock + active_stock)
    stock_web (int): Stock in database
    sku (string): Product sku
    active_count (int): Stock reserved for pre-picked orders
    '''
    if f'{id}_checkbox' not in st.session_state:
        st.session_state[f'{id}_checkbox'] = st.session_state['products_by_proveedor_seller'].at[id, 'checked']
    st.session_state['products_by_proveedor_seller'].at[id, 'checked'] = st.session_state[f'{id}_checkbox']
    if st.session_state[f'{id}_checkbox'] and inserted_stock - stock_fisico != 0:
        if id in st.session_state['products_ok']:
            del st.session_state['products_ok'][id]
        st.session_state['products_con_validacion'][id] = {"cost": cost,"inserted_stock": inserted_stock, "stock_fisico": stock_fisico, "difference": inserted_stock - stock_fisico, "stock_web": stock_web, "sku": sku, "active_count": active_count}
    if st.session_state[f'{id}_checkbox'] and inserted_stock - stock_fisico == 0:
        if id in st.session_state['products_con_validacion']:
            del st.session_state['products_con_validacion'][id]
        st.session_state['products_ok'][id] = {"cost": cost,"inserted_stock": inserted_stock, "stock_fisico": stock_fisico, "difference": inserted_stock - stock_fisico, "stock_web": stock_web, "sku": sku, "active_count": active_count}
    if (not st.session_state[f'{id}_checkbox']) and id in st.session_state['products_con_validacion']:
        del st.session_state['products_con_validacion'][id]
    if (not st.session_state[f'{id}_checkbox']) and id in st.session_state['products_ok']:
        del st.session_state['products_ok'][id]


def create_download_link(val, filename):
    '''
    Creates a url for downloading the pdf file
    
    Parameters:
    val (file): PDF file
    filename (string): File name
    
    Return (HTML component): A tag containing the download link
    '''
    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Descargar PDF</a>'

def finalizar_manejo_stock():
    '''
    Front end view for ending the stock counting process
    '''
    current_utc_time = datetime.utcnow()
    cst_offset = timedelta(hours=-6)
    cst_time = current_utc_time + cst_offset
    mysql_datetime_cst = cst_time.strftime('%Y-%m-%d %H:%M:%S')
    current_group_info = st.session_state['current_group_info']
    st.markdown('## Finalización de conteo')
    if 'is_generated' not in st.session_state:
        st.session_state['is_generated'] = False
    st.write('---')
    st.markdown(f'### Seller: {current_group_info["seller_name"]}')
    st.markdown(f'### Proveedor: {current_group_info["proveedor_name"]}')
    st.markdown(f'### Todos los productos: {len(st.session_state["products_ok"].keys()) + len(st.session_state["products_con_validacion"].keys())}')
    st.markdown(f'### Productos OK: {len(st.session_state["products_ok"].keys())}')
    st.markdown(f'### Productos con diferencias: {len(st.session_state["products_con_validacion"].keys())}')
    
    product_dict = st.session_state['products_con_validacion']
    ok_product_dict = st.session_state['products_ok']
    if st.button('Generar stock'):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(62, 10, 'Seller: ' + str(current_group_info["seller_name"]), 0, align='C')
        pdf.cell(62, 10, 'Proveedor: ' + str(current_group_info["proveedor_name"]), 0, align='C')
        pdf.cell(62, 10, 'Fecha Creación: ' + str(mysql_datetime_cst), 0, align='C')
        pdf.ln()
        pdf.cell(50, 10, 'Producto (SKU)', 1, align='C')
        pdf.cell(22, 10, 'Stock sistema', 1, align='C')
        pdf.cell(22, 10, 'Stock reservado', 1, align='C')
        pdf.cell(22, 10, 'Total stock', 1, align='C')
        pdf.cell(22, 10, 'Stock contado', 1, align='C')
        pdf.cell(22, 10, 'Diferencias', 1, align='C')
        pdf.cell(22, 10, 'Nuevo Stock', 1, align='C')
        pdf.ln()
        for product in product_dict:
            pdf.cell(50, 10, f"{product_dict[product]['sku']}", 1, align='C')
            pdf.cell(22, 10, f"{product_dict[product]['stock_web']}", 1, align='C')
            pdf.cell(22, 10, f"{product_dict[product]['active_count']}", 1, align='C')
            pdf.cell(22, 10, f"{product_dict[product]['stock_fisico']}", 1, align='C')
            pdf.cell(22, 10, f"{product_dict[product]['inserted_stock']}", 1, align='C')
            pdf.cell(22, 10, f"{product_dict[product]['difference']}", 1, align='C')
            pdf.cell(22, 10, f"{int(product_dict[product]['stock_web'] + product_dict[product]['difference'])}", 1, align='C')
            pdf.ln()
        for product in ok_product_dict:
            pdf.cell(50, 10, f"{ok_product_dict[product]['sku']}", 1, align='C')
            pdf.cell(22, 10, f"{ok_product_dict[product]['stock_web']}", 1, align='C')
            pdf.cell(22, 10, f"{ok_product_dict[product]['active_count']}", 1, align='C')
            pdf.cell(22, 10, f"{ok_product_dict[product]['stock_fisico']}", 1, align='C')
            pdf.cell(22, 10, f"{ok_product_dict[product]['inserted_stock']}", 1, align='C')
            pdf.cell(22, 10, f"{ok_product_dict[product]['difference']}", 1, align='C')
            pdf.cell(22, 10, f"{int(ok_product_dict[product]['stock_web'] + ok_product_dict[product]['difference'])}", 1, align='C')
            pdf.ln()
        html = create_download_link(pdf.output(dest="S").encode("latin-1"), 'reporte_stock_' + str(mysql_datetime_cst))
        st.session_state['is_generated'] = True
        st.markdown(html, unsafe_allow_html=True)
    if st.session_state['is_generated']:
        go_back = st.button('Regresar al inicio', key='go_back_btn')
        if go_back:
            st.session_state.current_view = 'detalle_ordenes_por_seller'
            st.session_state['is_generated'] = False
            st.rerun()

def conteo_stock_por_seller():
    '''
    Front end view for detalle ordenes por seller page
    '''
    if 'products_con_validacion' not in st.session_state:
        st.session_state['products_con_validacion'] = {}
    if 'products_ok' not in st.session_state:
        st.session_state['products_ok'] = {}
    df = st.session_state['products_by_proveedor_seller']
    product_names = df['post_title'].unique()
    st.markdown('''<style>
        .block-container{
            padding-top: 0
        }
        div[data-testid="stVerticalBlock"]:has(div.container_1){
            top: 30px;
            padding-bottom: 20px;
        }
        div[data-testid="stVerticalBlock"]:has(div.container_2){
            margin-top: 80px;
        }
        div:has( >.element-container div.floating) {
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 30px;
            z-index: 99;
               background-color: white !important;
        }
    </style>
    
    ''', unsafe_allow_html=True)
    container = st.container()
    with container:
        st.write('<div class="floating"></div>', unsafe_allow_html=True)
        if st.button('Regresar'):
            st.session_state['current_view'] = 'detalle_ordenes_por_seller'
            st.rerun()
        name_filter = st.selectbox('Nombre de producto', options=product_names, index=None)
        button = st.button('Terminar conteo')
        respuesta = ui.alert_dialog(show=button, title="Confirmación de conteo", description=f'Productos OK: {len(st.session_state["products_ok"].keys())} \n Productos con diferencias: {len(st.session_state["products_con_validacion"].keys())}', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
        if respuesta:
            update_product_stock()
            st.session_state.current_view = 'finalizar_manejo_stock'
            st.rerun()

    if name_filter is not None:
        filtered_products = df[df['post_title'] == name_filter]
    else:
        filtered_products = df


    container2 = st.container()
    with container2:
        current_group_info = st.session_state['current_group_info']
        st.markdown(f'### Seller: {current_group_info["seller_name"]}')
        st.markdown(f'### Proveedor: {current_group_info["proveedor_name"]}')
        st.write('<div class="container_2"></div>', unsafe_allow_html=True)
        
        for i, product in filtered_products.iterrows():
            stock_fisico = int(product['active_count']) + int(float(product['stock']))
            st.write('---')
            if product["img_url"] is not  None:
                st.image(product["img_url"], use_column_width=False, width=200 )
            else:
                st.markdown('Sin imagen')
            st.markdown(f'Nombre: {product["post_title"]}')
            st.markdown(f'SKU: {product["sku"]}')
            st.markdown(f'Unidades: {product["units_per_pack"]}')
            inserted_stock = st.number_input('Conteo físico', min_value=0, step=1, key=f'{i}_number_input', on_change=handle_input_change(i))
            if int(inserted_stock) != stock_fisico:
                st.error('Validacion')
            st.checkbox('Contado', key=f'{i}_checkbox', on_change=check_box_change_handler(i, product['cost'], inserted_stock, stock_fisico, int(float(product['stock'])), product["sku"], product['active_count']))

