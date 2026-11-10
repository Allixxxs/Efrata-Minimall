"""Operaciones protegidas de administración del inventario de ropa."""

import os
import tempfile
import pandas as pd
from .rutas import ARCHIVO_ADMINISTRADORES, ARCHIVO_ROPA, DIRECTORIO_DATOS
from .sesion import sesion_actual
from .catalogo import validar_inventario


def es_administrador(correo):
    if not sesion_actual.activa or not sesion_actual.correo or correo is None:
        return False
    normalizado = str(correo).strip().casefold()
    if normalizado != sesion_actual.correo.casefold() or not ARCHIVO_ADMINISTRADORES.exists():
        return False
    with ARCHIVO_ADMINISTRADORES.open("r", encoding="utf-8") as archivo:
        autorizado = {linea.strip().casefold() for linea in archivo
                      if linea.strip() and not linea.lstrip().startswith("#")}
    return normalizado in autorizado


def _requerir_administrador():
    if not es_administrador(sesion_actual.correo):
        raise PermissionError("Esta operación requiere una sesión administrativa autorizada.")


def cargar_inventario_administracion():
    _requerir_administrador()
    if not ARCHIVO_ROPA.exists():
        raise FileNotFoundError("No se encontró ropa.xlsx.")
    try:
        productos = pd.read_excel(ARCHIVO_ROPA, sheet_name="Productos")
        existencias = pd.read_excel(ARCHIVO_ROPA, sheet_name="Existencias")
    except (ValueError, OSError, ImportError) as error:
        raise ValueError("No se pudo leer ropa.xlsx o faltan sus hojas.") from error
    return validar_inventario(productos, existencias)


def guardar_inventario_administracion(productos, existencias):
    _requerir_administrador()
    productos, existencias = validar_inventario(productos, existencias)
    if not ARCHIVO_ROPA.exists():
        raise FileNotFoundError("No se encontró ropa.xlsx.")
    descripcion, nombre_temporal = tempfile.mkstemp(prefix=".ropa_admin_", suffix=".xlsx", dir=DIRECTORIO_DATOS)
    os.close(descripcion)
    try:
        with pd.ExcelWriter(nombre_temporal, engine="openpyxl") as escritor:
            productos.to_excel(escritor, sheet_name="Productos", index=False)
            existencias.to_excel(escritor, sheet_name="Existencias", index=False)
        os.replace(nombre_temporal, ARCHIVO_ROPA)
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise


def registrar_producto(codigo, nombre, seccion, categoria, precio):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    codigo, nombre, categoria = str(codigo).strip(), str(nombre).strip(), str(categoria).strip()
    if not codigo or not nombre or not categoria:
        raise ValueError("Código, nombre y categoría son obligatorios.")
    if productos["Codigo"].str.casefold().eq(codigo.casefold()).any():
        raise ValueError("El código del producto ya está registrado.")
    fila = pd.DataFrame([{"Codigo": codigo, "Nombre": nombre, "Seccion": str(seccion).strip(),
                         "Tipo": categoria, "Precio": _validar_precio(precio), "Estado": "Activo"}])
    guardar_inventario_administracion(pd.concat([productos, fila], ignore_index=True), existencias)
    return True


def _validar_precio(precio):
    try:
        resultado = float(precio)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("El precio debe ser numérico.") from error
    if not pd.notna(resultado) or resultado < 0 or resultado in (float("inf"), float("-inf")):
        raise ValueError("El precio debe ser un número igual o mayor que cero.")
    return resultado


def _validar_cantidad(cantidad):
    try:
        valor = float(cantidad)
        entero = int(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("La cantidad debe ser un entero igual o mayor que cero.") from error
    if valor != entero or entero < 0:
        raise ValueError("La cantidad debe ser un entero igual o mayor que cero.")
    return entero


def actualizar_producto(codigo, nombre=None, seccion=None, categoria=None, precio=None):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    clave = str(codigo).strip().casefold()
    filas = productos.index[productos["Codigo"].str.casefold() == clave]
    if len(filas) != 1:
        raise ValueError("No se encontró el código del producto.")
    indice = filas[0]
    for campo, valor in (("Nombre", nombre), ("Seccion", seccion), ("Tipo", categoria)):
        if valor is not None:
            productos.loc[indice, campo] = str(valor).strip()
    if precio is not None:
        productos.loc[indice, "Precio"] = _validar_precio(precio)
    guardar_inventario_administracion(productos, existencias)
    return True


def agregar_variante_existencias(codigo, talla, cantidad):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    codigo, talla = str(codigo).strip(), str(talla).strip()
    if not productos["Codigo"].str.casefold().eq(codigo.casefold()).any():
        raise ValueError("No existe un producto con ese código.")
    duplicado = (
        existencias["Codigo"].str.casefold().eq(codigo.casefold())
        & existencias["Talla"].str.casefold().eq(talla.casefold())
    )
    if duplicado.any():
        raise ValueError("Esa talla ya está registrada.")
    suma = pd.DataFrame([{"Codigo": codigo, "Talla": talla,
                              "Cantidad": _validar_cantidad(cantidad)}])
    guardar_inventario_administracion(productos, pd.concat([existencias, suma], ignore_index=True))
    return True


def actualizar_existencias(codigo, talla, cantidad):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    mascara = existencias["Codigo"].str.casefold().eq(str(codigo).strip().casefold()) & existencias["Talla"].str.casefold().eq(str(talla).strip().casefold())
    indices = existencias.index[mascara]
    if len(indices) != 1:
        raise ValueError("No existe esa combinación de producto y talla.")
    existencias.loc[indices[0], "Cantidad"] = _validar_cantidad(cantidad)
    guardar_inventario_administracion(productos, existencias)
    return True


def desactivar_producto(codigo):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    indices = productos.index[productos["Codigo"].str.casefold() == str(codigo).strip().casefold()]
    if len(indices) != 1:
        raise ValueError("No se encontró el código del producto.")
    productos.loc[indices[0], "Estado"] = "Inactivo"
    guardar_inventario_administracion(productos, existencias)
    return True
