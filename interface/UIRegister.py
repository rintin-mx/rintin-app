import sys
sys.path.append('..')
import streamlit as st

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import auth
import extra_streamlit_components as stx
from db.db_userApp import insert_user


if not firebase_admin._apps:
    cred = credentials.Certificate('rintin-16fee-firebase-adminsdk-zcrog-536fdf1dfb.json') 
    default_app = firebase_admin.initialize_app(cred)

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager(key="cookie_manager_register")
cookie_manager = get_manager()

def UIRegister():
    email = st.text_input('Email Address')
    password = st.text_input('Password',type='password', key='passwordRegistro')
    username = st.text_input("Ingresa tu nombre de usuario")
    if st.button('Create my account'):
        user = auth.create_user(email = email, password = password,uid=username)
        insert_user('prod',email,password)  
        st.success('Account created successfully!')
        st.markdown('Please Login using your email and password')
        st.balloons()
    else:
        st.text('Usted no tiene permiso para acceder a esta cuenta')
