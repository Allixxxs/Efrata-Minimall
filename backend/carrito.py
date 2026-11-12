

import os
import tempfile
from .rutas import ARCHIVO_CARRITO, DIRECTORIO_DATOS
from .sesion import requerir_usuario
from .catalogo import cargar_catalogo_ropa


def normalizar_correo(correo):
    return requerir_usuario(correo)


def leer_carrito(correo):
    correo = requerir_usuario(correo)
    cantidades = {}
    if not ARCHIVO_CARRITO.exists():
        return []
    with ARCHIVO_CARRITO.open("r", encoding="utf-8", newline="") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) != 4 or campos[0].strip().casefold() != correo:
                continue
            try:
                cantidad = int(campos[3])
            except ValueError:
                continue
            if cantidad <= 0:
                continue
            clave = (campos[1].strip().upper(), campos[2].strip().upper())
            cantidades[clave] = cantidades.get(clave, 0) + cantidad
    return [{"Codigo": codigo, "Talla": talla, "Cantidad": cantidad}
            for (codigo, talla), cantidad in cantidades.items()]


def validar_cantidad(cantidad):
    try:
        valor = float(cantidad)
        entero = int(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("La cantidad debe ser un número entero positivo.") from error
    if valor != entero or entero <= 0:
        raise ValueError("La cantidad debe ser un número entero positivo.")
    return entero


def guardar_carrito(correo, articulos):
    correo = requerir_usuario(correo)
    conservado = []
    if ARCHIVO_CARRITO.exists():
        with ARCHIVO_CARRITO.open("r", encoding="utf-8", newline="") as archivo:
            for linea in archivo:
                campos = linea.rstrip("\r\n").split("|")
                linea_propia_valida = False
                if len(campos) == 4:
                    try:
                        linea_propia_valida = campos[0].strip().casefold() == correo and int(campos[3]) > 0
                    except ValueError:
                        pass
                if not linea_propia_valida:
                    conservado.append(linea if linea.endswith(("\n", "\r")) else linea + "\n")
    for elemento in articulos:
        cantidad = int(elemento["Cantidad"])
        if cantidad > 0:
            codigo, talla = elemento["Codigo"].strip().upper(), elemento["Talla"].strip().upper()
            if any(caracter in valor for valor in (codigo, talla) for caracter in "|\r\n"):
                raise ValueError("El código y la talla no pueden contener separadores.")
            conservado.append(f"{correo}|{codigo}|{talla}|{cantidad}\n")
    descripcion, nombre_temporal = tempfile.mkstemp(prefix=".carrito_", suffix=".tmp", dir=DIRECTORIO_DATOS)
    try:
        with os.fdopen(descripcion, "w", encoding="utf-8", newline="") as archivo:
            archivo.writelines(conservado)
        os.replace(nombre_temporal, ARCHIVO_CARRITO)
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise


def obtener_variante(catalogo, codigo, talla):
    codigo, talla = str(codigo).strip().upper(), str(talla).strip().upper()
    for producto in catalogo:
        if producto["Codigo"].strip().upper() == codigo:
            for variante in producto["Tallas"]:
                if variante["Talla"].strip().upper() == talla:
                    return producto, variante
            return producto, None
    return None, None


def agregar_al_carrito(correo, codigo, talla, cantidad, catalogo=None):
    correo, cantidad = requerir_usuario(correo), validar_cantidad(cantidad)
    catalogo = cargar_catalogo_ropa() if catalogo is None else catalogo
    producto, variante = obtener_variante(catalogo, codigo, talla)
    if producto is None:
        raise ValueError("El producto no existe o está inactivo.")
    if variante is None:
        raise ValueError("La talla no está disponible para este producto.")
    articulos = leer_carrito(correo)
    codigo, talla = producto["Codigo"].strip().upper(), variante["Talla"].strip().upper()
    actual = next((elemento_x for elemento_x in articulos if elemento_x["Codigo"] == codigo and elemento_x["Talla"] == talla), None)
    nueva_cantidad = (actual["Cantidad"] if actual else 0) + cantidad
    if nueva_cantidad > variante["Cantidad"]:
        raise ValueError(f"Solo hay {variante['Cantidad']} unidades disponibles de {producto['Nombre']} talla {talla}.")
    if actual:
        actual["Cantidad"] = nueva_cantidad
    else:
        articulos.append({"Codigo": codigo, "Talla": talla, "Cantidad": nueva_cantidad})
    guardar_carrito(correo, articulos)
    return nueva_cantidad


def actualizar_cantidad_carrito(correo, codigo, talla, cantidad, catalogo=None):
    correo, cantidad = requerir_usuario(correo), validar_cantidad(cantidad)
    catalogo = cargar_catalogo_ropa() if catalogo is None else catalogo
    producto, variante = obtener_variante(catalogo, codigo, talla)
    if producto is None:
        raise ValueError("El producto no existe o está inactivo.")
    if variante is None:
        raise ValueError("La talla no está disponible para este producto.")
    if cantidad > variante["Cantidad"]:
        raise ValueError(f"Solo hay {variante['Cantidad']} unidades disponibles de {producto['Nombre']} talla {variante['Talla']}.")
    articulos = leer_carrito(correo)
    elemento = next((elemento_x for elemento_x in articulos if elemento_x["Codigo"] == producto["Codigo"].upper()
                 and elemento_x["Talla"] == variante["Talla"].upper()), None)
    if elemento is None:
        raise ValueError("Esa variante no está en tu carrito.")
    elemento["Cantidad"] = cantidad
    guardar_carrito(correo, articulos)
    return cantidad


def eliminar_del_carrito(correo, codigo, talla):
    correo = requerir_usuario(correo)
    clave = (str(codigo).strip().upper(), str(talla).strip().upper())
    articulos = leer_carrito(correo)
    restante = [elemento_x for elemento_x in articulos if (elemento_x["Codigo"], elemento_x["Talla"]) != clave]
    if len(restante) == len(articulos):
        return False
    guardar_carrito(correo, restante)
    return True


def obtener_detalles_carrito(correo, catalogo=None):
    correo = requerir_usuario(correo)
    catalogo = cargar_catalogo_ropa() if catalogo is None else catalogo
    detalles = []
    for elemento in leer_carrito(correo):
        producto, variante = obtener_variante(catalogo, elemento["Codigo"], elemento["Talla"])
        if producto is None:
            detalles.append({**elemento, "Nombre": "Producto no disponible", "Precio": None,
                            "Subtotal": None, "StockActual": None,
                            "Aviso": "El producto ya no está activo o no existe en el catálogo."})
        elif variante is None:
            detalles.append({**elemento, "Nombre": producto["Nombre"], "Precio": producto["Precio"],
                            "Subtotal": producto["Precio"] * elemento["Cantidad"], "StockActual": 0,
                            "Aviso": "La talla ya no está registrada en el inventario."})
        else:
            existencias = variante["Cantidad"]
            aviso = (f"La existencia cambió: quedan {existencias} unidades. El artículo se conserva en el carrito."
                      if elemento["Cantidad"] > existencias else "")
            detalles.append({**elemento, "Nombre": producto["Nombre"], "Precio": producto["Precio"],
                            "Subtotal": producto["Precio"] * elemento["Cantidad"], "StockActual": existencias,
                            "Aviso": aviso})
    return detalles
