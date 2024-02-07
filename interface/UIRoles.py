import streamlit as st
import pandas as pd
from db.db_roles import obtener_todos_los_roles, actualizar_rol, eliminar_rol, insert_rol    

def roles():
    st.title("Gestión de Roles")

    # Usar una variable de sesión para el estado del checkbox
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Inserción de un nuevo rol
    with st.expander("Insertar nuevo rol"):
        nombre_rol = st.text_input("Nombre del Rol", key="insertar")
        descripcion = st.text_area("Descripción", key="desc_insertar")
        if st.button("Insertar Rol"):
            if nombre_rol and descripcion:  # Validación básica
                insert_rol(nombre_rol, descripcion)
                st.success("Rol insertado con éxito")
                st.experimental_rerun()

    # Mostrar la lista de roles
    st.subheader("Lista de Roles")
    lista_roles = obtener_todos_los_roles()
    if lista_roles:
        df_roles = pd.DataFrame(lista_roles, columns=['id', 'nombre_rol', 'descripcion'])
        st.dataframe(df_roles)  # Mostrar los roles en un DataFrame

        # Selección de rol para editar o eliminar
        selected_role_id = st.selectbox("Seleccione un Rol para Editar o Eliminar", df_roles['id'])

        # Obtener los datos del rol seleccionado
        selected_role_data = df_roles[df_roles['id'] == selected_role_id].iloc[0]
        nombre_rol = selected_role_data['nombre_rol']
        descripcion = selected_role_data['descripcion']

        # Editar o eliminar rol
        st.session_state.edit_mode = st.checkbox("Editar Rol Seleccionado", value=st.session_state.edit_mode)
        if st.session_state.edit_mode:
            nombre_rol = st.text_input("Editar Nombre del Rol", value=nombre_rol)
            descripcion = st.text_area("Editar Descripción", value=descripcion)

            if st.button("Guardar Cambios"):
                if nombre_rol and descripcion:  # Validación básica
                    #actualizar_rol(selected_role_id, nombre_rol, descripcion)
                    st.success("Rol actualizado con éxito")
                    st.session_state.edit_mode = False  # Resetear el estado del checkbox
                    st.experimental_rerun()

        if st.button("Eliminar Rol"):
            eliminar_rol(selected_role_id)
            st.success("Rol eliminado con éxito")
            st.experimental_rerun()
