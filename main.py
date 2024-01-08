import streamlit as st
from streamlit_option_menu import option_menu
import extra_streamlit_components as stx
from db.db_UserInteractionEvents import event_instert

st.set_page_config(
        page_title="Rintin",
)
import login,picking, recoleccion, auditoria,logout, cookiesMenu, register,test, register,agrupacion

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
            st.session_state.username=val
            st.session_state.useremail=valEmail
            if val in ('Usuario Pickeo','Usuario_Pickeo2' ,'Usuario_Pickeo3','Usuario_Pickeo4'): 
                menu=['Logout','Pickeo']
                pagina=1
            elif val == 'Usuario Recoleccion':
                menu=['Logout','Recoleccion']
                pagina=1
            elif val== 'operaciones':
                menu=['Logout','Pickeo','Recoleccion','Auditoria']
                pagina=1
            elif val == 'francisco':
                menu=['Logout','Register','Pickeo','Recoleccion','Auditoria', 'Agrupacion','Cookies']
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
        print('app')
        print(app)

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
    run() 