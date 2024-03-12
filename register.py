import streamlit as st
from interface.ui_register import UIRegister
from interface.ui_roles import roles
from interface.ui_opciones_sistema import opcionSistema
from interface.ui_permisos import permisos
from interface.ui_roles_permisos import rolespermisos
from interface.ui_usuario import users
from db.db_roles import obtener_todos_los_roles

def app():

    tab1, tab2, tab3,tab4,tab5,tab6 = st.tabs(["Todos los usuarios","Registro de usuario", "Roles",  "Permisos","Opciones del Sistema","Roles y Permisos"])
    with tab1:
        users()
    with tab2:
        st.header("Registro de usuario")
        UIRegister()
    with tab3:
        roles()

    with tab4:
        opcionSistema()
    with tab5:
        permisos()
    with tab6:
        rolespermisos()
       