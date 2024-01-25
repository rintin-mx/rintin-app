import streamlit as st
from db.db_recoleccion import get_seller_recollection,get_data_seller_by_name
from db.db_order import get_order,get_seller
import pandas as pd


def app():
    if 'username' in st.session_state:
        print("st.session_state.username")
        print(st.session_state.username)
        print("st.session_state.username")
    else:
        st.image("imagen/logo_imagen_no_loguado.png", width=300)
        st.markdown("### Por favor, inicia sesión para continuar")
