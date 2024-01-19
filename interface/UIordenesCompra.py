
import sys
sys.path.append('..')

from integration.insertToS3 import insertImage
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import base64
from fpdf import FPDF
import asyncio
import time
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_ingresoOrdenesCompra import updateOrdenCompraStatus
from db.db_ordenesCompra import insertOrdenCompra, update_oi_values, update_product, updateOrdenCompra, deleteProducts
from datetime import datetime
import streamlit.components.v1 as components

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

async def update_order_note__wordpress(order_id, order_notes):
    result = await endpoint_write_order_note(order_id, order_notes)
    return result

list_test = []

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
    print(producto)
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
    print('order')
    print(order_data)
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
            st.session_state.current_view = 'ordenesCompra'
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
            pdf.cell(62, 10, str(bodega_recepcion), 1, align='C')
            pdf.ln()
            pdf.ln()
            pdf.cell(31, 10, 'Nombre de producto', 1, align='C')
            pdf.cell(31, 10, 'SKU', 1, align='C')
            pdf.cell(31, 10, 'Tipo de Producto', 1, align='C')
            pdf.cell(31, 10, 'Costo', 1, align='C')
            pdf.cell(31, 10, 'Cantidad', 1, align='C')
            pdf.cell(31, 10, 'Total', 1, align='C')
            pdf.ln()
            pdf.set_font('Arial', '', 6)
            for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
                pdf.cell(31, 10, str(value['nombre']), 1, align='C')
                pdf.cell(31, 10, str(value['sku']), 1, align='C')
                pdf.cell(31, 10, str(value['tipo_producto']), 1, align='C')
                pdf.cell(31, 10, str(value['costo']), 1, align='C')
                pdf.cell(31, 10, str(value['cantidad_pack']), 1, align='C')
                total = value['cantidad_pack'] * value['costo']
                pdf.cell(31, 10, str(f"${round(total,2):,}"), 1, align='C')
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
            print('deletedProducts')
            print(st.session_state['deletedProducts'])
            if 'deletedProducts' in st.session_state and len(st.session_state['deletedProducts']) > 0:
                deleteProducts(st.session_state['deletedProducts'], st.session_state['ordenCompraId'])
            updateOrdenCompra(st.session_state['ordenCompraId'], orderDict, st.session_state['dictProductos'][st.session_state['currentSeller']])
            st.session_state['isSaved'] = True
            st.rerun()
            
    elif 'isSaved' not in st.session_state:
        if st.button('Terminar Orden de Compra'):
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
        
# Vista de creación de producto
def UITAddProduct(producto):
    print(producto)
    if (producto is not None):
        nombreVal = producto['nombre']
        skuVal = producto['sku']
        tipo_product_indexVal = producto['tipo_product_index']
        costoVal = float(producto['costo'])
        img_url = producto['img_url']
        units_per_packVal =int(producto['units_per_pack'])
        strBtn = 'Confirmar Edición'
        product_id = None
        if 'product_id' in producto:
            product_id = producto['product_id']
    else:
        nombreVal = ''
        skuVal = ''
        tipo_product_indexVal = 0
        costoVal = 0
        units_per_packVal = 0
        strBtn = 'Confirmar Creación'
        
    st.title('Producto Nuevo')
    nombre = st.text_input('Nombre del producto', value=nombreVal)
    sku = st.text_input('Codigo Producto Seller', value=skuVal)
    tipo_producto_list = ['Unidad', 'Paquete']
    tipo_producto = st.selectbox('Tipo de producto', tipo_producto_list, index=tipo_product_indexVal)
    tipo_product_index = tipo_producto_list.index(tipo_producto)
    if tipo_producto == 'Paquete':
        units_per_pack = st.number_input('Unidades por paquete', value=units_per_packVal)
    else:
        units_per_pack = 0
    costo = st.number_input('Costo [Paquete/Unidad]', value=costoVal)
    if producto is not None and img_url != '':
        st.image(img_url)
    input_file = st.file_uploader("Agrega la imagen del producto", accept_multiple_files=False)
    if st.button(strBtn):
        if nombre != '' and sku != '' and costo != 0:
            productoDict = {
                'nombre': nombre,
                'sku': sku,
                'tipo_producto': tipo_producto,
                'tipo_product_index': tipo_product_index,
                'costo': costo,
                'units_per_pack': units_per_pack
            }
            if producto is not None:
                if input_file is not None:
                    res = insertImage(input_file, st.session_state['currentSellerId'], 'rintin-internal-apps')
                    if res:
                        productoDict['img_url'] = res
                else:
                    productoDict['img_url'] = img_url
                if product_id is not None:
                    productoDict['product_id'] = product_id
                modificarProducto(productoDict)
            else:
                if input_file is not None:
                    res = insertImage(input_file, st.session_state['currentSellerId'], 'rintin-internal-apps')
                    if res:
                        productoDict['img_url'] = res
                else:
                    productoDict['img_url'] = ''
                agregarProducto(productoDict)
        else:
            st.error('Debes llenar todos los campos correctamente')

def UITOrdenesCompraEdit(data):
    if st.button('Volver'):
        st.session_state.current_view = 'ordenesCompraMenu'
        st.rerun()
    st.title('Ordenes de compra')
    st.write('---')
    for i in range(len(data['id_orden_compra'])):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('**Numero orden**')
            st.text(str(data['id_orden_compra'][i]))
            st.markdown('**Seller**')
            st.text(str(data['seller_name'][i]))
            
        with col2:
            st.markdown('**Fecha creación**')
            st.text(str(data['fecha_creacion'][i]))
            st.markdown('**Estado**')
            st.text(str(data['estado'][i]))
        with col3:
            st.markdown('**Total**')
            st.text(str(f"${data['total_cost'][i]:,}"))
            st.text(' ')
            st.text(' ')
            if st.button('Editar', key=data['id_orden_compra'][i]):
                st.session_state['ordenCompraId'] = data['id_orden_compra'][i]
                st.session_state['fechaCreacionOrden'] = data['fecha_creacion'][i]
                st.session_state['isEditing'] = True
                st.session_state.current_view = 'ordenesCompra'
                st.session_state['currentSeller'] = data['seller_name'][i]
                st.rerun()
            if st.button('Eliminar', key=str(data['id_orden_compra'][i]) + '_eliminar'):
                updateOrdenCompraStatus('trash', data['id_orden_compra'][i])
                st.rerun()
        st.write('---')

def UITOrdenesCompraMenu():
    
    st.title('Ordenes de compra')
    if st.button('Creación ordenes de compra'):
        st.session_state.current_view = 'ordenesCompra'
        st.rerun()
    if st.button('Edición ordenes de compra'):
        st.session_state.current_view = 'editOrdenesCompra'
        st.rerun()

def UITOrdenesCompra(data, products):
    # Título de la página
    titleStr = 'Orden Compra'
    disabled = False
    print('products')
    print(products)
    if 'isEditing' in st.session_state:
        disabled = True
    if 'isEditing' in st.session_state and 'initialFetch' not in st.session_state:
        st.session_state['oi_changes'] = True
        st.session_state['deletedProducts'] = []
        titleStr = 'Edicion Orden Compra'
        
        
    if products is not None and 'initialFetch' not in st.session_state and 'isSaved' not in st.session_state:
        if 'dictProductos' not in st.session_state:
            st.session_state['dictProductos'] = {}
            st.session_state['dictProductos'][st.session_state['currentSeller']] = []
        tempArr = st.session_state['dictProductos'][st.session_state['currentSeller']]
        tipo_producto_list = ['Unidad', 'Paquete']
        for i in range(len(products['nombre_producto'])):
            tipo_product_index = tipo_producto_list.index(products['tipo_producto'][i])
            tempDict = {
                'product_id': products['product_id'][i],
                'nombre': products['nombre_producto'][i],
                'sku': products['sku_producto_wp'][i],
                'tipo_producto': products['tipo_producto'][i],
                'tipo_product_index': tipo_product_index,
                'cantidad_pack': products['line_paquetes'][i],
                'units_per_pack': products['units_per_pack'][i],
                'costo': products['cost_of_goods'][i],
                'img_url': products['foto'][i]
            }
            tempArr.append(tempDict)
        st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr
        print(st.session_state['dictProductos'][st.session_state['currentSeller']])
        st.session_state['initialFetch'] = True;
    if st.button('Volver'):
        st.session_state.current_view = 'ordenesCompraMenu'
        st.rerun()
    st.title(titleStr)
    

    if 'currentSeller' not in st.session_state:
        index = None
    else:
        index = data['dokan_store_name'].index(st.session_state['currentSeller'])
    # Selector para el vendedor
    
    seller = st.selectbox('Seller', data['dokan_store_name'], index=index, disabled=disabled)
    if seller is not None:
        index = data['dokan_store_name'].index(seller)
        st.session_state['currentSellerId'] = data['user_id'][index]
        st.session_state['currentSeller'] = seller

    # Sección de detalle de orden
    st.subheader('Productos de la orden')
    index = 0
    with st.container():
        if 'dictProductos' in st.session_state and 'currentSeller' in st.session_state and st.session_state['currentSeller'] in st.session_state['dictProductos']:
            st.write("---")
            for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if 'img_url' in value and value['img_url'] != '':
                        st.image(value['img_url'])
                    else:    
                        st.write("Sin imagen")
                with col2:
                    st.markdown('**SKU:** ' + value['sku'])
                    st.markdown('**Costo:** ' + str(f"${value['costo']:,}"))
                    st.markdown('**Tipo de producto:** ' + str(value['tipo_producto']))
                    
                with col3:
                    qty_val = 1
                    if 'cantidad_pack' in value:
                        qty_val = value['cantidad_pack']
                    qty = st.number_input('Cantidad', key=value['sku'] + 'input', value=qty_val)
                    total = qty * value['costo']
                    st.markdown('**Total:** ' + str(f"${total:,}"))
                    if st.button('Editar Producto', key=value['sku']):
                        if 'dictProductos' in st.session_state and 'currentSeller' in st.session_state and st.session_state['currentSeller'] in st.session_state['dictProductos']:
                            tempArr = []
                            for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
                                tempDict = value
                                tempDict['cantidad_pack'] = st.session_state[value['sku'] + 'input']
                                tempArr.append(tempDict)
                            st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr
                        editarProducto(index, st.session_state['currentSeller'])
                    if st.button('Eliminar Producto', key=value['sku'] + 'eliminar'):
                        if 'dictProductos' in st.session_state and 'currentSeller' in st.session_state and st.session_state['currentSeller'] in st.session_state['dictProductos']:
                            tempArr = []
                            for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
                                tempDict = value
                                tempDict['cantidad_pack'] = st.session_state[value['sku'] + 'input']
                                tempArr.append(tempDict)
                            st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr
                        if 'isEditing' in st.session_state:
                            tempArrDeleted = st.session_state['deletedProducts']
                            tempArrDeleted.append(value['product_id'])
                            print(tempArrDeleted)
                            st.session_state['deletedProducts'] = tempArrDeleted
                        tempArr = st.session_state['dictProductos'][st.session_state['currentSeller']]
                        del tempArr[index]
                        st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr;
                        st.rerun()
                st.write("---")
                index = index + 1
                
    if 'currentSeller' in st.session_state:
        if st.button('Agregar Producto'):
            if 'dictProductos' in st.session_state and 'currentSeller' in st.session_state and st.session_state['currentSeller'] in st.session_state['dictProductos']:
                tempArr = []
                for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
                    tempDict = value
                    tempDict['cantidad_pack'] = st.session_state[value['sku'] + 'input']
                    tempArr.append(tempDict)
                st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr
            verDetalle(seller)
            
    if 'dictProductos' in st.session_state and 'currentSeller' in st.session_state and st.session_state['currentSeller'] in st.session_state['dictProductos']:
        if st.button('Terminar Orden de Compra'):
            tempArr = []
            for value in st.session_state['dictProductos'][st.session_state['currentSeller']]:
                tempDict = value
                tempDict['cantidad_pack'] = st.session_state[value['sku'] + 'input']
                tempArr.append(tempDict)
            st.session_state['dictProductos'][st.session_state['currentSeller']] = tempArr
            terminarOrden()

                
            
