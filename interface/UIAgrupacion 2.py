
import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id, endpoint_write_order_note
from db.db_productosValidados import insert_productos_validados,update_order_product_status
from db.db_UserInteractionEvents import event_instert
from datetime import datetime
import streamlit.components.v1 as components


def UIOrdenesAgrupar(data):
    st.header("Ordenes a agrupar")
    header_col1, header_col2, header_col3, header_col4,header_col5 = st.columns([1, 3, 2, 2, 2])
    header_col1.write("")
    header_col2.write("**Ordenes Padre**")
    header_col3.write("**Pedidos Auditados**")
    header_col4.write("**En proceso**") 
    header_col5.write("**Estado**") 