
import os
import tempfile
import pandas as pd
from .rutas import ARCHIVO_FAVORITOS, DIRECTORIO_DATOS, ARCHIVO_ROPA
from .sesion import requerir_usuario
from .catalogo import cargar_catalogo_ropa


def _registros():
    if not ARCHIVO_FAVORITOS.exists():
        return []
    registros = []
    with ARCHIVO_FAVORITOS.open("r", encoding="utf-8", newline="") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) == 2 and all(campo.strip() for campo in campos):
                registros.append((campos[0].strip().casefold(), campos[1].strip()))
    return registros


def listar_favoritos(correo):
    correo = requerir_usuario(correo)
    codigos, vistos = [], set()
    for propietario, codigo in _registros():
        if propietario == correo and codigo.casefold() not in vistos:
            vistos.add(codigo.casefold())
            codigos.append(codigo)
    catalogo = {elemento["Codigo"].casefold(): elemento for elemento in cargar_catalogo_ropa()}
    inactivo = {}
    if ARCHIVO_ROPA.exists():
        productos = pd.read_excel(ARCHIVO_ROPA, sheet_name="Productos")
        if "Codigo" in productos and "Estado" in productos:
            for _, fila in productos.iterrows():
                codigo = str(fila.get("Codigo", "")).strip()
                estado = str(fila.get("Estado", "")).strip().casefold()
                if codigo and estado == "inactivo":
                    inactivo[codigo.casefold()] = str(fila.get("Nombre", ""))
    resultado = []
    for codigo in codigos:
        producto = catalogo.get(codigo.casefold())
        if producto:
            resultado.append({**producto, "EstadoFavorito": "Activo"})
        elif codigo.casefold() in inactivo:
            resultado.append({"Codigo": codigo, "Nombre": inactivo[codigo.casefold()], "EstadoFavorito": "Inactivo"})
        else:
            resultado.append({"Codigo": codigo, "Nombre": "", "EstadoFavorito": "No encontrado"})
    return resultado


def _escribir_cambios_usuario(lineas):
    descripcion, nombre_temporal = tempfile.mkstemp(prefix=".favoritos_", suffix=".tmp", dir=DIRECTORIO_DATOS)
    try:
        with os.fdopen(descripcion, "w", encoding="utf-8", newline="") as archivo:
            archivo.writelines(lineas)
        os.replace(nombre_temporal, ARCHIVO_FAVORITOS)
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise


def agregar_favorito(correo, codigo):
    correo = requerir_usuario(correo)
    codigo = str(codigo).strip()
    catalogo = cargar_catalogo_ropa()
    producto = next((producto_p for producto_p in catalogo if producto_p["Codigo"].casefold() == codigo.casefold()), None)
    if producto is None:
        raise ValueError("El producto no existe o está inactivo.")
    lineas = ARCHIVO_FAVORITOS.read_text(encoding="utf-8").splitlines(keepends=True) if ARCHIVO_FAVORITOS.exists() else []
    for linea in lineas:
        campos = linea.rstrip("\r\n").split("|")
        if len(campos) == 2 and campos[0].strip().casefold() == correo and campos[1].strip().casefold() == codigo.casefold():
            raise ValueError("Ese producto ya está en tus favoritos.")
    if lineas and not lineas[-1].endswith(("\n", "\r")):
        lineas[-1] += "\n"
    lineas.append(f"{correo}|{producto['Codigo']}\n")
    _escribir_cambios_usuario(lineas)
    return True


def eliminar_favorito(correo, codigo):
    correo = requerir_usuario(correo)
    codigo = str(codigo).strip().casefold()
    if not ARCHIVO_FAVORITOS.exists():
        return False
    lineas, eliminado = [], False
    with ARCHIVO_FAVORITOS.open("r", encoding="utf-8", newline="") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) == 2 and campos[0].strip().casefold() == correo and campos[1].strip().casefold() == codigo:
                eliminado = True
            else:
                lineas.append(linea)
    if eliminado:
        _escribir_cambios_usuario(lineas)
    return eliminado
