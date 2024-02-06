import streamlit as st
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import auth
import extra_streamlit_components as stx

if not firebase_admin._apps:
    cred = credentials.Certificate('rintin-16fee-firebase-adminsdk-zcrog-536fdf1dfb.json') 
    default_app = firebase_admin.initialize_app(cred)

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager(key='cookie_manager_authenticate')

cookie_manager = get_manager()


def initialise_st_state_vars():
    """
    Initialise Streamlit state variables.

    Returns:
        Nothing.
    """
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



def login(email):
    user = auth.get_user_by_email(email)
    cookie_manager.set("username", user.uid,key="username")
    cookie_manager.set("useremail", user.email,key="useremail")
    cookie_manager.set("authenticated", True,key="authenticated")
    st.session_state["username"] = user.uid
    

    return user.uid

def set_st_state_vars(useremail):
    initialise_st_state_vars()
    login(useremail)
    username=cookie_manager.get(cookie="username")
    return username

  
