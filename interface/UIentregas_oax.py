import sys
sys.path.append('..')

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import asyncio
from integration.endpoint_wordpress import endpoint_update_status_by_order_id
from db.db_entregas_oax import insert_route, update_route_order_status, insert_product_problem, update_recieved_money, update_route_status

DIFF_REASONS = ['Producto faltante', 'Producto con falla', 'Cliente sin dinero']
NO_ENTREGA_REASON = ['Sin contacto de cliente', 'Cliente sin dinero', 'No encuentro direccion']
NEXT_STATUS_DICT = {
	"Pendiente entrega": "Intento 1",
	"Intento 1": "Intento 2",
	"Intento 2": "Intento 3",
	"Intento 3": "Fallido"
}

async def update_status_wordpress(order_id, order_status):
    result = await endpoint_update_status_by_order_id(order_id, order_status)
    return result

def UIentregas_oax(data):
	respuesta = False
	st.markdown('''<style>
		.block-container{
			padding-top: 0
		}
		div[data-testid="stVerticalBlock"]:has(div.container_1){
			top: 30px;
			padding-bottom: 20px;
		}
		div[data-testid="stVerticalBlock"]:has(div.container_2){
			margin-top: 30px;
		}
		div:has( >.element-container div.floating) {
			display: flex;
			flex-direction: column;
			position: fixed;
			top: 30px;
			z-index: 99;
			   background-color: white !important;
		}
	</style>
	
	''', unsafe_allow_html=True)
	container = st.container()
	with container:
		st.write('<div class="floating"></div>', unsafe_allow_html=True)
		st.write('# Pedidos a entregar')
		button = st.button('Generar ruta')
	container2 = st.container()
	with container2:
		st.write('<div class="container_2"></div>', unsafe_allow_html=True)
		orders_for_route_list = []
		for i in range(len(data["order_id"])):
			st.write('#### Cliente:')
			st.write(f'{data["name"][i]}')
			st.write('#### Número de pedido:')
			st.write(f'{data["order_id"][i]}')
			st.write('#### Número de contacto:')
			st.write(f'{data["number_unified"][i]}')
			st.write('#### Dirección:')
			st.write(f'{data["address"][i]}')
			st.write('#### Número de paquetes:')
			st.write(f'{int(data["num_paquetes"][i])}')
			st.write('### Zona de entrega:')
			st.write(f'{data["zona_entrega"][i]}')
			checked = st.checkbox('Ingresar a ruta', key=i)
			if checked:
				orders_for_route_list.append({
					"order_id": data["order_id"][i],
					"name": data["name"][i],
					"number_unified": data["number_unified"][i],
					"address": data["address"][i],
					'total': data['order_total'][i]
				})
			st.write('---')
	respuesta = ui.alert_dialog(show=button, title="Confirmación de ruta", description=f'Se creará una ruta con {len(orders_for_route_list)} ordenes distintas.', confirm_label="Confirmar", cancel_label="Volver", key="alert_dialog_order")
	if respuesta:
		insert_route(st.session_state.username, orders_for_route_list)
		print('dentro')
		st.session_state['current_view'] = 'entregas_oax'
		st.rerun()
		
def UIroute_orders(data, route_id):
	respuesta = False
	st.write('## Entregas')
	st.write(f'### {st.session_state.username}')
	st.write('---')
	if data:
		for i in range(len(data["order_id"])):
			st.write('#### Cliente:')
			st.write(f'{data["name"][i]}')
			st.write('#### Número de pedido:')
			st.write(f'{data["order_id"][i]}')
			st.write('#### Número de contacto:')
			st.write(f'{data["number_unified"][i]}')
			st.write('#### Dirección:')
			st.write(f'{data["address"][i]}')
			st.write('#### Número de paquetes:')
			st.write(f'{int(data["num_paquetes"][i])}')
			button = st.button('Entregar', key=i)
			st.write('---')
			if button:
				st.session_state['current_order'] = {
					"name": data["name"][i],
					"order_id": data["order_id"][i],
					"number_unified": data["number_unified"][i],
					"address": data["address"][i],
					"total": data['order_total'][i],
					"estado": data["estado"][i]
				}
				st.session_state.route_id = route_id
				st.session_state.current_view = 'entrega_order_detail'
				st.rerun()
	else:
		st.write('### No hay ordenes pendientes en la ruta. Puedes finalizarla.')
	button = st.button('Terminar ruta')
	respuesta = ui.alert_dialog(show=button, title="Confirmación de terminación de ruta", description=f'¿Estas seguro que deseas terminar la ruta?', confirm_label="Confirmar", cancel_label="Volver", key="respuesta_terminar")
	if respuesta:
		update_route_status(route_id, 'Finalizado')
		st.session_state.current_view = 'entregas_oax'
		st.rerun()

def order_detail(order_id, number_unified, address, total, order_items, route_id, estado):
	if st.button('Regresar'):
		st.session_state.current_view = 'entregas_oax'
		st.rerun()
	orders_dict = {}
	respuesta = False
	st.write(f'### Pedido: {order_id}')
	st.write(f'### Telefono cliente: {number_unified}')
	st.write(f'### Dirección:')
	st.write(address)
	st.write('---')
	st.write('En caso de no haber entregado el pedido:')
	razon_no_entrega = st.selectbox('Razon de no entrega', options=NO_ENTREGA_REASON, index=None)
	no_entregue_btn = st.button('No se entregó el pedido')
	if no_entregue_btn and razon_no_entrega != None:
		update_route_order_status(route_id, order_id, NEXT_STATUS_DICT[estado], razon_no_entrega)
		st.session_state.current_view = 'entregas_oax'
		st.rerun()
	st.write('---')
	st.write('#### Productos de la orden')
	order_items_con_falla = []
	for i in range(len(order_items['order_item_id'])):
		st.image(order_items['img_url'][i])
		st.write('#### Nombre de producto:')
		st.write(order_items['order_item_name'][i])
		st.write('#### SKU:')
		st.write(order_items['sku'][i])
		st.write('#### Cantidad:')
		st.write(int(order_items['line_qty'][i]))
		recieved = st.number_input('Cantidad recibida', min_value=0, max_value=int(order_items['line_qty'][i]), step=1, key=f'amount_{i}')
		if recieved != int(order_items['line_qty'][i]):
			reason = st.selectbox('Razón diferencia', options=DIFF_REASONS, key=f'select_{i}')
			st.error('Validación')
			order_items_con_falla.append({
				"order_item_id": order_items['order_item_id'][i],
				"cantidad_entregada": recieved,
				"razon_no_entrega": reason
			})
		else:
			reason = ''
			st.success('OK')
		if order_items['order_id'][i] in orders_dict:
			orders_dict[order_items['order_id'][i]] += recieved
		else:
			orders_dict[order_items['order_id'][i]] = recieved
	st.write('---')
	st.write(f'Total a cobrar: ${total}')
	value = st.number_input('Total recibido: ', min_value=0.00, step=0.01)
	if value != float(total):
		st.error('Validacion')
	button = st.button('Confirmar entrega')
	respuesta = ui.alert_dialog(show=button, title="Confirmación de entrega de orden", description=f'Se entrego la orden {order_id}', confirm_label="Confirmar", cancel_label="Volver", key="respuesta_entrega")
	if respuesta:
		for product in order_items_con_falla:
			insert_product_problem(route_id, product)
		update_route_order_status(route_id, order_id, 'Entregado', razon_no_entrega)
		update_recieved_money(order_id, value)
		for order in orders_dict:
			if orders_dict[order] == 0:
				r = asyncio.run(update_status_wordpress(order, 'devolucion_proces'))
		for order in orders_dict:
			if orders_dict[order] != 0:
				r = asyncio.run(update_status_wordpress(order, 'delivered'))
		st.session_state.current_view = 'entregas_oax'
		st.rerun()
	