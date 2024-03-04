import streamlit as st
import pandas as pd
from db.db_opciones_sistema import obtener_todos_los_opciones_sistema, actualizar_opciones_sistema, eliminar_opciones_sistema, insert_opciones_sistema

def opcionSistema():
    st.title("Gestión de Opciones de sistema")

    # Usar una variable de sesión para el estado del checkbox
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Inserción de un nuevo rol
    #`ops_id` int(11) NOT NULL AUTO_INCREMENT,
    #`nombre_opcion` varchar(100) NOT NULL,
    #`descripcion` text DEFAULT NULL,
    with st.expander("Insertar nueva opción de sistema"):
        nombre_opcion = st.text_input("Nombre de la opción", key="insertar_opcion")
        descripcion = st.text_area("Descripción", key="desc_insertar_opcion")
        if st.button("Insertar opciónde sistema", key="button_insertar_opcion"):
            if nombre_opcion and descripcion:  
                insert_opciones_sistema(nombre_opcion, descripcion)
                st.success("Opción de Sistema insertada con éxito")
                st.experimental_rerun()

    # Mostrar la lista de roles
    st.subheader("Lista de Opciones de Sistema")
    lista_roles = obtener_todos_los_opciones_sistema()
    if lista_roles:
        df_opciones = pd.DataFrame(lista_roles, columns=['ops_id', 'nombre_opcion', 'descripcion'])
        st.dataframe(df_opciones)  # Mostrar los roles en un DataFrame

        # Selección de rol para editar o eliminar
        selected_opciones_id = st.selectbox("Seleccione una opción de sietema para Editar o Eliminar", df_opciones['ops_id'])

        # Obtener los datos del rol seleccionado
        selected_opcion_data = df_opciones[df_opciones['ops_id'] == selected_opciones_id].iloc[0]
        nombre_opcion = selected_opcion_data['nombre_opcion']
        descripcion = selected_opcion_data['descripcion']

        # Editar o eliminar rol
        st.session_state.edit_mode = st.checkbox("Editar opción de sistema Seleccionada", value=st.session_state.edit_mode)
        if st.session_state.edit_mode:
            nombre_opcion = st.text_input("Editar Nombre del Rol", value=nombre_opcion)
            descripcion = st.text_area("Editar Descripción", value=descripcion)

            if st.button("Guardar Cambios", key="button_guardar_cambios_opcion"):
                if nombre_opcion and descripcion:  # Validación básica
                    actualizar_opciones_sistema(selected_opciones_id, nombre_opcion, descripcion)
                    st.success("Opción de sistema actualizado con éxito")
                    st.session_state.edit_mode = False  # Resetear el estado del checkbox
                    st.experimental_rerun()
        
       
        if st.button("Eliminar opción de sistema"):
            eliminar_opciones_sistema(selected_opciones_id)
            st.success("Opción de sistema eliminadoacon éxito")
            st.experimental_rerun()
