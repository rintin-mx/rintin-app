
import sys
sys.path.append('..')

from integration.insert_to_S3 import insertImage
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import base64
from fpdf import FPDF
import time

from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_ingreso_ordenes_compra import updateOrdenCompraStatus
from db.db_ordenes_compra import insertOrdenCompra, update_oi_values, update_product, updateOrdenCompra, deleteProducts
from datetime import datetime
import streamlit.components.v1 as components
from integration.aws_integration import insert_product_to_db

list_test = []

bodega_destino = {
    "centro_cdmx": "Bodega Centro CDMX",
    "oaxaca": "Bodega Oaxaca",
    "aj_cdmx": "A&J CDMX",
    "showroom": "Showroom"
}

# Funcion para cambio de vista a terminación de orden
def terminarOrden():
    st.session_state['current_view'] = 'terminar_orden_compra'
    st.rerun()

# Funcion para cambio de vista paraa agregar productos de orden
# Se maneja un diccionario cuya llave es el nombre del seller y su valor es una lista de productos
# De esta forma siempre se guardarán los productos agregados al seller antes de que se confirme para BD
def verDetalle(seller_name):
    st.session_state.current_view = 'detalleOrdenCompra'
    if "dictProductos" not in st.session_state:
        st.session_state['dictProductos']={seller_name: []}
    elif seller_name not in st.session_state['dictProductos']:
        tempDict = st.session_state['dictProductos']
        tempDict[seller_name] = []
        st.session_state['dictProductos'] = tempDict
    st.rerun()

# Funcion para cambio de vista para editar un producto de una orden
def editarProducto(index, seller_name):
    productsArr = st.session_state['dictProductos'][seller_name]
    st.session_state['editProduct'] = productsArr[index]
    st.session_state['editProductIndex'] = index
    st.session_state.current_view = 'detalleOrdenCompra'
    st.rerun()

# Funcion para agregar un producto a lista del diccionario del seller
def agregarProducto(producto):
    tempArr = st.session_state['dictProductos'][st.session_state['currentSeller']]
    tempArr.append(producto)
    st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr 
    st.session_state.current_view = 'ordenesCompra'
    st.rerun()

# Funcion para modificar un producto de la lista del diccionario del seller
def modificarProducto(producto):
    tempArr = st.session_state['dictProductos'][st.session_state['currentSeller']]
    tempArr[st.session_state['editProductIndex']] = producto
    st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr
    st.session_state.current_view = 'ordenesCompra'
    del st.session_state['editProduct']
    del st.session_state['editProductIndex']
    st.rerun()


# Funcion para crear link de descarga de pdg
def create_download_link(val, filename):
    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Descargar PDF</a>'


# Vista de confirmación de orden de compra
def UITTerminarOrdenCompra(parents, order_data):
    order_parent_list = [0]
    bodegas_recepcion = ['centro_cdmx', 'oaxaca', 'aj_cdmx', 'showroom']
    if parents is not None and len(parents['id_orden_compra']) > 0:
        order_parent_list = order_parent_list + parents['id_orden_compra']
    if order_data is not None:
        bodevaValIndex = bodegas_recepcion.index(order_data['bodega_recepcion'][0])
        parentIndex = order_parent_list.index(order_data['orden_compra_padre'][0])
    else:
        bodevaValIndex = 0
        parentIndex = 0
    total_cobro = 0
    for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
        total_cobro = total_cobro + (float(value['costo']) * value['cantidad_pack'])
    if 'isSaved' not in st.session_state:    
        if st.button('Volver'):
            st.session_state.current_view = 'ordenesCompraMenu'
            st.rerun()
    tableArr = []
    for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
        tableArr.append({
            'Nombre Producto': value['nombre'],
            'SKU': value['sku'],
            'Cantindad:': value['cantidad_pack'],
            'Total': str(f"${round(value['cantidad_pack'] * value['costo'], 2):,}")
        })
    # Despliegue de información de orden de compra
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### **Seller:** ' + st.session_state['currentSeller'])
    with col2:
        if 'ordenCompraId' in st.session_state:
            st.markdown('#### **Orden de Compra:** ' + str(st.session_state['ordenCompraId']))
    st.write('---')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('**Total Productos**')
        st.text(str(len(st.session_state['dictProductos'][st.session_state['currentSeller']])))
    with col2:
        st.markdown('**Total a Pagar**')
        st.text(str(f'${round(total_cobro, 2):,}'))
    st.write("---")
    st.table(tableArr)
    col1, col2 = st.columns(2)
    with col1:
        orden_padre = st.selectbox('Orden Padre', options=order_parent_list, index=parentIndex)
    with col2:
        bodega_recepcion = st.selectbox('Bodega Recepción', options=bodegas_recepcion, index=bodevaValIndex)
    # Generación de PDF
    if 'ordenCompraId' in st.session_state:
        if st.button('Generar PDF'):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 8)
            pdf.cell(62, 10, 'Orden de Compra: ' + str(st.session_state['ordenCompraId']), 0, align='C')
            pdf.cell(62, 10, 'Seller: ' + str(st.session_state['currentSeller']), 0, align='C')
            pdf.cell(62, 10, 'Fecha Creación: ' + str(st.session_state['fechaCreacionOrden']), 0, align='C')
            pdf.ln()
            pdf.cell(62, 10, 'Total a Pagar', 1, align='C')
            pdf.cell(62, 10, 'Total Productos', 1, align='C')
            pdf.cell(62, 10, 'Almacen', 1, align='C')
            pdf.ln()
            pdf.cell(62, 10, str(f'${round(total_cobro, 2):,}'), 1, align='C')
            pdf.cell(62, 10, str(len(st.session_state['dictProductos'][st.session_state['currentSeller']])), 1, align='C')
            pdf.cell(62, 10, bodega_destino[bodega_recepcion], 1, align='C')
            pdf.ln()
            pdf.ln()
            pdf.cell(21, 10, 'Nombre', 1, align='C')
            pdf.cell(15, 10, 'SKU', 1, align='C')
            pdf.cell(18, 10, 'Marca', 1, align='C')
            pdf.cell(32, 10, 'Dueño Producto', 1, align='C')
            pdf.cell(32, 10, 'Proveedor', 1, align='C')
            pdf.cell(21, 10, 'Tipo', 1, align='C')
            pdf.cell(15, 10, 'Costo', 1, align='C')
            pdf.cell(15, 10, 'Cantidad', 1, align='C')
            pdf.cell(18, 10, 'Total', 1, align='C')
            pdf.ln()
            pdf.set_font('Arial', '', 6)
            for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
                pdf.cell(21, 10, str(value['nombre']), 1, align='C')
                pdf.cell(15, 10, str(value['sku']), 1, align='C')
                pdf.cell(18, 10, str(value['marca']), 1, align='C')
                pdf.cell(32, 10, f"{value['fabricante_name']}_{value['fabricante']}", 1, align='C')
                pdf.cell(32, 10, f"{value['proveedor_name']}_{value['proveedor']}", 1, align='C')
                pdf.cell(21, 10, str(value['tipo_producto']), 1, align='C')
                pdf.cell(15, 10, str(value['costo']), 1, align='C')
                pdf.cell(15, 10, str(value['cantidad_pack']), 1, align='C')
                total = value['cantidad_pack'] * value['costo']
                pdf.cell(18, 10, str(f"${round(total,2):,}"), 1, align='C')
                pdf.ln()
            html = create_download_link(pdf.output(dest="S").encode("latin-1"), 'orden_de_compra_' + str(st.session_state['ordenCompraId']))
            st.markdown(html, unsafe_allow_html=True)

    # INSERT a BD
    if 'isEditing' in st.session_state and 'isSaved' not in st.session_state:
        if st.button('Guardar cambios'):
            orderDict = {            
                'total_paquetes': len(st.session_state['dictProductos'][st.session_state['currentSeller']]),
                'total_cost': total_cobro,
                'fecha_edicion': time.strftime('%Y-%m-%d %H:%M:%S'),
                'bodega_recepcion': bodega_recepcion,
                'orden_padre': orden_padre
            }
            if 'deletedProducts' in st.session_state and len(st.session_state['deletedProducts']) > 0:
                deleteProducts(st.session_state['deletedProducts'], st.session_state['ordenCompraId'])
            updateOrdenCompra(st.session_state['ordenCompraId'], orderDict, st.session_state['dictProductos'][st.session_state['currentSeller']])
            st.session_state['isSaved'] = True
            st.rerun()
            
    elif 'isSaved' not in st.session_state:
        if st.button('Terminar Orden de Compra'):
            with st.spinner(f'Agregando información a base de datos...'):
                fechaCreacion = time.strftime('%Y-%m-%d %H:%M:%S')
                orderDict = {
                    'codigo_seller': st.session_state['currentSellerId'],
                    'seller_name': st.session_state['currentSeller'],
                    'total_paquetes': len(st.session_state['dictProductos'][st.session_state['currentSeller']]),
                    'total_cost': total_cobro,
                    'bodega_recepcion': bodega_recepcion,
                    'orden_padre': orden_padre,
                    'usuario_creacion': st.session_state['username'],
                    'fecha_creacion': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'fecha_edicion': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                res = insertOrdenCompra(orderDict, st.session_state['dictProductos'][st.session_state['currentSeller']])
                if(res):
                    st.session_state['ordenCompraId'] = res
                    st.session_state['fechaCreacionOrden'] = fechaCreacion
                    st.session_state['isSaved'] = True
                    st.rerun()
    
    elif 'isSaved' in st.session_state:
        st.success('Orden guardada con éxito')
        if st.button('Regresar al Inicio'):
            st.session_state.current_view = 'ordenesCompraMenu'
            st.rerun()
        

def UITOrdenesCompraMenu():
    
    st.title('Ordenes de compra')
    if st.button('Creación ordenes de compra por csv'):
        st.session_state.current_view = 'ordenesCompraCsv'
        st.rerun()
    if st.button('Edición ordenes de compra'):
        st.session_state.current_view = 'editOrdenesCompra'
        st.rerun()

def UITOrdenesCompraCSV(data, fabricante, proveedores):
    if st.button('Volver'):
        st.session_state.current_view = 'ordenesCompraMenu'
        st.rerun()
    st.session_state['dictProductos'] = {}
    st.title('Creación de ordenes de compra por CSV')
    st.markdown('''
                <p>
                    Ingresa la orden de compra en un archivo ".csv". El archivo debe seguir el siguiente <a href="https://rintin-internal-apps.s3.us-east-2.amazonaws.com/example_files/template_orden_compra.csv" download="true">formato.</a>
                </p>''', unsafe_allow_html=True)
    if 'currentSeller' not in st.session_state:
        index = None
    else:
        index = data['dokan_store_name'].index(st.session_state['currentSeller'])
    seller = st.selectbox('Seller', data['dokan_store_name'], index=index)
    if seller is not None:
        index = data['dokan_store_name'].index(seller)
        st.session_state['currentSellerId'] = data['user_id'][index]
        st.session_state['currentSeller'] = seller
    csv_file = st.file_uploader('Archivo csv', type='.csv', accept_multiple_files=False)
    button = st.button('Confirmar')
    if button and csv_file is not None and seller is not None:
        try:
            csv_df = pd.read_csv(csv_file)
            csv_df = csv_df[['sku','nombre','paquetes', 'piezas_por_paquete', 'costo_por_paquete', 'marca', 'dueno_producto', 'proveedor', 'sku_rintin']]
            csv_dict = csv_df.to_dict(orient='list')
            #'Unidad', 'Paquete'
            tempArr = []
            for i in range(len(csv_dict['sku'])):   
                if csv_dict['piezas_por_paquete'][i] == 1:
                    tipo_producto = 'Unidad'
                else:
                    tipo_producto = 'Paquete'
                fabricanteIndex = fabricante['user_id'].index(csv_dict['dueno_producto'][i])
                fabricante_name = fabricante['meta_value'][fabricanteIndex]
                proveedorIndex = proveedores['user_id'].index(csv_dict['proveedor'][i])
                proveedor_name = proveedores['meta_value'][proveedorIndex]
                productDict = {
                    'nombre': csv_dict['nombre'][i],
                    'sku': csv_dict['sku'][i],
                    'tipo_producto': tipo_producto,
                    'cantidad_pack': csv_dict['paquetes'][i],
                    'units_per_pack': csv_dict['piezas_por_paquete'][i],
                    'costo': csv_dict['costo_por_paquete'][i],
                    'img_url': '',
                    'marca': csv_dict['marca'][i],
                    'fabricante': csv_dict['dueno_producto'][i],
                    'fabricante_name': fabricante_name,
                    'proveedor': csv_dict['proveedor'][i],
                    'proveedor_name': proveedor_name,
                    'sku_rintin': csv_dict['sku_rintin'][i]
                }
                tempArr.append(productDict)
            st.session_state['dictProductos'][seller] = tempArr
            st.session_state['current_view'] = 'terminar_orden_compra'
            st.rerun()
        except Exception as e:
            print(e)
            st.error('Hubo un error al procesar el archivo, revisa que siga el formato correctamente.')
    st.write(
            """<style>
            [data-testid="stHorizontalBlock"] {
                align-items: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

