from .sesion import EstadoSesion, sesion_actual
from .usuarios import autenticar_usuario, registrar_usuario, cerrar_sesion
from .datos_personales import leer_datos_personales, guardar_datos_personales, eliminar_datos_personales
from .catalogo import (
    cargar_catalogo_ropa, filtrar_catalogo_ropa, cargar_trajes,
    cargar_descripciones_trajes, validar_catalogo_ropa, validar_inventario,
    validar_trajes,
    guardar_trajes, actualizar_disponibilidad_traje,
)
from .alquileres import (
    obtener_alquileres_usuario, hay_conflicto_alquiler, registrar_alquiler, devolver_alquiler,
)
from .carrito import (
    leer_carrito, agregar_al_carrito, actualizar_cantidad_carrito,
    eliminar_del_carrito, obtener_detalles_carrito,
)
from .compras import (
    preparar_compra, confirmar_compra, listar_compras, obtener_detalle_compra,
)
from .administracion import (
    es_administrador, cargar_inventario_administracion, registrar_producto,
    actualizar_producto, agregar_variante_existencias, actualizar_existencias,
    desactivar_producto, listar_clientes_administracion,
    cargar_trajes_administracion, registrar_traje, actualizar_traje,
    listar_compras_administracion, listar_alquileres_administracion,
    obtener_estadisticas_administracion,
)
from .favoritos import listar_favoritos, agregar_favorito, eliminar_favorito

__all__ = [
    "EstadoSesion", "sesion_actual", "autenticar_usuario", "registrar_usuario",
    "cerrar_sesion", "leer_datos_personales", "guardar_datos_personales",
    "eliminar_datos_personales", "cargar_catalogo_ropa", "filtrar_catalogo_ropa",
    "cargar_trajes",     "cargar_descripciones_trajes", "validar_catalogo_ropa", "validar_trajes",
    "validar_inventario", "guardar_trajes", "actualizar_disponibilidad_traje",
    "obtener_alquileres_usuario", "hay_conflicto_alquiler", "registrar_alquiler",
    "devolver_alquiler", "leer_carrito", "agregar_al_carrito",
    "actualizar_cantidad_carrito", "eliminar_del_carrito", "obtener_detalles_carrito",
    "preparar_compra", "confirmar_compra", "listar_compras",
    "obtener_detalle_compra", "es_administrador",
    "cargar_inventario_administracion", "registrar_producto", "actualizar_producto",
    "agregar_variante_existencias", "actualizar_existencias", "desactivar_producto",
    "cargar_trajes_administracion", "registrar_traje", "actualizar_traje",
    "listar_clientes_administracion", "listar_compras_administracion",
    "listar_alquileres_administracion", "obtener_estadisticas_administracion",
    "listar_favoritos", "agregar_favorito", "eliminar_favorito",
]
