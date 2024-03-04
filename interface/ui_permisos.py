import streamlit as st
import pandas as pd
from db.db_pemrisos import insertar_permiso, eliminar_permiso, actualizar_permiso, obtener_todos_los_permisos
from db.db_opciones_sistema import obtener_todos_los_opciones_sistema

def opcionSistema():
    lista_roles = obtener_todos_los_opciones_sistema()
    df_opciones = pd.DataFrame(lista_roles, columns=['ops_id', 'nombre_opcion', 'descripcion'])
    df_opciones['opsCompuesta'] = df_opciones['ops_id'].astype(str) + '-' + df_opciones['nombre_opcion']
    return df_opciones

def permisos():
    st.title("Gestión de Permisos")

    # Usar una variable de sesión para el estado del checkbox
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Inserción de un nuevo permiso
    with st.expander("Insertar nuevo permiso"):
        df_opciones=opcionSistema()
        ops_id_fk=st.selectbox("Seleccione una opción de sistema", df_opciones['opsCompuesta'])
        id_fk_clean=ops_id_fk.split('-')[0]
        print(id_fk_clean)
        nombre_permiso = st.text_input("Nombre del Permiso:", key="insertar_permiso_nombre")
        descripcion = st.text_area("Descripción", key="insertar_permiso_descripcion")
        if st.button("Insertar Permiso", key="button_insertar_permiso"):
            if ops_id_fk and nombre_permiso and descripcion:
                insertar_permiso(id_fk_clean, nombre_permiso, descripcion)
                st.success("Permiso insertado con éxito")
                st.experimental_rerun()

    # Mostrar la lista de permisos
    st.subheader("Lista de Permisos")
    lista_permisos = obtener_todos_los_permisos()
    if lista_permisos:
        df_permisos = pd.DataFrame(lista_permisos, columns=['permiso_id', 'ops_id_fk', 'nombre_permiso', 'descripcion'])
        st.dataframe(df_permisos)  # Mostrar los permisos en un DataFrame
        df_permisos['opsCompuesta'] = df_permisos['permiso_id'].astype(str) + '-' + df_permisos['nombre_permiso']

        # Selección de permiso para editar o eliminar
        selected_permiso_id = st.selectbox("Seleccione un Permiso para Editar o Eliminar", df_permisos['opsCompuesta'])
        id_fk_permiso_clean=int(selected_permiso_id.split('-')[0])
        print(id_fk_permiso_clean)
        print(df_permisos['permiso_id'])

        # Obtener los datos del permiso seleccionado
        selected_permiso_data = df_permisos[df_permisos['permiso_id'] == id_fk_permiso_clean].iloc[0]
        ops_id_fk = selected_permiso_data['ops_id_fk']
        nombre_permiso = selected_permiso_data['nombre_permiso']
        descripcion = selected_permiso_data['descripcion']

        # Editar o eliminar permiso
        st.session_state.edit_mode = st.checkbox("Editar Permiso Seleccionado", value=st.session_state.edit_mode)
        if st.session_state.edit_mode:
            ops_id_fk = st.text_input("Editar Ops ID", value=ops_id_fk, key="editar_permiso_ops_id")
            nombre_permiso = st.text_input("Editar Nombre del Permiso", value=nombre_permiso, key="editar_permiso_nombre")
            descripcion = st.text_area("Editar Descripción", value=descripcion, key="editar_permiso_descripcion")

            if st.button("Guardar Cambios", key="button_guardar_cambios_permiso"):
                if ops_id_fk and nombre_permiso and descripcion:  # Validación básica
                    actualizar_permiso(id_fk_permiso_clean, ops_id_fk, nombre_permiso, descripcion)
                    st.success("Permiso actualizado con éxito")
                    st.session_state.edit_mode = False  # Resetear el estado del checkbox
                    st.experimental_rerun()

        if st.button("Eliminar Permiso"):
            eliminar_permiso(id_fk_permiso_clean)
            st.success("Permiso eliminado con éxito")
            st.experimental_rerun()