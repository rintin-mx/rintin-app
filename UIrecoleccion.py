# db/script_db.py
import sys
sys.path.append('..') 
import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from db.db_order import insert_order_metadata
import streamlit_shadcn_ui as ui
import time


def ejecuto ():
    print("ejecuto")
def UIpendienteRecoleccion(total_pedidos, total_paquetes , total_registros, data):
    
    print("UIpendienteRecoleccion")

    
    # Título de la sección
    st.header("Pendiente recoleccion")
    ts,tp,tpa=0,0,0
    df = pd.DataFrame(data)

    cols = st.columns(3)
    with cols[0]:
        ui.metric_card(title="Total Sellers", content=total_pedidos,  key="card1")
    with cols[1]:
        ui.metric_card(title="Total Pedidos", content=total_paquetes,  key="card2")
    with cols[2]:
        ui.metric_card(title="Total Paquetes", content=total_registros,  key="card3")

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
            print("pulse boton Iniciando recolección")
            st.session_state.current_view = 'recoleccion'
            st.rerun()

            
def UIpendienteRecoleccionSeleccion(total_pedidos, total_paquetes , total_registros, data):
    print("UIpendienteRecoleccionSeleccion")
    #if 'mostrar_expander' not in st.session_state:
    #st.session_state['mostrar_expander'] = False
    #if st.button("Volver a inicio"):
    #        print("pulse boton Iniciando pick")
    #        st.session_state.current_view = 'pick'
    #        st.rerun()
    st.header("Proceso de recolección y selección")


    cols = st.columns(3)
    with cols[0]:
        ui.metric_card(title="Total Sellers", content=total_pedidos,  key="card1")
    with cols[1]:
        ui.metric_card(title="Total Pedidos", content=total_paquetes,  key="card2")
    with cols[2]:
        ui.metric_card(title="Total Paquetes", content=total_registros,  key="card3")

    # Título de la tabla
    st.subheader("Sellers a recolectar")
    st.write("---")
    df = pd.DataFrame(data)
    header_col1, header_col2, header_col3,header_col4= st.columns([2, 1, 1,1])
    header_col1.write("**Seller**")
    header_col2.write("**Pedidos**")
    header_col3.write("**Paquetes**") 
    header_col4.write("")
    for index, vendedor in df.iterrows():
        txt = str(vendedor["#Paquetes"]).split(".")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.write(str(vendedor["Seller"]))
        with col2:
            st.write(vendedor["#Pedidos"])
        with col3:
            st.write(int(txt[0]))
        with col4:
            #recolectar_button = st.button("Recolectar", key=vendedor["nombre"])
            if st.button("Recolectar", key=f"recolectar_{index}"):
                st.session_state.Seller_name = vendedor["Seller"]
                print("st.session_state.Seller_name")
                print(st.session_state.Seller_name)
                
                st.session_state.current_view = 'pendiente'
                st.rerun()
        st.write("---")
                
    
    # Botón para finalizar la recolección
    if st.button("Terminar Recoleccion"):
        st.success("Recolección finalizada.")
        st.session_state.current_view = 'recolect'
        st.rerun()


def UIagrerPedidoSellerSeleccion(data):
    print("UIagrerPedidoSellerSeleccion")
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
    # Solo necesitas una columna
    col1 = st.columns(1)[0]
    col1.write('Información de orden')
    recoTotal=[]
    noReco=[]
    # Iterar a través del DataFrame para crear la interfaz
    for index, row in df.iterrows():
        txt=str(row.num_paquetes).split(".")
        print(row)
        
        with col1:
            st.markdown(f'<div class="flex-container"><div class="nombre-producto">order_id: {row.order_id}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="flex-container"><div class="sku-producto">Seller: {row.seller_name}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="flex-container"><div class="sku-producto">Numero de Paquetes:{txt[0]}</div></div>', unsafe_allow_html=True) 
            recolectado = st.toggle('',key=f'recolectado{index}')
            print("recolectado")
            if recolectado:
                st.session_state.recolectado=False
                recoTotal.append({'order_id':row.order_id,"seller_name":row.seller_name, "num_pedidos":row.num_pedidos, "num_paquetes":row.num_paquetes,"recolectado":recolectado})
            else:
                st.session_state.recolectado=True
            
            if st.session_state.recolectado==True:
                choice = ui.select(options=["No motivo","Seller no tenía el pedido listo", "Seller creía que no estaba pagado", "Capacidad de nuestro recolector","Seller dice ya haberlo entregado"])
                noReco.append({'order_id':row.order_id,"seller_name":row.seller_name, "num_pedidos":row.num_pedidos, "num_paquetes":row.num_paquetes,"noReco":choice})

    #print("recoTotal")
    #print(recoTotal)
    #print("noReco")
    #print(noReco)
    #recoTotal= [{'order_id': 281958, 'seller_name': 'Fanny Love', 'num_pedidos': 1, 'num_paquetes': 1.0, 'recolectado': True},[{'order_id': 281958, 'seller_name': 'Fanny Love', 'num_pedidos': 1, 'num_paquetes': 1.0, 'recolectado': True}]]
    if st.button('Continuar', key=f"Continuar_50"):
        print("pulse boton Continuar")
        if len(recoTotal)>0:
             print("entre recoTotal")
             with st.spinner(f'Actualizando estatus del pedido Auditoria'):
                 order_status='rec_ped_aud'
                 for i,pedido in enumerate(recoTotal):
                    print(pedido)
                    #print(pedido['order_id'])
                        #idPedido
                        #para test '281660'
                    r=asyncio.run(endpoint_update_status_by_order_id(pedido['order_id'], order_status))
                    print(r)
                    st.session_state.flag = True
        if len(noReco)>0:
            print("entre noReco")
            with st.spinner(f'Actualizando estatus del pedido Auditoria no recolectados'):
                print("insertar nuevo estado")
                for i,pedido in enumerate(noReco):
                    if pedido['noReco']!="No motivo":
                        
                        print("pedido")
                        print(pedido['order_id'])
                        meta_key='_no_motivo_recoleccion'
                        insert_order_metadata(pedido['order_id'],meta_key,pedido['noReco'])
                        st.session_state.flag = True
                    else:
                        st.session_state.flag = False
                        st.warning('Error  de inserción, no se pudo insertar la metadada')



        if st.session_state.flag == True:
            print("entre al if st.session_state.flag")
            st.session_state.current_view = 'recoleccion'
            st.rerun()
            #recoTotal.append({'order_id':row['order_id'],"seller_name":row['seller_name'], "num_pedidos":row['num_pedidos'], "num_paquetes":row['num_paquetes'],"recolectado":recolectado})
        #with col2:
        #    st.text(row['seller_name'])
        #with col3:
        #    st.text(int(row['num_pedidos']))
        #with col4:
        #    st.text(int(row['num_paquetes']))
        #with col2:
        #    recolectado = st.toggle('',key=f'recolectado{index}')
        #    recoTotal.append({'order_id':row['order_id'],"seller_name":row['seller_name'], "num_pedidos":row['num_pedidos'], "num_paquetes":row['num_paquetes'],"recolectado":recolectado})
    
    #print(recoTotal)
    #for i in range(len(recoTotal)):
    #    if recoTotal[i]['recolectado'] ==True:
    #        recoletarVerdaderoArray.append({'order_id':recoTotal[i]['order_id'],"seller_name":recoTotal[i]['seller_name'], "num_pedidos":recoTotal[i]['num_pedidos'], "num_paquetes":recoTotal[i]['num_paquetes']})
    #    else:
    #        recoletarFalsoArray.append({'order_id':recoTotal[i]['order_id'],"seller_name":recoTotal[i]['seller_name'], "num_pedidos":recoTotal[i]['num_pedidos'], "num_paquetes":recoTotal[i]['num_paquetes']})

   
    #print("recoletarVerdaderoArray")
    ##print(len(recoletarVerdaderoArray)) 
    #print("recoletarFalsoArray")
    #print(len(recoletarFalsoArray))
    
    #st.session_state.grabe=False
    #if recolectado:
    #    trigger_btn = ui.button(text="Continuar", key="trigger_btn")
    #    if len(recoletarVerdaderoArray)>0:
    #        respuesta_auditoria=ui.alert_dialog(show=trigger_btn, title="Confirmemos el pickeo", description='Enviaremos el pedido a "Pedidos por auditar"\nConfirma si es lo que quisieras', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_auditoria")
    #        if respuesta_auditoria:
    #            with st.spinner(f'Actualizando estatus del pedido'):
    #                    order_status='rec_ped_aud'
                    #for i,pedido in enumerate(recoletarVerdaderoArray):
                        #print("pedido")
                        #print(pedido['order_id'])
    #                    st.session_state.grabe=True
                        #idPedido
                        #para test '281660'
                        #r=asyncio.run(endpoint_update_status_by_order_id('281660', order_status))
                        #print(r)
                        #time.sleep(5)
    #                    st.session_state.current_view = 'pendiente'
    #                    st.rerun()
    #if len(recoletarFalsoArray)>0:
    #    if st.session_state.grabe==True:
    #        if st.button('Continuar'):
    #                with st.expander(f"#Confirmemos Recolección del Seller: {st.session_state.Seller_name}", expanded=True):
    #                    st.write("Enviaremos el pedido a 'Auditoría'")
    #                    st.write("Confirma si es lo que quieras")

    #                    col1, col2 = st.columns(2)
    #                    with col1:
    #                        if st.button("Volver"):
    #                            print("pulse boton Volver")
    #                            #st.session_state['confirmar_envio'] = False  # Se cancela la acción
    #                            #st.rerun()  # Actualiza la página para reflejar el cambio
    #                    with col2:
    #                        if st.button("Confirmar"):
    #                            st.session_state.recoletarFalsoArray=recoletarFalsoArray

    #                            st.session_state.current_view ='secuencia'
    #                            st.rerun()
    

            

'''
    if st.button('Continuar'):
        st.session_state.recoletarVerdaderoArray=recoletarVerdaderoArray
        st.session_state.recoletarFalsoArray=recoletarFalsoArray
        st.session_state.current_view = 'secuencia'
        st.rerun()

    
    if st.button('Continuar'):
        shown_page = 'intro'
        if shown_page == "intro":
            contIntro = st.empty()
            expIntro = contIntro.expander('What App Wizard Can Do', True)
            job_name = expIntro.text("Give this Job a Name")
            col1, col2 = expIntro.columns([8,2])
            col1.write("")
            exp1_button = col2.button('To Step 1') 

            if exp1_button:
                contIntro.empty()
                shown_page = 'Step 1'

        if shown_page == 'Step 1':
            header_text = 'Step 1'
            cont1 = st.empty()
            exp1 = cont1.expander('Step 1 of 2', True)
            exp1.file_uploader('Upload Data', type=None, accept_multiple_files=False)
            col1, col2 = exp1.columns([9,2])
            col1.write("")
            #exp1_back_button = col1.button('Back to Intro')
            exp1_next_button = col2.button('To Step 2') 

            #if exp1_back_button:
            #    cont1.empty()
            #    shown_page = 'Intro'

            if exp1_next_button:
                cont1.empty()
                shown_page = 'Step 2'
        
        if shown_page == 'Step 2':
            header_text = 'Step 2'
            cont2 = st.empty()
            exp2 = cont2.expander("Step 2 of 2", True)
            job_name = exp2.text_input("Some more info")
            col1, col2 = exp2.columns([9,1])
            exp2_back_button = col1.button("Back to Step 1")
            exp2_forward_button = col2.button('To Another Setp in Future') 

            if exp2_back_button:
                print("back")

            if exp2_back_button:
                cont2.empty()
                shown_page = 'Step 2'

            if exp2_forward_button:
                cont2.empty()
        
        if len(recoletarVerdaderoArray)>0:
            with st.expander(f"#Confirmemos Recolección del Seller: {st.session_state.Seller_name}", expanded=True):
                st.write("Enviaremos el pedido a 'Auditoría'")
                st.write("Confirma si es lo que quieras")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Volver"):
                        print("pulse boton Volver")
                        #st.session_state['confirmar_envio'] = False  # Se cancela la acción
                        #st.rerun()  # Actualiza la página para reflejar el cambio
                with col2:
                    if st.button("Confirmar"):
                        st.session_state.recoletarFalsoArray=recoletarFalsoArray

                        st.session_state.current_view ='secuencia'
                        st.rerun()
                        
                        print("pulse boton Confirmar")
                        if len(recoletarFalsoArray)>0:
                            with st.expander(f"#Confirmemos razón de NO recolección del Seller: {st.session_state.Seller_name}", expanded=True):                  
                                for i,pedido in enumerate(recoletarFalsoArray):
                                    print("pedido")
                                    print(pedido)

                                    col1,col2 = st.columns([3,1])
                                    with col1:
                                        st.text(pedido['seller_name'])
                                        st.text(pedido['num_pedidos'])
                                        st.subheader('Razón de NO recolección')
                                        razon_no_recoleccion = st.text_area('Escriba tu comentario', key='razon_no_recoleccion')
                                if st.button('Aceptar'):
                                    st.success('Se ha registrado la información y se continúa con el proceso.')
                                    st.session_state.current_view = 'recolect'
                                    st.rerun()

                                if st.button("Regresar"):
                                    st.session_state['confirmar_envio'] = False  # Se cancela la acción
                                    st.rerun()  # Actualiza la página para reflejar el cambio
                            #st.session_state.pedidos = []
                            #st.success("Recolección finalizada.")
                            #st.session_state.current_view = 'recolect'
                            #st.rerun()
                        '''
'''
        else:
            with st.expander(f"#Confirmemos razón de NO recolección del Seller: {st.session_state.Seller_name}", expanded=True):                  
                for i,pedido in enumerate(recoletarFalsoArray):
                    print("pedido")
                    print(pedido)

                    col1,col2 = st.columns([3,1])
                    with col1:
                        st.text(pedido['seller_name'])
                        st.text(pedido['num_pedidos'])
                        st.subheader('Razón de NO recolección')
                        razon_no_recoleccion = st.text_area('Escriba tu comentario', key='razon_no_recoleccion')
                if st.button('Aceptar'):
                    st.success('Se ha registrado la información y se continúa con el proceso.')
                    st.session_state.current_view = 'recolect'
                    st.rerun()

                if st.button("Regresar"):
                    st.session_state['confirmar_envio'] = False  # Se cancela la acción
                    st.rerun()  # Actualiza la página para reflejar el cambio
'''

