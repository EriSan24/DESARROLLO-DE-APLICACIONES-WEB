from conexion.conexion import initialize_database, get_products, insert_product, get_product_by_code, update_product, delete_product

initialize_database()
print('COUNT_BEFORE', len(get_products()))
product = {'codigo': 'P999', 'nombre': 'Producto prueba', 'categoria': 'Pruebas', 'precio': 42.5, 'stock': 7}
print('INSERT', insert_product(product))
print('FOUND', get_product_by_code('P999'))
print('UPDATE', update_product('P999', 'P999', 'Producto modificado', 'Pruebas', 99.9, 15))
print('FOUND_AFTER_UPDATE', get_product_by_code('P999'))
print('DELETE', delete_product('P999'))
print('COUNT_AFTER', len(get_products()))
