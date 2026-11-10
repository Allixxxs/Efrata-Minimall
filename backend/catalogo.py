"""Lectura, validación y filtrado de los dos inventarios Excel."""

import math
import os
import tempfile
import pandas as pd
from .rutas import (
    ARCHIVO_ROPA, ARCHIVO_INVENTARIO_TRAJES, ARCHIVO_CONSULTA_DISPONIBILIDAD, DIRECTORIO_DATOS,
)

COLUMNAS_PRODUCTOS = ["Codigo", "Nombre", "Seccion", "Tipo", "Precio", "Estado"]
COLUMNAS_EXISTENCIAS = ["Codigo", "Talla", "Cantidad"]


def crear_libro_ropa_vacio():
    """Crea solo la plantilla vacía, y únicamente cuando el catálogo la necesita."""
    if ARCHIVO_ROPA.exists():
        return False
    with pd.ExcelWriter(ARCHIVO_ROPA, engine="openpyxl") as escritor:
        pd.DataFrame(columns=COLUMNAS_PRODUCTOS).to_excel(
            escritor, sheet_name="Productos", index=False
        )
        pd.DataFrame(columns=COLUMNAS_EXISTENCIAS).to_excel(
            escritor, sheet_name="Existencias", index=False
        )
    return True


def validar_inventario(productos, existencias):
    productos_faltantes = [caracter_c for caracter_c in COLUMNAS_PRODUCTOS if caracter_c not in productos.columns]
    existencias_faltantes = [caracter_c for caracter_c in COLUMNAS_EXISTENCIAS if caracter_c not in existencias.columns]
    if productos_faltantes or existencias_faltantes:
        raise ValueError("ropa.xlsx no tiene los encabezados requeridos en ambas hojas.")
    if "Descripcion" not in productos.columns:
        productos["Descripcion"] = None
    productos = productos[COLUMNAS_PRODUCTOS + ["Descripcion"]].dropna(how="all").copy()
    for columna in ("Codigo", "Nombre", "Seccion", "Tipo", "Descripcion", "Estado"):
        productos[columna] = productos[columna].fillna("").astype(str).str.strip()
    productos["_key"] = productos["Codigo"].str.casefold()
    if (productos["_key"] == "").any() or productos["_key"].duplicated().any():
        raise ValueError("Cada producto debe tener un código único.")
    for columna in ("Codigo", "Nombre", "Seccion", "Tipo", "Descripcion", "Estado"):
        if productos[columna].str.contains(r"[|\r\n]", regex=True).any():
            raise ValueError(f"{columna} no puede contener | ni saltos de línea.")
    if (productos["Nombre"] == "").any() or (productos["Tipo"] == "").any():
        raise ValueError("Cada producto debe tener nombre y categoría.")
    secciones = {"mujer": "Mujer", "hombre": "Hombre", "unisex": "Unisex"}
    productos["Seccion"] = productos["Seccion"].str.casefold().map(secciones)
    estados = {"activo": "Activo", "inactivo": "Inactivo"}
    productos["Estado"] = productos["Estado"].str.casefold().map(estados)
    if productos["Seccion"].isna().any() or productos["Estado"].isna().any():
        raise ValueError("La sección o el estado de un producto no son válidos.")
    productos["Precio"] = pd.to_numeric(productos["Precio"], errors="coerce")
    precio_invalido = productos["Precio"].map(
        lambda elemento_x: pd.isna(elemento_x) or not math.isfinite(float(elemento_x)) or elemento_x < 0
    )
    if precio_invalido.any():
        raise ValueError("El precio debe ser un número igual o mayor que cero.")

    for columna in ("Codigo", "Talla"):
        existencias[columna] = existencias[columna].fillna("").astype(str).str.strip()
    for columna in ("Codigo", "Talla"):
        if existencias[columna].str.contains(r"[|\r\n]", regex=True).any():
            raise ValueError(f"{columna} no puede contener | ni saltos de línea.")
    existencias["_code_key"] = existencias["Codigo"].str.casefold()
    existencias["_size_key"] = existencias["Talla"].str.casefold()
    if (existencias["_code_key"] == "").any() or (existencias["_size_key"] == "").any():
        raise ValueError("Cada existencia debe tener código y talla.")
    if existencias.duplicated(["_code_key", "_size_key"]).any():
        raise ValueError("La combinación de código y talla debe ser única.")
    desconocido = set(existencias["_code_key"]) - set(productos["_key"])
    if desconocido:
        raise ValueError("Hay existencias asociadas a productos inexistentes.")
    existencias["Cantidad"] = pd.to_numeric(existencias["Cantidad"], errors="coerce")
    cantidad_invalida = existencias["Cantidad"].map(
        lambda elemento_x: pd.isna(elemento_x) or not math.isfinite(float(elemento_x)) or elemento_x < 0 or elemento_x % 1 != 0
    )
    if cantidad_invalida.any():
        raise ValueError("Las cantidades deben ser enteros iguales o mayores que cero.")
    existencias["Cantidad"] = existencias["Cantidad"].astype(int)
    return productos[COLUMNAS_PRODUCTOS + ["Descripcion"]].reset_index(drop=True), existencias[COLUMNAS_EXISTENCIAS].reset_index(drop=True)

def validar_catalogo_ropa(productos, existencias):
    productos, existencias = validar_inventario(productos, existencias)
    existencias_por_codigo = {}
    for _, fila in existencias.iterrows():
        existencias_por_codigo.setdefault(str(fila["Codigo"]).casefold(), []).append({
            "Talla": fila["Talla"], "Cantidad": int(fila["Cantidad"]),
        })
    resultado = []
    for _, fila in productos[productos["Estado"] == "Activo"].iterrows():
        tallas = existencias_por_codigo.get(str(fila["Codigo"]).casefold(), [])
        resultado.append({
            "Codigo": fila["Codigo"], "Nombre": fila["Nombre"],
            "Seccion": fila["Seccion"], "Tipo": fila["Tipo"],
            "Precio": float(fila["Precio"]), "Tallas": tallas,
            "Disponibilidad": "Disponible" if any(elemento_s["Cantidad"] > 0 for elemento_s in tallas) else "Agotado",
            "Descripcion": fila["Descripcion"],
        })
    return resultado


def cargar_catalogo_ropa():
    if not ARCHIVO_ROPA.exists():
        crear_libro_ropa_vacio()
    try:
        productos = pd.read_excel(ARCHIVO_ROPA, sheet_name="Productos")
        existencias = pd.read_excel(ARCHIVO_ROPA, sheet_name="Existencias")
    except (ValueError, OSError, ImportError) as error:
        raise ValueError("No se pudo leer ropa.xlsx o faltan sus hojas.") from error
    return validar_catalogo_ropa(productos, existencias)


def filtrar_catalogo_ropa(catalogo, seccion=None, categoria=None):
    return [
        producto for producto in catalogo
        if (not seccion or producto["Seccion"].casefold() == seccion.casefold())
        and (not categoria or producto["Tipo"].casefold() == categoria.casefold())
    ]


def cargar_trajes():
    if not ARCHIVO_INVENTARIO_TRAJES.exists():
        raise FileNotFoundError(f"No se encontró el inventario de trajes: {ARCHIVO_INVENTARIO_TRAJES.name}")
    marco = pd.read_excel(ARCHIVO_INVENTARIO_TRAJES)
    requerido = ["Codigo", "Nombre", "Tallas", "Precio", "Estado"]
    if any(columna not in marco.columns for columna in requerido):
        raise ValueError("inventario.xlsx no tiene los encabezados de trajes requeridos.")
    return [[str(fila[0]), fila[1], fila[2], int(fila[3]), fila[4]] for fila in marco[requerido].values]

def cargar_descripciones_trajes():
    """Devuelve un diccionario {codigo: descripcion} de los trajes."""
    if not ARCHIVO_INVENTARIO_TRAJES.exists():
        return {}
    marco = pd.read_excel(ARCHIVO_INVENTARIO_TRAJES)
    if "Descripcion" not in marco.columns:
        return {}
    descripciones = {}
    for _, fila in marco.iterrows():
        descripcion = fila["Descripcion"]
        if pd.isna(descripcion):
            descripcion = ""
        descripciones[str(fila["Codigo"])] = str(descripcion).strip()
    return descripciones

def guardar_trajes(trajes):
    marco = pd.DataFrame(trajes, columns=["Codigo", "Nombre", "Tallas", "Precio", "Estado"])
    descripcion, nombre_temporal = tempfile.mkstemp(prefix=".inventario_", suffix=".xlsx", dir=DIRECTORIO_DATOS)
    os.close(descripcion)
    try:
        marco.to_excel(nombre_temporal, index=False)
        os.replace(nombre_temporal, ARCHIVO_INVENTARIO_TRAJES)
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise


def actualizar_disponibilidad_traje():
    filas = cargar_trajes()
    with ARCHIVO_CONSULTA_DISPONIBILIDAD.open("w", encoding="utf-8") as archivo:
        for traje in filas:
            archivo.write(f"{traje[0]}|{traje[1]}|{traje[4]}\n")
    return True
