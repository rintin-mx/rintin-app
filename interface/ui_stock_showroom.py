import streamlit as st
import pandas as pd

from db.db_stock_showroom import get_one_product_info
from integration.cache_api import update_order_metadata

def UIstartPage():
    st.write("###")
    st.header("Stock Showroom")
    st.divider()
    
    if st.button("Actualizar un producto"):
        st.session_state['current_view'] = 'actualizar_showroom'
        st.rerun()
    
    if st.button("Visualizar todos los productos"):
        st.session_state['current_view'] = 'visualizar_showroom'
        st.rerun()

def UIvisualizarShowroom(data):
    st.header("Productos con Stock en Showroom")
    st.write("###")
    if st.button("Regresar"):
        st.session_state['current_view'] = 'showroom'
        st.rerun()

    if not data.empty:
        for i in range(len(data['product_id'])):
            st.image(data['img_url'][i], width=400)
            st.write(f"**SKU**: {data['sku'][i]}")
            st.write(f"**Proveedor**: {data['proveedor'][i]}")
            st.write(f"**Dueño del producto**: {data['dueno_producto'][i]}")
            st.write(f"**Marca del producto**: {data['marca'][i]}")
            st.write(f"**Stock real**: {data['real_stock'][i]}")
            if data['stock_showroom'][i] is None:
                st.write("**Stock en showroom**: 0")
            else:
                st.write(f"**Stock en showroom**: {data['stock_showroom'][i]}")
            st.write(f"**Nombre del producto**: {data['product_name'][i]}")
            st.write(f"**Seller**: {data['seller'][i]}")
            st.divider()

def UIactualizarShowroom(sku_list):
    if 'is_clicked' not in st.session_state:
        st.session_state['is_clicked'] = False
    st.header("Busca un producto")
    st.write("###")
    if st.button("Regresar"):
        st.session_state['current_view'] = 'showroom'
        st.rerun()

    sku_seleccionado = st.selectbox("Ingresa el SKU:", options= sku_list, index= None, placeholder= "Escribe un SKU o una parte de él")
    confirm_btn = st.button("Buscar", key='confirm_btn')
    if st.session_state.confirm_btn or st.session_state.is_clicked:
        st.session_state.is_clicked = True
        st.divider()
        
        info_producto = get_one_product_info(sku_seleccionado)
        if pd.DataFrame(info_producto).empty:
            st.warning("## Este SKU no existe. Verifique que sea el correcto o ingrese uno diferente.")
        else:
            st.image(info_producto['img_url'][0], width=400)
            st.write(f"**SKU**: {info_producto['sku'][0]}")
            st.write(f"**Proveedor**: {info_producto['proveedor'][0]}")
            st.write(f"**Dueño del producto**: {info_producto['dueno_producto'][0]}")
            st.write(f"**Marca del producto**: {info_producto['marca'][0]}")
            st.write(f"**Stock real**: {info_producto['real_stock'][0]}")
            if info_producto['stock_showroom'][0] is None:
                st.write("**Stock en showroom**: 0")
            else:
                st.write(f"**Stock en showroom**: {info_producto['stock_showroom'][0]}")
            st.write(f"**Nombre del producto**: {info_producto['product_name'][0]}")
            st.write(f"**Seller**: {info_producto['seller'][0]}")
            new_stock = st.number_input('Nuevo Stock en Showroom', min_value=0, step=1)

            if st.button("**Actualizar stock en showroom**"):

                update_order_metadata([info_producto['product_id'][0]], '_stock_shr', str(new_stock))
                
                st.session_state.current_view = 'finalizar_actualizacion'
                st.session_state.shr_prod_sku = info_producto['sku'][0]
                st.session_state.shr_new_stock = new_stock
                st.session_state.is_clicked = False
                st.rerun()

def UIfinalizarActualizacion(shr_prod_sku, shr_new_stock):
    st.markdown(f'## Se actualizó el producto con sku {shr_prod_sku} a una cantidad en showroom {shr_new_stock}.')
    st.write('---')

    if st.button('Regresar'):
        st.session_state['current_view'] = 'showroom'
        if 'shr_prod_sku' in st.session_state:
            del st.session_state['shr_prod_sku']
        if 'shr_new_stock' in st.session_state:
            del st.session_state['shr_new_stock']
        
        st.rerun()