import streamlit as st
import pandas as pd
from db.db_roles import obtener_todos_los_roles
from db.db_pemrisos import obtener_todos_los_permisos
from streamlit_extras.dataframe_explorer import dataframe_explorer
from db.db_rolesPermisos import insertar_rol_permiso, eliminar_rol_permiso, actualizar_rol_permiso, obtener_todos_los_roles_permisos


def anadir_fila(rol,permiso):
    st.session_state.tabla = pd.concat([st.session_state.tabla, pd.DataFrame([{'Rol': rol, 'Permiso': permiso}])], ignore_index=True)
    #st.session_state.tabla = st.session_state.tabla.append({'Rol': rol, 'Permiso': permiso}, ignore_index=True)
    #st.experimental_rerun()

# Función para eliminar una fila de la tabla
def eliminar_fila(index):
    st.session_state.tabla = st.session_state.tabla.drop(index).reset_index(drop=True)
    #st.experimental_rerun()


def rolespermisos():
    st.title("Gestión de Roles y Permisos")
    with st.expander("Insertar nueva relación de roles y permisos"):
        if 'tabla' not in st.session_state:
            st.session_state.tabla = pd.DataFrame(columns=['Rol', 'Permiso'])
        lista_roles = obtener_todos_los_roles()
        df_rol = pd.DataFrame(lista_roles, columns=['rol_id','nombre_rol', 'descripcion'])
        df_rol['opsCompuesta'] = df_rol['rol_id'].astype(str) + '-' + df_rol['nombre_rol']
        rol_id_fk=st.selectbox("Seleccione una opción del rol", df_rol['opsCompuesta'], key='rol_id_fk_opsCompuesta')
        lista_permisos = obtener_todos_los_permisos()
        df_permiso = pd.DataFrame(lista_permisos, columns=['permiso_id', 'ops_id_fk','nombre_permiso', 'descripcion'])
        df_permiso['opsCompuestaPermiso'] = df_permiso['permiso_id'].astype(str) + '-' + df_permiso['nombre_permiso']
        permiso_id_fk=st.selectbox("Seleccione una opción de los permisos", df_permiso['opsCompuestaPermiso'],key='permiso_id_fk')
        # Botón para añadir una fila
        if st.button('Añadir a la tabla', key='add_row'):
            anadir_fila(rol_id_fk,permiso_id_fk)
            st.rerun()
        # Mostrar la tabla
        for index, row in st.session_state.tabla.iterrows():
            cols = st.columns([1, 1, 1])
            with cols[0]:
                st.write(row['Rol'])
            with cols[1]:
                st.write(row['Permiso'])
            with cols[2]:
                st.button('Eliminar', key=f'del_{index}', on_click=lambda idx=index: eliminar_fila(idx))
        if st.button('Crear'):
            for index, row in st.session_state.tabla.iterrows():
                id_fk_rol_clean=row['Rol'].split('-')[0]
                id_fk_permiso_clean=row['Permiso'].split('-')[0]
                print(id_fk_rol_clean)
                print(id_fk_permiso_clean)
                insertar_rol_permiso(id_fk_rol_clean,id_fk_permiso_clean)
                st.session_state.tabla = pd.DataFrame(columns=['Rol', 'Permiso'])

            st.success('The relationship was successfully created!')
            st.balloons()
            st.rerun()
    # Mostrar la lista de permisos
    st.subheader("Lista de la realción de roles y permisos")
    lista_roles_permisos = obtener_todos_los_roles_permisos()
    print('******************')
    print(lista_roles_permisos)
    print('******************')
    if lista_roles_permisos:
        #rp.rol_id_fk ,rp.permiso_id_fk,r.nombre_rol, p.nombre_permiso
        df_roles_permisos = pd.DataFrame(lista_roles_permisos, columns=['rol_id_fk', 'permiso_id_fk','nombre_rol','nombre_permiso'])
        #AgGrid(df_roles_permisos)
        filtered_df = dataframe_explorer(df_roles_permisos, case=True)
        st.dataframe(filtered_df, use_container_width=True)
        #st.dataframe(df_roles_permisos,hide_index=True,column_order=['rol_id_fk', 'nombre_rol','permiso_id_fk','nombre_permiso']) 