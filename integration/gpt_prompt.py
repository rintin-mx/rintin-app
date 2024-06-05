from openai import OpenAI

# API key
key = "sk-proj-Tw1KNpopjJ5E9hxFrRtsT3BlbkFJlQIbd2Z8Jq0VExcGvMNG"

client = OpenAI(
    api_key=key,
)

# Prompt para chatGPT
messages=[
  {
    "role": "user",
    "content": [
      {"type": "text",
      "text": """
        Extrae de los productos en las imágenes: 
        codigo_de_producto (si no se encuentra, dejar vacío), 
        Categoria_padre (Hombre, mujer, niño/niña, unisex, productos varios),
        Categoria_hijo (Ropa, calzado, Maquillaje, Bolsas/Mochilas/carteras, accesorios, escolar/profesional, papeleria),
        Subcategoria_1 (Ropa Interior,Pantalones,Pantuflas,Sandalias,Tenis,Carteras,Jeans,Chalecos,Bolsas,Pijamas,Vestidos,Blusas,Ropa Deportiva,Sueters,Chamarras,Conjuntos,Playeras,Pants,Leggings,Sudaderas,Gorras/Viseras/Sombreros,Faldas,Shorts,Calcetines/calceteria,Bermudas,Ponchos/Capas/Kimonos,Camisas,Ropa de Maternidad,Trajes de Baño,Tops,Botas y Botines,Palazzo,Impermeables,Jumpsuit,Mangas,Lenceria,Mochilas,Joggers,Bufanda,Saco),
        Subcategoria_2 (Tenis Casual,Corte Skinny,Corte Acampanado,Tenis Deportivo,Mochilas,Chamarra Mezclilla,Corte Wide Leg,Corte Mom,Pijamas,Ropa térmica,Corte Colombiano,Conjunto,Crop Top,Leggings,Boxers,Cacheteros,Brasier,Pantaletas,Falda,Short,Protectores,Corte Vaquero,Baby Dalls,Faja,Overol,Tops,Corte Cargo,Corte Recto,Corte Stretch,Tanga,Bikini,Calcetines tobillo,Trusa,Medias,Calcetines Altos,Calcetines cortos,Camiseta,Corset,Calcetines Medios,Bolsa Formal,Body,Corte Extra Skinny,Corte Slim Fit,Corte Regular Fit,Licras,Top niña,Talla Extra,Chaleco Mezclilla,Vestidos largos,Vestidos cortos),
        Subcategoria_3 (Escoge entre estas opciones o deja vacío: Algodón, Encaje, Microfibra, Sin costura),
        Tipo_de_producto (Escoge entre estas opciones o deja vacío: Linea continua, Promocion, Novedad),
        Nombre_de_producto (Si existe uno en la imágen colócalo, sino, creea un nombre como lo haría un experto en ecomerce Mexicano en no más de 5 palabras),
        Venta_por_unidad_o_paquete (escribir paquete si es por paquete y unidad si se vende por unidad),
        Tipo_de_unidad (Kit, Piezas, Paquetes),
        Unidades_por_paquete (si lo incluye la imagen, sino dejar vacío),
        Marca (Si no aparece marca, dejar en blanco),
        Material_composicion_y_porcentajes (Si aparece en la imagen información de la composición del producto, sino dejar vacío),
        Importado_o_hecho_en_mexico (Coloca "Importado" o "Hecho en méxico"),
        Colores_presentes_en_producto (varios colores (escribe los colores que identifiques), un color),
        Tallas (Si se muestra en la imagen, sino dejar vacío),
        Observaciones (Coloca observaciones que te parezcan relevantes del producto en no más de 20 palabras)

        responde únicamente colocando esta información en un csv en formato tabla donde cada línea representa 1 producto o 1 imagen que ha sido enviada junto con este mensaje y no coloques tíldes en la información de respuesta. A demás, si vas a hacer un listado, no coloques comas para separar los items de la lista. Sepáralos a través de guiones. Por último, no te saltes campos. Si no tienes respuesta para un campo, dejalo vacío.
        """
      },
    ],
  }
]