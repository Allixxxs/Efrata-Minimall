"""Servicios de negocio de Efrata Minimall.

Importar este paquete no inicia la consola ni crea archivos de datos.
"""

from .sesion import current_session
from .usuarios import authenticate_user, register_user, close_session
from .datos_personales import (
    read_personal_data, save_personal_data, delete_personal_data,
)
from .catalogo import (
    load_clothing_catalog, filter_clothing_catalog, load_suits, load_suit_descriptions
)
from .alquileres import (
    get_user_rentals, check_rental_conflict, register_rental, return_rental,
)
from .carrito import (
    read_cart, add_to_cart, update_cart_quantity, remove_from_cart,
    get_cart_details,
)
from .compras import (
    prepare_purchase, confirm_purchase, list_purchases, get_purchase_detail,
)
from .administracion import is_administrator
from .favoritos import list_favorites, add_favorite, remove_favorite

# Nombres heredados para facilitar la transición desde efrataminimall.py.
cargar_catalogo_ropa = load_clothing_catalog
filtrar_catalogo_ropa = filter_clothing_catalog
cargar_trajes = load_suits
cargar_descripciones_trajes = load_suit_descriptions
hay_conflicto_alquiler = check_rental_conflict
leer_carrito_usuario = read_cart
agregar_al_carrito = add_to_cart
actualizar_cantidad_carrito = update_cart_quantity
eliminar_del_carrito = remove_from_cart
obtener_detalle_carrito = get_cart_details
preparar_compra = prepare_purchase
mis_compras = list_purchases

__all__ = [
    "current_session", "authenticate_user", "register_user", "close_session",
    "read_personal_data", "save_personal_data", "delete_personal_data",
    "load_clothing_catalog", "filter_clothing_catalog", "load_suits",
    "get_user_rentals", "check_rental_conflict", "register_rental", "return_rental",
    "read_cart", "add_to_cart", "update_cart_quantity", "remove_from_cart",
    "get_cart_details", "prepare_purchase", "confirm_purchase",
    "list_purchases", "get_purchase_detail", "is_administrator",
    "list_favorites", "add_favorite", "remove_favorite",
    "cargar_catalogo_ropa", "filtrar_catalogo_ropa", "cargar_trajes",
    "hay_conflicto_alquiler", "leer_carrito_usuario", "agregar_al_carrito",
    "actualizar_cantidad_carrito", "eliminar_del_carrito",
    "obtener_detalle_carrito", "preparar_compra", "mis_compras", "load_suit_descriptions",
]
