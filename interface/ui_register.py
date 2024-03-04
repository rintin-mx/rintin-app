import sys
sys.path.append('..')
import streamlit as st

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import auth
import extra_streamlit_components as stx
import pandas as pd
from db.db_user_app import insert_user
from db.db_pemrisos import obtener_todos_los_permisos
from db.db_roles import obtener_todos_los_roles
from db.db_usuario_roles import insertar_usuario_rol


if not firebase_admin._apps:
    cred = credentials.Certificate('rintin-16fee-firebase-adminsdk-zcrog-536fdf1dfb.json') 
    default_app = firebase_admin.initialize_app(cred)

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager(key="cookie_manager_login_register")
cookie_manager = get_manager()


def UIRegister():
    if 'tabla' not in st.session_state:
        st.session_state.tabla = pd.DataFrame(columns=['Rol', 'Permiso'])
    email = st.text_input('Email Address')
    password = st.text_input('Password',type='password', key='passwordRegistro')
    username = st.text_input("Ingresa tu nombre de usuario")
    lista_roles = obtener_todos_los_roles()
    df_rol = pd.DataFrame(lista_roles, columns=['rol_id','nombre_rol', 'descripcion'])
    df_rol['opsCompuesta'] = df_rol['rol_id'].astype(str) + '-' + df_rol['nombre_rol']
    rol_id_fk=st.selectbox("Seleccione una opción del rol", df_rol['opsCompuesta'], key='rol_id_fk')

    if st.button('Crear cuenta'):
        
        user = auth.create_user(email = email, password = password,uid=username)
        user_id=insert_user('prod',email,password) 
        print(user_id)
        rol_id_fk_clean=int(rol_id_fk.split('-')[0])
        print(rol_id_fk_clean) 
        insertar_usuario_rol(user_id,int(rol_id_fk_clean))
        st.success('Account created successfully!')
        st.markdown('Please Login using your email and password')
        st.balloons()
    else:
        st.text('Usted no tiene permiso para acceder a esta cuenta')
