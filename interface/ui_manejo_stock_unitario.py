import sys
sys.path.append('..')
import pandas as pd
import streamlit as st
import streamlit_shadcn_ui as ui
from fpdf import FPDF
import base64
from datetime import datetime, timedelta
from db.db_manejo_stock_unitario import get_one_product, get_stok_in_orders, insert_to_stock_count_table, update_product_status, update_product_stock_on_db

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

def off_info():
    """
    Searched product's info reset function
    """
    st.session_state['show_info_stock_unitario'] = False

def search_product_by_sku(sku_list):
    """
    Frontend for search a product by sku
    """

    st.title("Manejo Stock Unitario")
    st.markdown("#### Búsqueda de producto por sku:")
    selected_sku = st.selectbox("Ingresa el SKU:", options= sku_list, index= None, placeholder= "Escribe un SKU o una parte de él")
    pressed = st.button("**Buscar**")

    if pressed:
        st.session_state['show_info_stock_unitario'] = not st.session_state['show_info_stock_unitario']
    
    if st.session_state['show_info_stock_unitario']:
        need_val = False
        state = 'no necesita validación'

        product = get_one_product(selected_sku)
        stock_in_order = get_stok_in_orders(selected_sku)

        container = st.container()
        with container:
            if not product['product_id'][0] == None:
                stock_fisico = int(stock_in_order) + int(float(product['stock'][0]))
                print(stock_fisico)
                st.write('---')
                if product["img_url"][0] is not  None:
                    st.image(product["img_url"][0], use_column_width=False, width=200 )
                else:
                    st.markdown('Sin imagen')
                st.markdown(f'Nombre: {product["post_title"][0]}')
                st.markdown(f'SKU: {product["sku"][0]}')
                st.markdown(f'Unidades: {product["units_per_pack"][0]}')
                inserted_stock = st.number_input('Conteo físico', min_value=0, step=1)
                if int(inserted_stock) != stock_fisico:
                    st.error('Validacion')
                    need_val = True
                    state = 'necesita validación'
                boton = st.button("**Terminar Conteo**")
                respuesta = ui.alert_dialog(show=boton, title="Confirmación de conteo", description=f"El producto ajustado {state}.", confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
                if respuesta:
                    producto = {
                        "costo": float(product['cost'][0]),
                        "inserted_stock": int(inserted_stock),
                        "stock_fisico": stock_fisico,
                        "difference": inserted_stock - stock_fisico,
                        "stock_web": int(float(product['stock'][0])),
                        "sku": product['sku'][0],
                        "active_count": int(stock_in_order),
                        "product_id": int(product['product_id'][0]),
                        "need_val": need_val
                    }   
                    update_product_stock(producto, need_val, product["sku"][0])
                    st.session_state.current_view = 'finalizar_manejo_stock_unitario'
                    st.session_state.producto_alterado = producto
                    st.rerun()
            else:
                st.warning("**Escriba un SKU existente o corrija el escrito.**")

def update_product_stock(producto, need_val, sku):
    '''
    Checks if product stock can be automatically updated or needs validation. 
    In case it can be updated, updates the stock, else sends it to validation.
    '''
    if need_val:
        if producto['difference'] < 0 and int(abs(producto['difference']) * float(producto['costo'])) >= 2000:
            update_product_status(producto['product_id'])

        elif producto['difference'] != 0:
            update_product_stock_on_db(producto['product_id'], producto['stock_web'], int(producto['stock_web'] + producto['difference']), sku)
            insert_to_stock_count_table(producto['product_id'], producto['stock_web'], producto['active_count'], producto['stock_fisico'], producto['inserted_stock'], producto['difference'], int(producto['stock_web'] + producto['difference']), st.session_state.useremail)
    else:
        insert_to_stock_count_table(producto['product_id'], producto['stock_web'], producto['active_count'], producto['stock_fisico'], producto['inserted_stock'], producto['difference'], int(producto['stock_web'] + producto['difference']), st.session_state.useremail)

def finalizar_manejo_stock_unitario(producto):
    '''
    Front end view for ending the stock counting process
    '''
    current_utc_time = datetime.utcnow()
    cst_offset = timedelta(hours=-6)
    cst_time = current_utc_time + cst_offset
    mysql_datetime_cst = cst_time.strftime('%Y-%m-%d %H:%M:%S')
    st.markdown('## Finalización de conteo')
    if 'is_generated' not in st.session_state:
        st.session_state['is_generated'] = False
    st.write('---')
    st.markdown(f"### Producto revisado: {producto['sku']}")
    if producto['need_val'] and producto['difference'] * producto['costo'] > 2000:
        val = 'Necesita validación'
    else:
        val = 'No necesita validación'

    st.markdown(f"### Estado: {val}.")

    if st.button('Generar stock'):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 8)
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
        if producto['need_val']:
            pdf.cell(50, 10, f"{producto['sku']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['stock_web']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['active_count']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['stock_fisico']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['inserted_stock']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['difference']}", 1, align='C')
            pdf.cell(22, 10, f"{int(producto['stock_web'] + producto['difference'])}", 1, align='C')
            pdf.ln()
        else:
            pdf.cell(50, 10, f"{producto['sku']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['stock_web']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['active_count']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['stock_fisico']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['inserted_stock']}", 1, align='C')
            pdf.cell(22, 10, f"{producto['difference']}", 1, align='C')
            pdf.cell(22, 10, f"{int(producto['stock_web'] + producto['difference'])}", 1, align='C')
            pdf.ln()
        html = create_download_link(pdf.output(dest="S").encode("latin-1"), 'reporte_stock_' + str(mysql_datetime_cst))
        st.session_state['is_generated'] = True
        st.markdown(html, unsafe_allow_html=True)
    if st.session_state['is_generated']:
        go_back = st.button('Regresar al inicio', key='go_back_btn')
        if go_back:
            st.session_state.current_view = 'manejo_stock_unitario'
            st.session_state['show_info_stock_unitario'] = False
            st.rerun()