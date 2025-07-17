
import streamlit as st
import pandas as pd
from db.db_user_app import get_user_permissions,get_all_user
from db.db_roles import obtener_todos_los_roles
from db.db_usuario_roles import insertar_usuario_rol

def users():
    # Inicialización de la interfaz de Streamlit
    st.title('Consulta de Permisos de Usuario')
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 0
    if 'rol_id' not in st.session_state:
        st.session_state.rol_id = 0
    if 'visible' not in st.session_state:
        st.session_state.visible = False
    
    # Obtener usuarios
    users = get_all_user() 
    # Si hay usuarios, mostrarlos en un ListBox
    if users:
        user_emails = [str(user['id']) +'-'+ user['email'] for user in users]
        selected_user = st.selectbox("Seleccione un usuario", user_emails)
        user_id=int(selected_user.split('-')[0])
        st.session_state.user_id = int(user_id)
        st.write("Has seleccionado:", selected_user.split('-')[1])
        lista_roles = obtener_todos_los_roles()
        if lista_roles:
            df_roles = pd.DataFrame(lista_roles, columns=['id', 'nombre_rol', 'descripcion','updated_at'])
            df_roles['opsCompuesta'] = df_roles['id'].astype(str) + '-' + df_roles['nombre_rol']
            # Selección de permiso para editar o eliminar
            selected_role_id = st.selectbox("Seleccione un rol para editar o eliminar", df_roles['opsCompuesta'])
            id_fk_rol_clean=int(selected_role_id.split('-')[0])
            st.session_state.rol_id = int(id_fk_rol_clean)
            st.session_state.visible=True
    if st.button('Mostrar Permisos'):
            # Obtiene los permisos del usuario
            user_permissions = get_user_permissions(user_id)
            if  len(user_permissions)>0:
                # Mostrar los permisos en un dataframe
                st.dataframe(user_permissions)
 

    if st.button('Asignar permisos', key="button_asignar_permisos"):
            insertar_usuario_rol(st.session_state.user_id,st.session_state.rol_id)
            st.success('Se asigno correctamente un rol a este usuario!')
            st.balloons()
            st.session_state.user_id=0
            st.session_state.rol_id=0
            st.session_state.visible=False
            st.rerun()

                    


