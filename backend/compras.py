"""Preparación, confirmación e historial de compras."""

import datetime
import os
import tempfile
import uuid
from pathlib import Path
from openpyxl import load_workbook
from .rutas import (
    ARCHIVO_ROPA, ARCHIVO_COMPRAS, ARCHIVO_CARRITO, DIRECTORIO_COMPROBANTES, DIRECTORIO_DATOS,
)
from .sesion import requerir_usuario
from .carrito import leer_carrito, validar_cantidad
from .catalogo import cargar_catalogo_ropa


def preparar_compra(correo):
    correo = requerir_usuario(correo)
    carrito = leer_carrito(correo)
    if not carrito:
        return [], 0.0, "Tu carrito está vacío."
    catalogo = cargar_catalogo_ropa()
    detalles, total, errores = [], 0.0, []
    for elemento in carrito:
        producto = next((producto_p for producto_p in catalogo if producto_p["Codigo"].casefold() == elemento["Codigo"].casefold()), None)
        if producto is None:
            errores.append(f"{elemento['Codigo']}: producto inexistente o inactivo.")
            continue
        variante = next((elemento_v for elemento_v in producto["Tallas"] if elemento_v["Talla"].casefold() == elemento["Talla"].casefold()), None)
        if variante is None:
            errores.append(f"{elemento['Codigo']} talla {elemento['Talla']}: talla inexistente.")
            continue
        cantidad = validar_cantidad(elemento["Cantidad"])
        if cantidad > variante["Cantidad"]:
            errores.append(f"{producto['Nombre']} talla {variante['Talla']}: solicitas {cantidad}, hay {variante['Cantidad']}.")
            continue
        precio = float(producto["Precio"])
        subtotal = precio * cantidad
        detalles.append({"Codigo": producto["Codigo"].upper(), "Nombre": str(producto["Nombre"]),
                        "Talla": variante["Talla"].upper(), "Cantidad": cantidad,
                        "Precio": precio, "Subtotal": subtotal})
        total += subtotal
    if errores:
        return [], 0.0, "Compra cancelada; no se modificó ningún archivo. " + " ".join(errores)
    return detalles, total, ""


def _preparar_inventario(reducciones):
    libro = load_workbook(ARCHIVO_ROPA)
    try:
        if "Existencias" not in libro.sheetnames:
            raise ValueError("No existe la hoja Existencias.")
        hoja = libro["Existencias"]
        encabezados = {str(hoja.cell(1, columna).value).strip(): columna
                   for columna in range(1, hoja.max_column + 1)
                   if hoja.cell(1, columna).value is not None}
        if not {"Codigo", "Talla", "Cantidad"}.issubset(encabezados):
            raise ValueError("Columnas inválidas en Existencias.")
        for (codigo, talla), cantidad_solicitada in reducciones.items():
            filas = [registro_r for registro_r in range(2, hoja.max_row + 1)
                    if str(hoja.cell(registro_r, encabezados["Codigo"]).value).strip().upper() == codigo
                    and str(hoja.cell(registro_r, encabezados["Talla"]).value).strip().upper() == talla]
            if len(filas) != 1:
                raise ValueError(f"Variante duplicada o inexistente: {codigo} talla {talla}.")
            fila = filas[0]
            bruto = hoja.cell(fila, encabezados["Cantidad"]).value
            try:
                cantidad_existente = int(bruto)
                if float(bruto) != cantidad_existente or cantidad_existente < cantidad_solicitada:
                    raise ValueError
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError(f"Existencias insuficientes o inválidas: {codigo} talla {talla}.") from error
            hoja.cell(fila, encabezados["Cantidad"]).value = cantidad_existente - cantidad_solicitada
        descripcion, nombre_temporal = tempfile.mkstemp(prefix=".ropa_pedido_", suffix=".xlsx", dir=DIRECTORIO_DATOS)
        os.close(descripcion)
        try:
            libro.save(nombre_temporal)
            return nombre_temporal
        except Exception:
            if os.path.exists(nombre_temporal):
                os.remove(nombre_temporal)
            raise
    finally:
        libro.close()


def _lineas_pedido(id_pedido, correo, fecha, detalles, total):
    lineas = []
    for elemento in detalles:
        nombre = str(elemento["Nombre"]).replace("|", "/").replace("\r", " ").replace("\n", " ")
        lineas.append("|".join((id_pedido, correo, fecha, elemento["Codigo"], nombre,
                               elemento["Talla"], str(elemento["Cantidad"]),
                               f"{elemento['Precio']:.2f}", f"{elemento['Subtotal']:.2f}",
                               f"{total:.2f}", "Confirmada")) + "\n")
    return lineas


def _comprobante(id_pedido, correo, fecha, detalles, total):
    lineas = ["COMPROBANTE DE COMPRA - EFRATA MINI-MALL", f"Pedido: {id_pedido}",
             f"Fecha: {fecha}", f"Correo: {correo}", "", "ARTÍCULOS:"]
    for elemento in detalles:
        lineas.append(f"{elemento['Nombre']} | Código: {elemento['Codigo']} | Talla: {elemento['Talla']} | "
                     f"Cantidad: {elemento['Cantidad']} | Precio unitario: ${elemento['Precio']:,.2f} | "
                     f"Subtotal: ${elemento['Subtotal']:,.2f}")
    lineas.extend(["", f"TOTAL: ${total:,.2f}", "Compra simulada; no se procesó ningún pago."])
    return "\n".join(lineas) + "\n"


def _bytes_temporales(contenido, prefijo):
    descripcion, nombre_temporal = tempfile.mkstemp(prefix=prefijo, suffix=".tmp", dir=DIRECTORIO_DATOS)
    try:
        with os.fdopen(descripcion, "wb") as archivo:
            archivo.write(contenido)
        return nombre_temporal
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise


def _carrito_sin_usuario(correo):
    if not ARCHIVO_CARRITO.exists():
        return b""
    lineas = []
    with ARCHIVO_CARRITO.open("r", encoding="utf-8", newline="") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            propio = False
            if len(campos) == 4 and campos[0].strip().casefold() == correo:
                try:
                    propio = int(campos[3]) > 0
                except ValueError:
                    pass
            if not propio:
                lineas.append(linea if linea.endswith(("\n", "\r")) else linea + "\n")
    return "".join(lineas).encode("utf-8")


def _restaurar_archivo(ruta, existia, contenido):
    if not existia:
        if ruta.exists():
            ruta.unlink()
        return
    descripcion, nombre_temporal = tempfile.mkstemp(prefix=".compra_restaurar_", suffix=".tmp", dir=DIRECTORIO_DATOS)
    try:
        with os.fdopen(descripcion, "wb") as archivo:
            archivo.write(contenido)
        os.replace(nombre_temporal, ruta)
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise


def _nuevo_id_pedido():
    while True:
        id_pedido = datetime.datetime.now().strftime("PED-%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8].upper()
        comprobante = DIRECTORIO_COMPROBANTES / f"{id_pedido}.txt"
        usado = False
        if ARCHIVO_COMPRAS.exists():
            with ARCHIVO_COMPRAS.open("r", encoding="utf-8") as archivo:
                usado = any(linea.split("|", 1)[0] == id_pedido for linea in archivo)
        if not usado and not comprobante.exists():
            return id_pedido, comprobante


def confirmar_compra(correo, confirmado, fecha_hora=None):
    correo = requerir_usuario(correo)
    detalles, total, error = preparar_compra(correo)
    if error:
        return {"ok": False, "message": error, "details": [], "total": 0.0}
    if not confirmado:
        return {"ok": False, "message": "Compra cancelada. El carrito y las existencias no cambiaron.",
                "details": detalles, "total": total}
    detalles_actuales, total_actual, error = preparar_compra(correo)
    if error:
        return {"ok": False, "message": error, "details": [], "total": 0.0}
    if detalles_actuales != detalles or total_actual != total:
        return {"ok": False, "message": "El carrito, el precio o las existencias cambiaron durante la confirmación.",
                "details": detalles_actuales, "total": total_actual}
    detalles, total = detalles_actuales, total_actual
    marca_temporal = fecha_hora or datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    id_pedido, ruta_comprobante = _nuevo_id_pedido()
    rutas_archivos = {"inventario": ARCHIVO_ROPA, "compras": ARCHIVO_COMPRAS, "carrito": ARCHIVO_CARRITO}
    copias_respaldo = {}
    try:
        for nombre, ruta in rutas_archivos.items():
            copias_respaldo[nombre] = (ruta.exists(), ruta.read_bytes() if ruta.exists() else b"")
    except OSError as error:
        return {"ok": False, "message": f"No se pudieron respaldar los archivos: {error}", "details": detalles, "total": total}

    temporales, comprobante_creado = [], False
    try:
        reducciones = {}
        for elemento in detalles:
            clave = (elemento["Codigo"], elemento["Talla"])
            reducciones[clave] = reducciones.get(clave, 0) + elemento["Cantidad"]
        excel_temporal = _preparar_inventario(reducciones)
        temporales.append(excel_temporal)
        pedidos_anteriores = copias_respaldo["compras"][1]
        if pedidos_anteriores and not pedidos_anteriores.endswith((b"\n", b"\r")):
            pedidos_anteriores += b"\n"
        pedidos_temporales = _bytes_temporales(pedidos_anteriores + "".join(
            _lineas_pedido(id_pedido, correo, marca_temporal, detalles, total)
        ).encode("utf-8"), ".compras_pedido_")
        temporales.append(pedidos_temporales)
        carrito_temporal = _bytes_temporales(_carrito_sin_usuario(correo), ".carrito_pedido_")
        temporales.append(carrito_temporal)
        DIRECTORIO_COMPROBANTES.mkdir(parents=True, exist_ok=True)
        with ruta_comprobante.open("x", encoding="utf-8") as archivo:
            comprobante_creado = True
            archivo.write(_comprobante(id_pedido, correo, marca_temporal, detalles, total))
        for clave, nombre_temporal in (("compras", pedidos_temporales), ("inventario", excel_temporal), ("carrito", carrito_temporal)):
            os.replace(nombre_temporal, rutas_archivos[clave])
            temporales.remove(nombre_temporal)
    except Exception as error:
        errores_restauracion = []
        for nombre, ruta in rutas_archivos.items():
            existia, contenido = copias_respaldo[nombre]
            try:
                _restaurar_archivo(ruta, existia, contenido)
            except Exception as error_restauracion:
                errores_restauracion.append(f"{ruta.name}: {error_restauracion}")
        if comprobante_creado:
            try:
                ruta_comprobante.unlink(missing_ok=True)
            except OSError as error_comprobante:
                errores_restauracion.append(f"{ruta_comprobante.name}: {error_comprobante}")
        for nombre_temporal in temporales:
            try:
                Path(nombre_temporal).unlink(missing_ok=True)
            except OSError:
                pass
        sufijo = " No se pudo restaurar: " + "; ".join(errores_restauracion) if errores_restauracion else " Se restauraron los archivos anteriores."
        return {"ok": False, "message": f"No se completó la compra: {error}.{sufijo}",
                "details": detalles, "total": total}
    return {"ok": True, "message": "Compra confirmada.", "pedido": id_pedido,
            "comprobante": str(ruta_comprobante), "details": detalles, "total": total}


def listar_compras(correo):
    correo = requerir_usuario(correo)
    if not ARCHIVO_COMPRAS.exists():
        return []
    pedidos = {}
    with ARCHIVO_COMPRAS.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) != 11 or campos[1].strip().casefold() != correo:
                continue
            try:
                elemento = {"Codigo": campos[3], "Nombre": campos[4], "Talla": campos[5],
                        "Cantidad": int(campos[6]), "Precio": float(campos[7]),
                        "Subtotal": float(campos[8]), "Estado": campos[10]}
                total = float(campos[9])
            except (ValueError, TypeError):
                continue
            pedido = pedidos.setdefault(campos[0], {"Pedido": campos[0], "Fecha": campos[2],
                                                  "Total": total, "Articulos": []})
            pedido["Articulos"].append(elemento)
    return list(pedidos.values())


def obtener_detalle_compra(correo, id_pedido):
    correo = requerir_usuario(correo)
    return next((pedido for pedido in listar_compras(correo)
                 if pedido["Pedido"].casefold() == str(id_pedido).strip().casefold()), None)
