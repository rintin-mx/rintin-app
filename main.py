import streamlit as st
from streamlit_option_menu import option_menu
import extra_streamlit_components as stx
from db.db_UserInteractionEvents import event_instert
from db.db_userApp import get_user_permissions_by_email
import numpy as np

st.set_page_config(
        page_title="Rintin",
)
import ingresoPickup,login,picking_pickups,picking,confirmacion, numerosGuia, empaquetado, recoleccion, ingresoOrdenesCompra , auditoria,logout, cookiesMenu, register,test, register,agrupacion, ordenesCompra

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager(key="cookie_manager_main")

cookie_manager = get_manager()

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        # app = st.sidebar(
        with st.sidebar:        
            #,'Facturas'
            menu=[]
            pagina=0
            cookies = cookie_manager.get_all(key="cookie_manager_login:get_all") 
            val=cookie_manager.get(cookie="username")
            valEmail=cookie_manager.get(cookie="useremail")
            lista_permisos = []
            permisos={}
            if valEmail is not None:
                permisos=get_user_permissions_by_email(valEmail)
                lista_permisos = [dic['nombre_permiso'] for dic in permisos]

            print(permisos)
            print('************')
            print(lista_permisos)
            print('************')
            st.session_state.username=val
            st.session_state.useremail=valEmail
            st.session_state.pagina=1
            # if val in ('Usuario Pickeo','Usuario_Pickeo2' ,'Usuario_Pickeo3','Usuario_Pickeo4'): 
            #     menu=['Logout','Pickeo', 'Ingreso OC Bodega']
            #     pagina=1
            if len(lista_permisos)==0:
                if val == 'picker_oaxaca':
                    menu=['Logout','Pickeo', 'Picking Pickups']
                    pagina=st.session_state.pagina=1
                # elif val == 'Usuario Recoleccion':
                #     menu=['Logout','Recoleccion']
                #     pagina=1
                elif val == 'aurea':
                    menu=['Logout','Confirmación Seller']
                elif val in ('operaciones','santiago','ivan','leslie','joshua','jesus','morris','emilio','lucero','daniel','oscar','jonathan','ismael','ayjpickeo'):
                    menu=['Logout','Confirmación Seller','Pickeo','Recoleccion','Auditoria' ,'Agrupacion', 'Empaquetado','Números de Guía','Ordenes de Compra', 'Ingreso OC Bodega']
                    pagina=st.session_state.pagina=1
                elif val == ' ivan':
                    menu=['Logout','Pickeo','Ordenes de Compra', 'Picking Pickups']
                # elif val == 'ismael':
                #     menu=['Logout','Auditoria','Agrupacion']
                elif val in ('francisco', 'JuanMa'):
                    menu=['Logout','Register','Pickeo','Ingreso Pickups','Confirmación Seller','Picking Pickups','Recoleccion','Auditoria', 'Agrupacion', 'Empaquetado','Números de Guía','Ordenes de Compra', 'Ingreso OC Bodega','Cookies','Test']

            else:
                #persona con permisos consedidos por el administrador
                #y le modulo de permisos
                menu=lista_permisos
                st.session_state.pagina=1
            app = option_menu(
                menu_title='Operaciones',
                options=menu,
                icons=['sign-out-alt','person-circle','bi-archive-fill','bi-hand-index-thumb'],
                menu_icon='chat-text-fill',
                default_index=pagina,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
                    "icon": {"color": "white", "font-size": "23px"}, 
                    "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},}
                )
        if app == "Login":
            login.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción login',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Pickeo":
            picking.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción picking',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == 'Picking Pickups':
            picking_pickups.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción picking pickups',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == 'Ingreso Pickups':
            ingresoPickup.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción picking pickups',valEmail
                event_instert(EventName,EventAction,EventUser)

        if app == 'Empaquetado':
            empaquetado.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción empaquetado',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == 'Números de Guía':
            numerosGuia.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción numeros de guia',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == 'Confirmación Seller':
            confirmacion.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción confirmacion',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Recoleccion":
            recoleccion.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción recoleccion',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Logout":
            logout.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción logout',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Auditoria":
            auditoria.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción ingresoPickeoReco',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Cookies":
            cookiesMenu.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción cookies',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Register":
            register.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción register',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Agrupacion":
            agrupacion.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción agrupacion',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == "Ordenes de Compra":
            ordenesCompra.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción Ordenes de Compra',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app == 'Ingreso OC Bodega':
            ingresoOrdenesCompra.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción Ingreso Ordenes de Compra Bodega',valEmail
                event_instert(EventName,EventAction,EventUser)
        if app=='Test':
            test.app()

    run() 