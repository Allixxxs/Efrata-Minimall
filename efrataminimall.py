"""Lanzador compatible con el nombre original del programa."""

from main import main
from backend import *
from backend.catalogo import save_suits as guardar_trajes, update_suit_availability as actualizar_disponibilidad
from backend.alquileres import get_user_rentals as obtener_mis_alquileres
from consola import (
    sesion, cuenta, home, buscar, alquiler_trajes, consultar_alquileres,
    devolver_traje, carrito, favoritos, mis_datos, mostrar_catalogo,
    mostrar_catalogo_ropa, mostrar_carrito,
    mis_compras, confirmar_compra,
)
from backend.administracion import (
    is_administrator as es_administrador,
    register_product as registrar_producto_admin,
    update_product as modificar_producto_admin,
    add_stock_variant as agregar_existencia_admin,
    update_stock as actualizar_existencia_admin,
    deactivate_product as desactivar_producto_admin,
)


def __getattr__(name):
    """Compatibilidad de solo lectura con los antiguos globales de sesión."""
    if name == "usuario":
        from backend.sesion import current_session
        return current_session.email
    if name == "sesion_activa":
        from backend.sesion import current_session
        return current_session.active
    if name == "contraseña":
        from backend.sesion import current_session
        return current_session.password
    raise AttributeError(name)


if __name__ == "__main__":
    main()
