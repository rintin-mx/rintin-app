import sys
sys.path.append('..')

from config import USER, PASSWORD,HOST,DATABASE,USER_REPLICA,PASSWORD_REPLICA,HOST_REPLICA,DATABASE_REPLICA

import mysql.connector
import pandas as pd
import numpy as np
import time

def config_db(db='repl') -> dict:
    
    if db == 'prod':
        config = {
            'user': USER,
            'password': PASSWORD,
            'host': HOST,
            'database': DATABASE
        }
    else:
        config = {
            'user': USER_REPLICA,
            'password': PASSWORD_REPLICA,
            'host': HOST_REPLICA,
            'database': DATABASE_REPLICA
        }
    return config

def get_lista_ordenes_padre(db='repl'):

    # Get a list of Parent orders and their children orders to be searched in the UI

    # Parameters:
    # None

    # Returns:
    # Dataframe: a dataframe containing the query results 
    #             (Parent_order_id, [children_order_id,children_order_id, ..., children_order_id])

    
    config = config_db(db)
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        ordenes_padres_e_hijos_sql = """
        with orders as (
	select
		id,
		post_parent,
		post_status
	from wp_posts 
	where post_type = 'shop_order'
),
final_helper as(
select 
	post_parent,
	count(case when post_status not in ('wc-empaquetar', 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces') then id else null end) as ordenes_activas,
	count(case when post_status = 'wc-agrupar-pedidos' then id else null end) as pedidos_auditados,
    group_concat(case when post_status not in ('wc-empaquetar', 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces') then id else null end separator ', ') as hijos_en_proceso
from 
	orders

where post_parent != 0
group by post_parent
having ordenes_activas > 0
),
ordenes_padres AS (
	select
		id,
		post_parent,
		post_status
	from wp_posts 
	where post_type = 'shop_order' and post_parent = 0
),
helper_3 as (
select
	ordenes_padres.id as order_id,
    ordenes_padres.id as hijos
from
	ordenes_padres
where
	ordenes_padres.id not in (
    select
		distinct post_parent
	from wp_posts 
	where post_type = 'shop_order' and post_parent != 0
    )
    and post_status not in ('wc-empaquetar', 'wc-pendientes_ograma', 'wc-failed', 'wc-caducado', 'wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces')
)
select post_parent as order_id, 
hijos_en_proceso as hijos
from final_helper 
union
select
	order_id,
    hijos
from
	helper_3
order by order_id desc

        """
        
        # Ejecutar la primera consulta
        cursor.execute(ordenes_padres_e_hijos_sql)

        # Obtener los resultados de la primera consulta
        resultados_ordenes_padres_e_hijos_sql = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        ordenes_padres_e_hijos = pd.DataFrame(resultados_ordenes_padres_e_hijos_sql)

    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close() 
        # Nueva lista de nombres de columnas
        return ordenes_padres_e_hijos

def get_order_bitacora(order_id, db='Repl'):

    # Get all the information needed to create a Bitacora for a Parent order, including the childrens info

    # Parameters:
    # order_id (int): the Parent order_id

    # Returns:
    # Dataframe: A Dataframe containing the query results
    # ()

    config = config_db(db)
    
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        
        info_bitacora = f"""
        With order_client_info AS (
select 
	post_id as order_id,
    MAX(case When meta_key = '_customer_user' then meta_value end) as customer_user,
	MAX(case When meta_key = '_billing_first_name' then meta_value end) as billing_first_name,
    MAX(case When meta_key = '_billing_last_name' then meta_value end) as billing_last_name,
    MAX(case When meta_key = '_billing_phone' then meta_value end) as billing_phone,
    MAX(case When meta_key = '_order_total' then meta_value end) as sub_total,
    MAX(case When meta_key = '_cart_discount' then meta_value end) as discount,
    MAX(case When meta_key = '_shipping_address_index' then meta_value end) as shipping_addres,
    MAX(case When meta_key = '_billing_postcode' then meta_value end) as postcode,
    MAX(case When meta_key = '_shipping_address_2' then meta_value end) as shipping_addres_2,
    MAX(case When meta_key = '_shipping_state' then meta_value end) as shipping_state,
    MAX(case When meta_key = '_billing_tipo_negocio_entrega' then meta_value end) as negocio_entrega,
    MAX(case When meta_key = '_billing_hora_preferente_entrega' then meta_value end) as hora_preferente,
    MAX(case When meta_key = '_order_shipping' then meta_value end) as order_shipping,
    MAX(case When meta_key = '_payment_method' then meta_value end) as payment_method_title
from
	wp_postmeta
where post_id = {order_id}
),
comentarios AS (
select 
	comment_post_ID as order_id,
    group_concat(comment_content separator ',') as comments
from 
	wp_comments
where 
    comment_content like 'comentario interno%'
group by 
    order_id
),
zona_entrega AS (
SELECT
wordpress.codigos_postales.codigo_postal as postcode,
wordpress.zonas_entrega.zona_entrega as zona_entrega,
estado
FROM wordpress.cobertura
LEFT JOIN wordpress.codigos_postales ON wordpress.codigos_postales.id = fk_id_codigo_postal
INNER JOIN wordpress.zonas_entrega ON wordpress.zonas_entrega.id = fk_id_zonas_entrega
where zona_entrega like '%pickup%'
),
shipping_detail as (
  select
    wp_woocommerce_order_items.order_item_name AS order_item_name,
    wp_woocommerce_order_items.order_id AS order_id
  from
    (
      wp_woocommerce_order_items
    )
  where
    wp_woocommerce_order_items.order_item_type = 'shipping'
),
shipping_method AS (
select
	shipping_detail.order_id AS order_id,
	group_concat(
	  shipping_detail.order_item_name separator ','
	) AS order_item_name
from
	shipping_detail
group by
	shipping_detail.order_id
),
subpedidos AS (
select
    post_parent,
    post_date,
	count(ID) as num_subpedidos,
    group_concat(case when post_parent != 0 then ID end separator ',') as pedidos_hijos
from
	wp_posts
group by
	post_parent
)
select
	order_client_info.order_id AS order_id,
    concat(order_client_info.billing_first_name, ' ', order_client_info.billing_last_name) AS full_name,
    order_client_info.billing_phone AS phone,
    wp_posts.post_date AS fecha_orden,
    order_client_info.sub_total - order_client_info.order_shipping + order_client_info.discount AS sub_total,
    order_client_info.discount AS discount,
    order_client_info.order_shipping AS shipping,
    order_client_info.sub_total AS total,
    order_client_info.shipping_addres AS shipping_addres,
    concat(case when order_client_info.shipping_addres_2 is null then '' else order_client_info.shipping_addres_2 end,
			'. Preferible a la hora: ',
            case when order_client_info.hora_preferente is null then '' else order_client_info.hora_preferente end,
			', se entregará en:',
            case when order_client_info.negocio_entrega is null then '' else order_client_info.negocio_entrega end) AS comentarios_entrega,
    Case
		When order_client_info.payment_method_title = 'cheque' or lcase(order_client_info.payment_method_title) = 'cod' then 'COD'
        else 'Prepaid'
	end as pay_method,
    case 
		when zona_entrega.zona_entrega is not null then zona_entrega.zona_entrega
		else '' end AS zona,
    Case
		when shipping_method.order_item_name like '%Oaxaca%' then 'Bodega Oaxaca'
		when shipping_method.order_item_name like '%Ciudad de Mexico%' then 'Bodega CDMX' COLLATE utf8mb4_general_ci
        when zona_entrega.zona_entrega is not null then
			case
				When zona_entrega.zona_entrega = 'pickup-A' then 'Zona Centro'
				When zona_entrega.zona_entrega = 'pickup-B' then 'Etla, Telix, Mazaltepec'
				When zona_entrega.zona_entrega = 'pickup-C' then 'Tlacolula, Ixtaltepec, Tlapazola'
				When zona_entrega.zona_entrega = 'pickup-D' then 'Ocotlan, Zimatlan'
				When zona_entrega.zona_entrega = 'pickup-E' then 'Ejutla'
				When zona_entrega.zona_entrega = 'pickup-M' then 'Miahuatlan'
			end
        else
			case 
				when order_client_info.shipping_state = 'DF' or order_client_info.shipping_state = 'CDMX' or order_client_info.shipping_state = 'Ciudad de México' then 'Ciudad de México'
				when order_client_info.shipping_state = 'MX' or order_client_info.shipping_state = 'Estado de México' or order_client_info.shipping_state = 'México' then 'México'
				when order_client_info.shipping_state = 'NL' then 'Nuevo León'
				when order_client_info.shipping_state = 'NA' then 'Nayarit'
				when order_client_info.shipping_state = 'GT' then 'Guanajuato'
				when order_client_info.shipping_state = 'MI' then 'Michoacán'
				when order_client_info.shipping_state = 'AG' then 'Aguascalientes'
				when order_client_info.shipping_state = 'QR' then 'Quintana Roo'
				when order_client_info.shipping_state = 'ZA' then 'Zacatecas'
				when order_client_info.shipping_state = 'SI' then 'Sinaloa'
				when order_client_info.shipping_state = 'JA' or order_client_info.shipping_state = 'Jalisco' then 'Jalisco'
				when order_client_info.shipping_state = 'SO' or order_client_info.shipping_state = 'Sonora' then 'Sonora'
				when order_client_info.shipping_state = 'HG' or order_client_info.shipping_state = 'Hidalgo' then 'Hidalgo'
				when order_client_info.shipping_state = 'OA' or order_client_info.shipping_state = 'oaxaca' then 'Oaxaca'
				when order_client_info.shipping_state = 'TM' then 'Tamaulipas'
				when order_client_info.shipping_state = 'MO' or order_client_info.shipping_state = 'Morelos' then 'Morelos'
				when order_client_info.shipping_state = 'VE' then 'Veracruz'
				when order_client_info.shipping_state = 'CH' then 'Chihuahua'
				when order_client_info.shipping_state = 'BS' then 'Baja California Sur'
				when order_client_info.shipping_state = 'DG' then 'Durango'
				when order_client_info.shipping_state = 'TB' then 'Tabasco'
				when order_client_info.shipping_state = 'CO' then 'Coahuila'
				when order_client_info.shipping_state = 'BC' then 'Baja California'
				when order_client_info.shipping_state = 'SL' then 'San Luis Potosí'
				when order_client_info.shipping_state = 'YU' then 'Yucatán'
				when order_client_info.shipping_state = 'CM' then 'Campeche'
				when order_client_info.shipping_state = 'TL' then 'Tlaxcala'
				when order_client_info.shipping_state = 'QT' then 'Querétaro'
				when order_client_info.shipping_state = 'PU' then 'Puebla'
				when order_client_info.shipping_state = 'CH' then 'Chiapas'
				when order_client_info.shipping_state = 'GR' or order_client_info.shipping_state = 'Guerrero' then 'Guerrero'
				when order_client_info.shipping_state = 'CL' then 'Colima'
				when order_client_info.shipping_state = 'GT' then 'Guanajuato'
			end
	end AS destino,
    case when comentarios.comments is null then 'N/A' else comentarios.comments end AS comments,
    shipping_method.order_item_name AS metodo_de_envio,
    case when subpedidos.num_subpedidos is not null then subpedidos.num_subpedidos else 1 end AS num_subpedidos,
    case when subpedidos.num_subpedidos is not null then subpedidos.pedidos_hijos else order_client_info.order_id end  AS pedidos_hijos
from
	order_client_info
left join
	zona_entrega on order_client_info.postcode = zona_entrega.postcode
left join
	comentarios on order_client_info.order_id = comentarios.order_id
join
	shipping_method on order_client_info.order_id = shipping_method.order_id
left join
	subpedidos on order_client_info.order_id = subpedidos.post_parent
join
	wp_posts on order_client_info.order_id = wp_posts.ID
        """
        # Ejecutar la primera consulta
        cursor.execute(info_bitacora)

        # Obtener los resultados de la primera consulta
        resultados_info_bitacora = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        info_bitacora = pd.DataFrame(resultados_info_bitacora)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

    # Nueva lista de nombres de columnas
    info_bitacora = info_bitacora[['order_id','full_name','phone','fecha_orden','sub_total','discount','shipping','total', 'shipping_addres', 'comentarios_entrega', 'pay_method', 'zona', 'destino', 'comments', 'metodo_de_envio', 'num_subpedidos', 'pedidos_hijos']]
    # Nueva lista de nombres de columnas
    info_bitacora.columns = ['order_id','full_name','phone','fecha_orden','sub_total','discount','shipping','total', 'shipping_addres', 'comentarios_entrega', 'pay_method', 'zona', 'destino', 'comments', 'metodo_de_envio', 'num_subpedidos', 'pedidos_hijos']
    return info_bitacora

def get_fees_bitacora(order_id, db='Repl'):
    """
    Retrieves fee information from the database for a given order ID.

    Args:
        order_id (int): The ID of the order.
        db (str, optional): The name of the database. Defaults to 'Repl'.

    Returns:
        pandas.DataFrame: A DataFrame containing the order ID, fee name, and fee amount.
    """
    config = config_db(db)
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        fees = f"""
            select order_item_name as 'name', meta_value as fee_amount
            from wp_woocommerce_order_items oi
            inner join wp_woocommerce_order_itemmeta om on oi.order_item_id = om.order_item_id
            where order_id = {order_id}
            and meta_key = '_fee_amount'
            and order_item_type = 'fee' 
        """
        cursor.execute(fees)
        resultados_fees = cursor.fetchall()
        
    finally:
        cursor.close()
        conexion.close()
    if len(resultados_fees) > 0:
        fees = pd.DataFrame(resultados_fees)
        fees = fees[['name', 'fee_amount']]
        fees = fees.to_dict(orient='list')
    else:
        fees = {'name': [], 'fee_amount': []}
    return fees

def get_suborders_bitacora(orders_id, db='Repl'):

    # Get all the information needed to create a Bitacora for a Parent order, including the childrens info

    # Parameters:
    # order_id (int): the Parent order_id

    # Returns:
    # Dataframe: A Dataframe containing the query results
    # ()

    config = config_db(db)
    
    try:
        conexion = mysql.connector.connect(**config)
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor(dictionary=True)
        
        sub_orders = f"""
        With item_per_order AS (
select
	order_item_id,
    order_id
 from
	wp_woocommerce_order_items
where order_id in ({orders_id})
),
order_status AS (
select 
	ID as suborder_id,
	post_status
from
	wp_posts
),
tabla_producto as (
select
	ID as product_id,
    post_title as product_name
from
	wp_posts
where post_type = 'product'
),
vendor_info as (
select
	 user_id,
    max(
		case
			when `meta_key` = '_dokan_vendor_id' then `meta_value`
			else NULL
		end
	) AS `seller_id`,
    max(
		case
			when `meta_key` = 'dokan_store_name' then `meta_value`
			else NULL
		end
	) AS `dokan_store_name`,
    max(
		case
			when `meta_key` = 'wp_capabilities' then `meta_value`
			else NULL
		end
	) AS `capabilities`
from
	wp_usermeta
group by
	user_id
),
seller_info as (
select
	vendor_info.user_id as user_id,
    dokan_store_name as seller_name
from
	vendor_info
left join
	wp_users on vendor_info.user_id = wp_users.ID
where capabilities like '%seller%'
),
sellers as (
select
	post_id as order_id,
    max(
		case
			when `meta_key` = '_dokan_vendor_id' then `meta_value`
			else NULL
		end
	) AS `seller_id`
from
	wp_postmeta
where
	post_id in ({orders_id})
),
dokan as (
select
	order_id,
    seller_id
from
	wp_dokan_orders
where
	order_id in ({orders_id})
),
order_with_seller as (
select
	sellers.order_id,
    case when dokan.seller_id is not null then dokan.seller_id else sellers.seller_id end as def_seller_id
from
	sellers
left join
	dokan on sellers.order_id = dokan.order_id
    
union

select
	dokan.order_id as order_id,
    case when dokan.seller_id is not null then dokan.seller_id else sellers.seller_id end as def_seller_id
from
	sellers
right join
	dokan on sellers.order_id = dokan.order_id
),
order_and_seller as (
select
	order_id,
    seller_info.seller_name as seller_name
from
	order_with_seller
left join
	seller_info on order_with_seller.def_seller_id = seller_info.user_id
),
unit_per_pack AS (
select
    post_id as product_id,
    CASE
      WHEN cast(
        meta_value AS decimal(10, 2)
      ) = 0 THEN 1
      WHEN meta_value = '' THEN 1
      ELSE cast(
        meta_value AS decimal(10, 2)
      )
    END AS units_per_pack_absolute
from
	wp_postmeta
where meta_key = '_units_per_pack'
),
order_items_detail AS (
select
	wp_woocommerce_order_itemmeta.order_item_id as order_item_id,
    max(
		case
			when `meta_key` = '_product_id' then `meta_value`
			else NULL
		end
	) AS `product_id`,
    max(
		case
			when `meta_key` = '_qty' then `meta_value`
			else NULL
		end
	) AS `qty`,
    max(
		case
			when `meta_key` = '_line_total' then `meta_value`
			else NULL
		end
	) AS `line_total`,
    max(
		case
			when `meta_key` = '_line_subtotal' then `meta_value`
			else NULL
		end
	) AS `line_subtotal`
    from wp_woocommerce_order_itemmeta
    group by wp_woocommerce_order_itemmeta.order_item_id
),
order_items_detail_2 as (
select
	order_items_detail.order_item_id as order_item_id,
	order_items_detail.product_id as product_id,
    order_items_detail.qty as qty,
    order_items_detail.line_total as line_total,
    order_items_detail.line_subtotal as line_subtotal,
    order_items_detail.line_subtotal - order_items_detail.line_total as discount,
    tabla_producto.product_name as product_name
from
	order_items_detail
inner join
	tabla_producto on tabla_producto.product_id = order_items_detail.product_id
),
cambios_productos as (
select
	order_item_id, nuevo_producto_sku
from
	cambios_productos
),
final AS (
select
	post_status as estado,
    suborder_id as suborder,
    order_and_seller.seller_name as shop,
    order_items_detail_2.product_name as product_name,
    cambios_productos.nuevo_producto_sku as changes,
    units_per_pack_absolute as units_per_pack,
    qty as qty_of_packs,
    line_subtotal / qty as pack_price,
    order_items_detail_2.discount as discount
from
	item_per_order
left join order_status on item_per_order.order_id = order_status.suborder_id
left join order_items_detail_2 on order_items_detail_2.order_item_id = item_per_order.order_item_id
left join order_and_seller on item_per_order.order_id = order_and_seller.order_id
left join unit_per_pack on unit_per_pack.product_id = order_items_detail_2.product_id
left join cambios_productos on item_per_order.order_item_id = cambios_productos.order_item_id
)
select
	case
		when estado in ('wc-pendientes_ograma','wc-failed', 'wc-caducado','wc-cancelled', 'wc-devuelto', 'wc-devolucion_proces', 'wc-contracargo-ganad', 'wc-contra-cargo', 'wc-refunded', 'wc-reembolso-parcial') then 'Cancelado'
        when estado = 'wc-contra-cargo' then 'Contra-cargo'
        when estado in ('delivered', 'wc-delivered') then 'Entregado'
        when estado in ('wc-pending', 'wc-processing', 'wc-completed', 'wc-parcel', 'wc-auditoria', 'wc-embarque',
						'wc-contra-entrega', 'wc-stock-2', 'wc-recolectar-2', 'wc-auditoria-2', 'wc-rec-problem-2',
						'wc-pickup-4', 'wc-mod-padre-2', 'wc-recepcion-2', 'wc-pendiente-pago-1', 'wc-promesa_pago_1',
						'wc-prepara_pedido', 'wc-generar_pedido', 'wc-valida_cod_client', 'wc-pendientes_ograma',
						'wc-pedidos_auditar', 'wc-rec_ped_aud', 'wc-agrupar-pedidos', 'wc-generar_guia', 'wc-empaquetar',
						'wc-msj-creacion') then 'Confirmado'
	end AS estado,
    suborder,
    shop,
    product_name,
    case when changes is not null then concat('Se cambió por ', changes) else '' end as changes,
    units_per_pack,
    qty_of_packs,
    pack_price,
    discount,
    pack_price * qty_of_packs - discount as subtotal
from
	final
where
	qty_of_packs is not null
        """
        # Ejecutar la primera consulta
        cursor.execute(sub_orders)

        # Obtener los resultados de la primera consulta
        resultados_sub_orders = cursor.fetchall()

        # Convertir los resultados a un DataFrame de pandas
        sub_orders = pd.DataFrame(resultados_sub_orders)
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()
    # Nueva lista de nombres de columnas
    sub_orders = sub_orders[['estado','suborder','shop','product_name','changes','units_per_pack','qty_of_packs','pack_price', 'discount', 'subtotal']]
    # Nueva lista de nombres de columnas
    sub_orders.columns = ['estado','suborder','shop','product_name','changes','units_per_pack','qty_of_packs','pack_price', 'discount', 'subtotal']
    return sub_orders
