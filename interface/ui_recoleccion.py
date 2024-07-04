# db/script_db.py
import sys
sys.path.append('..') 
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from db.db_order import insert_order_metadata
from db.db_user_interaction_events import event_instert
from db.db_recoleccion import get_substitute_prod
import streamlit_shadcn_ui as ui
import asyncio


def UIpendienteRecoleccion(total_pedidos, total_paquetes , total_registros, data):

    # Título de la sección
    st.header("Pendiente recoleccion")
    ts,tp,tpa=0,0,0
    df = pd.DataFrame(data)

    cols = st.columns(3)
    with cols[0]:
        ui.metric_card(title="Total Sellers", content=total_registros,  key="card1")
    with cols[1]:
        ui.metric_card(title="Total Pedidos", content=total_pedidos ,  key="card2")
    with cols[2]:
        ui.metric_card(title="Total Paquetes", content=total_paquetes ,  key="card3")

    # Espacio entre secciones
    st.write("---")

    # Título de la tabla
    st.subheader("Sellers a recolectar")

    #edited_df = st.data_editor(df,disabled=("Seller", "#Pedidos", "#Paquetes"))
    st.dataframe(df, width=1000)

    #st.table(df)

    left_col, right_col = st.columns([0.3, 0.1])  # Ajusta la proporción según sea necesario
    with right_col:
        if st.button("Iniciar recolección"):
            EventName,EventAction,EventUser='picking','Se pulso en botón Iniciar recolección',st.session_state.useremail
            event_instert(EventName,EventAction,EventUser)
            st.session_state.current_view = 'recoleccion'
            st.rerun()

            
def UIpendienteRecoleccionSeleccion(total_pedidos, total_paquetes , total_registros, data):
    #if 'mostrar_expander' not in st.session_state:
    #st.session_state['mostrar_expander'] = False
    #if st.button("Volver a inicio"):
    #        st.session_state.current_view = 'pick'
    #        st.rerun()
    st.header("Proceso de recolección y selección")


    cols = st.columns(3)
    with cols[0]:
        ui.metric_card(title="Total Sellers", content=total_registros,  key="card1")
    with cols[1]:
        ui.metric_card(title="Total Pedidos", content=total_pedidos ,  key="card2")
    with cols[2]:
        ui.metric_card(title="Total Paquetes", content=total_paquetes ,  key="card3")

    # Título de la tabla
    st.subheader("Sellers a recolectar")
    st.write("---")
    df = pd.DataFrame(data)
    header_col1, header_col2, header_col3,header_col4,header_col5= st.columns([2, 1, 1, 1, 1])
    header_col1.write("**Seller**")
    header_col2.write("**Pedidos**")
    header_col3.write("**Paquetes**") 
    header_col4.write("**Reemplazos**")
    header_col5.write("")
    for index, vendedor in df.iterrows():
        txt = str(vendedor["paquetes"]).split(".")
        print(vendedor)
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        with col1:
            st.write(str(vendedor["seller"]))
        with col2:
            st.write(vendedor["pedidos"])
        with col3:
            st.write(int(txt[0]))
        with col4:
            st.write(vendedor["reemplazos"])
        with col5:
            #recolectar_button = st.button("Recolectar", key=vendedor["nombre"])
            if st.button("Recolectar", key=f"recolectar_{index}"):
                EventName,EventAction,EventUser='picking','Se pulso en botón Recolectar',st.session_state.useremail
                event_instert(EventName,EventAction,EventUser)
                st.session_state.Seller_name = vendedor["seller"]
                print("st.session_state.Seller_name")
                print(st.session_state.Seller_name)
                
                st.session_state.current_view = 'pendiente'
                st.rerun()
        st.write("---")
                
    
    # Botón para finalizar la recolección
    if st.button("Terminar Recoleccion"):
        EventName,EventAction,EventUser='picking','Se pulso en botón Terminar Recoleccion',st.session_state.useremail
        event_instert(EventName,EventAction,EventUser)
        st.success("Recolección finalizada.")
        st.session_state.current_view = 'recolect'
        st.rerun()

def UIrecoleccionFinal(childList, childListString):
    if len(childList) == 1:
        st.markdown(f'## Se actualizó el pedido #{childListString} al estado "Auditoria"')
    elif len(childList) > 1:
        st.markdown(f'## Se actualizaron los pedidos con número {childListString} al estado "Auditoria"')
    st.write('---')
    if st.button('Regresar'):
        st.session_state['current_view'] = 'recolect'
        st.rerun()

def UIagrerPedidoSellerSeleccion(data):
    j=0
    st.title(f'Seller: {st.session_state.Seller_name}')
    st.header('Pedidos a recolectar')
    # Inicializar la sesión con los datos de ejemplo si aún no se ha hecho
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = data
    if 'flag' not in st.session_state:
        st.session_state.flag = False


    # Función para agregar un nuevo pedido
    def agregar_pedido():
        st.session_state.pedidos.append({'seller_name': '','num_pedidos': '', 'num_paquetes': '', 'recolectado': False})

    df = pd.DataFrame(data)
    st.write("---")

    # Verificar si hay productos cambiados
    order_list = ''
    for order in df.iterrows():
        print(order[1][5])
        if int(order[1][5]) > 0:    
            order_list += f"{order[1][4]},"

    if order_list != '':
        substitute_products = get_substitute_prod(order_list[:-1])

    # Solo necesitas una columna
    col1 = st.columns(1)[0]
    col1.write('Información de orden')
    recoTotal=[]
    recoString = ''
    noReco=[]
    # Iterar a través del DataFrame para crear la interfaz
    for index, row in df.iterrows():
        txt=str(row.num_paquetes).split(".")
        
        with col1:
            st.markdown(f'<div class="flex-container"><div class="nombre-producto">order_id: {row.order_id}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="flex-container"><div class="sku-producto">Seller: {row.seller_name}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="flex-container"><div class="sku-producto">Numero de Paquetes:{txt[0]}</div></div>', unsafe_allow_html=True)

            if order_list != '':
                # Búsqueda de la orden en la lista de cambiados
                i = 0
                while i < len(substitute_products['order_id']) - 1 and substitute_products['order_id'][i] != row.order_id:
                    i += 1
                
                # Al ser encontrado, despliega la información del cambio
                if substitute_products['order_id'][i] == row.order_id:
                    sku = substitute_products['nuevo_producto_sku'][i]
                    sku_anterior = substitute_products['sku'][i]
                    st.warning(f'Este pedido tuvo cambios: {sku_anterior} por {sku}.')

            recolectado = st.toggle('',key=f'recolectado{index}')
            if recolectado:
                st.session_state.recolectado=False
                recoTotal.append({'order_id':row.order_id,"seller_name":row.seller_name, "num_pedidos":row.num_pedidos, "num_paquetes":row.num_paquetes,"recolectado":recolectado})
                recoString = recoString + str(row.order_id) + ', '
            else:
                st.session_state.recolectado=True
            
            if st.session_state.recolectado==True:
                choice = ui.select(options=["No motivo","Seller no tenía el pedido listo", "Seller creía que no estaba pagado", "Capacidad de nuestro recolector","Seller dice ya haberlo entregado","Seller dice que no existe el pedido"], key=f'choice1'+str(index))
                noReco.append({'order_id':row.order_id,"seller_name":row.seller_name, "num_pedidos":row.num_pedidos, "num_paquetes":row.num_paquetes,"noReco":choice})

    #recoTotal= [{'order_id': 281958, 'seller_name': 'Fanny Love', 'num_pedidos': 1, 'num_paquetes': 1.0, 'recolectado': True},[{'order_id': 281958, 'seller_name': 'Fanny Love', 'num_pedidos': 1, 'num_paquetes': 1.0, 'recolectado': True}]]
    if st.button('Continuar', key=f"Continuar_50"):
        EventName,EventAction,EventUser='picking','Se pulso en botón Continuar',st.session_state.useremail
        event_instert(EventName,EventAction,EventUser)
        if len(recoTotal)>0:
            recoString = recoString[:-2]
            with st.spinner(f'Actualizando estatus del pedido Auditoria'):
                order_status='rec_ped_aud'
                for i,pedido in enumerate(recoTotal):
                        #idPedido
                        #para test '281660'
                    r=asyncio.run(endpoint_update_status_by_order_id(pedido['order_id'], order_status))
                    EventName,EventAction,EventUser='picking','Se ejecuto endpoint_update_status_by_order_id',st.session_state.useremail
                    event_instert(EventName,EventAction,EventUser)
            st.session_state['orderList'] = recoTotal
            st.session_state['orderStr'] = recoString
            st.session_state.current_view = 'recoleccionFinal'
            st.rerun()
        if len(noReco)>0:
            with st.spinner(f'Actualizando estatus del pedido Auditoria no recolectados'):
                for i,pedido in enumerate(noReco):
                    if pedido['noReco']!="No motivo":
                        
                        meta_key='_no_motivo_recoleccion'
                        insert_order_metadata(pedido['order_id'],meta_key,pedido['noReco'])
                        EventName,EventAction,EventUser='picking','Se ejecuto insert_order_metadata',st.session_state.useremail
                        event_instert(EventName,EventAction,EventUser)
                        st.session_state.flag = True
                    else:
                        st.session_state.flag = False
                        st.warning('Error  de inserción, no se pudo insertar la metadada')



        if st.session_state.flag == True:
            st.session_state.current_view = 'recoleccion'
            st.rerun()
          