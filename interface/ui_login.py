import sys
sys.path.append('..')
import streamlit as st

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import auth
import extra_streamlit_components as stx
from db.db_user_app import validate_user
from db.db_user_interaction_events import event_instert

if not firebase_admin._apps:
    cred = credentials.Certificate('rintin-16fee-firebase-adminsdk-zcrog-536fdf1dfb.json') 
    default_app = firebase_admin.initialize_app(cred)

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager(key="cookie_manager_login")
cookie_manager = get_manager()

def initialise_st_state_vars():
    if "auth_code" not in st.session_state:
        st.session_state["auth_code"] = ""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_cognito_groups" not in st.session_state:
        st.session_state["user_cognito_groups"] = []
    if 'useremail' not in st.session_state:
        st.session_state["useremail"] = ''
    if 'username' not in st.session_state:
        st.session_state["username"] = ''

def login(email,password):
    user = auth.get_user_by_email(email)
    if user is not None:
        validated=validate_user('prod',email,password)
        if validated==False:
            st.warning('Login error, validate your credentials')
            return False
        else:
            EventName,EventAction,EventUser='Login','Autenticación en firebase',email
            event_instert(EventName,EventAction,EventUser)
            cookie_manager.set("username", user.uid,key="username")
            cookie_manager.set("useremail", user.email,key="useremail")
            cookie_manager.set("authenticated", validated,key="authenticated")
            return True


def set_st_state_vars(useremail,password):
    initialise_st_state_vars()
    isLogin=login(useremail,password)
    if isLogin==True:
        username=cookie_manager.get(cookie="username")
        return username
    else:    
        return None

def UILogin():
    authenticated=cookie_manager.get(cookie="authenticated")    
    if authenticated==False or authenticated is None or authenticated==True:
        try:
            #choice = st.selectbox('Login/Signup',['Login','Sign up'],key="Login/Signup")
            email = st.text_input('Email Address',key="emailAdress")
            password = st.text_input('Password',type='password')
            if st.button('Login'):
                isOk=set_st_state_vars(email,password)
                if isOk:
                    useremail=cookie_manager.get(cookie="useremail")
                    authenticated=cookie_manager.get(cookie="authenticated")
                    if useremail is not None:
                        EventName,EventAction,EventUser='Login','Autenticación en firebase',useremail
                        event_instert(EventName,EventAction,EventUser)
                    #st.session_state.useremail=useremail
                    #st.session_state.authenticated=authenticated
                else:
                    st.warning('Login error, validate your credentials UILogin')
        except Exception as e:
            st.warning('Login error, validate your credentials UILogin Except')
            st.warning(f'Login error: {str(e)}')
            st.warning(traceback.format_exc())

            
def UILogput():
    cookies = cookie_manager.get_all(key="cookie_manager_login_logout")
    val=cookie_manager.get(cookie="username")
    valEmail=cookie_manager.get(cookie="useremail")
    if valEmail is not None:
        EventName,EventAction,EventUser='Login','Autenticación en firebase',valEmail
        event_instert(EventName,EventAction,EventUser)
    if val is not None:
        st.text('Bienvenido '+val)
    if st.button('Cerrar sesión'):
        if val is not None:
            st.text('Email id: '+val)
    
        event_name = "Loginout"
        event_action = "Click"
        cookie_manager.delete("useremail",key="useremail")
        cookie_manager.delete("username",key="username")
        cookie_manager.delete("authenticated",key="authenticated")
