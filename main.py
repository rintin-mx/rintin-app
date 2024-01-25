import streamlit as st
from streamlit_option_menu import option_menu
import extra_streamlit_components as stx
from db.db_UserInteractionEvents import event_instert

st.set_page_config(
        page_title="Rintin",
)
import login,picking,confirmacion, empaquetado, recoleccion, ingresoOrdenesCompra , auditoria,logout, cookiesMenu, register,test, register,agrupacion, ordenesCompra

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
            print('*****')
            print(val)
            print('*****')
            valEmail=cookie_manager.get(cookie="useremail")
            st.session_state.username=val
            st.session_state.useremail=valEmail
            # if val in ('Usuario Pickeo','Usuario_Pickeo2' ,'Usuario_Pickeo3','Usuario_Pickeo4'): 
            #     menu=['Logout','Pickeo', 'Ingreso OC Bodega']
            #     pagina=1
            if val == 'picker_oaxaca':
                menu=['Logout','Pickeo']
                pagina=1
            # elif val == 'Usuario Recoleccion':
            #     menu=['Logout','Recoleccion']
            #     pagina=1
            elif val in ('operaciones','santiago','ivan','leslie','joshua','jesus','morris','emilio','lucero','daniel','oscar','jonathan','ismael','ayjpickeo'):
                menu=['Logout','Confirmación Seller', 'Empaquetado','Pickeo','Recoleccion','Auditoria','Agrupacion','Ordenes de Compra', 'Ingreso OC Bodega']
                pagina=1
            elif val == ' ivan':
                 menu=['Logout','Pickeo','Ordenes de Compra']
            # elif val == 'ismael':
            #     menu=['Logout','Auditoria','Agrupacion']
            elif val in ('francisco', 'JuanMa'):
                menu=['Logout','Register','Pickeo','Confirmación Seller','Recoleccion','Auditoria', 'Agrupacion', 'Empaquetado','Ordenes de Compra', 'Ingreso OC Bodega','Cookies','Test']
            else:
                menu=['Login']
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
        if app == 'Empaquetado':
            empaquetado.app()
            if valEmail is not None:
                EventName,EventAction,EventUser='Main','acceso a la opción empaquetado',valEmail
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