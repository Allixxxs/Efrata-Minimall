import os
import tempfile
import pandas as pd
from .rutas import (
    ARCHIVO_ADMINISTRADORES, ARCHIVO_ROPA, ARCHIVO_USUARIOS,
    ARCHIVO_DATOS_PERSONALES, ARCHIVO_COMPRAS, ARCHIVO_ALQUILERES,
    ARCHIVO_INVENTARIO_TRAJES, DIRECTORIO_DATOS,
)
from .sesion import sesion_actual
from .catalogo import validar_inventario, validar_trajes, guardar_trajes


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


def registrar_producto(codigo, nombre, seccion, categoria, precio, descripcion="", estado="Activo"):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    codigo = str(codigo).strip().upper()
    nombre, categoria = str(nombre).strip(), str(categoria).strip()
    if not codigo or not nombre or not categoria:
        raise ValueError("Código, nombre y categoría son obligatorios.")
    if productos["Codigo"].str.casefold().eq(codigo.casefold()).any():
        raise ValueError("El código del producto ya está registrado.")
    fila = pd.DataFrame([{
        "Codigo": codigo, "Nombre": nombre, "Seccion": str(seccion).strip(),
        "Tipo": categoria, "Precio": _validar_precio(precio),
        "Estado": str(estado).strip(), "Descripcion": str(descripcion).strip(),
    }])
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


def _normalizar_talla(talla):
    return str(talla).strip().upper()


def actualizar_producto(codigo, nombre=None, seccion=None, categoria=None,
                        precio=None, descripcion=None, estado=None):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    clave = str(codigo).strip().upper().casefold()
    filas = productos.index[productos["Codigo"].str.casefold() == clave]
    if len(filas) != 1:
        raise ValueError("No se encontró el código del producto.")
    indice = filas[0]
    for campo, valor in (
        ("Nombre", nombre), ("Seccion", seccion), ("Tipo", categoria),
        ("Descripcion", descripcion), ("Estado", estado),
    ):
        if valor is not None:
            productos.loc[indice, campo] = str(valor).strip()
    if precio is not None:
        productos.loc[indice, "Precio"] = _validar_precio(precio)
    guardar_inventario_administracion(productos, existencias)
    return True


def agregar_variante_existencias(codigo, talla, cantidad):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    codigo, talla = str(codigo).strip().upper(), _normalizar_talla(talla)
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
    talla = _normalizar_talla(talla)
    mascara = existencias["Codigo"].str.casefold().eq(str(codigo).strip().upper().casefold()) & existencias["Talla"].str.casefold().eq(talla.casefold())
    indices = existencias.index[mascara]
    if len(indices) != 1:
        raise ValueError("No existe esa combinación de producto y talla.")
    existencias.loc[indices[0], "Talla"] = talla
    existencias.loc[indices[0], "Cantidad"] = _validar_cantidad(cantidad)
    guardar_inventario_administracion(productos, existencias)
    return True


def desactivar_producto(codigo):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    indices = productos.index[productos["Codigo"].str.casefold() == str(codigo).strip().upper().casefold()]
    if len(indices) != 1:
        raise ValueError("No se encontró el código del producto.")
    productos.loc[indices[0], "Estado"] = "Inactivo"
    guardar_inventario_administracion(productos, existencias)
    return True


def cargar_trajes_administracion():
    _requerir_administrador()
    if not ARCHIVO_INVENTARIO_TRAJES.exists():
        raise FileNotFoundError("No se encontró inventario.xlsx.")
    try:
        return validar_trajes(pd.read_excel(ARCHIVO_INVENTARIO_TRAJES))
    except (OSError, ValueError, ImportError) as error:
        raise ValueError("No se pudo leer inventario.xlsx.") from error


def registrar_traje(codigo, nombre, precio, tallas, descripcion="", estado="Activo"):
    _requerir_administrador()
    trajes = cargar_trajes_administracion()
    nuevo = pd.DataFrame([{
        "Codigo": str(codigo).strip().upper(),
        "Nombre": str(nombre).strip(),
        "Tallas": str(tallas).strip(),
        "Precio": precio,
        "Estado": str(estado).strip(),
        "Descripcion": str(descripcion).strip(),
    }])
    validar_trajes(pd.concat([trajes, nuevo], ignore_index=True))
    guardar_trajes(pd.concat([trajes, nuevo], ignore_index=True))
    return True


def actualizar_traje(codigo, nombre, precio, tallas, descripcion="", estado="Activo"):
    _requerir_administrador()
    trajes = cargar_trajes_administracion()
    clave = str(codigo).strip().upper().casefold()
    indices = trajes.index[trajes["Codigo"].str.casefold() == clave]
    if len(indices) != 1:
        raise ValueError("No se encontró el código del traje.")
    indice = indices[0]
    trajes.loc[indice, "Nombre"] = str(nombre).strip()
    trajes.loc[indice, "Tallas"] = str(tallas).strip()
    trajes.loc[indice, "Precio"] = _validar_precio(precio)
    trajes.loc[indice, "Estado"] = str(estado).strip()
    trajes.loc[indice, "Descripcion"] = str(descripcion).strip()
    guardar_trajes(trajes)
    return True


def listar_clientes_administracion():
    """Devuelve un resumen de clientes sin exponer datos innecesarios."""
    _requerir_administrador()
    nombres = {}
    if ARCHIVO_DATOS_PERSONALES.exists():
        with ARCHIVO_DATOS_PERSONALES.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                campos = linea.rstrip("\r\n").split("|")
                if len(campos) >= 3 and campos[0].strip():
                    nombres[campos[0].strip().casefold()] = {
                        "Nombre": f"{campos[1].strip()} {campos[2].strip()}".strip()
                    }

    clientes = []
    if ARCHIVO_USUARIOS.exists():
        with ARCHIVO_USUARIOS.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                campos = linea.rstrip("\r\n").split("|")
                if len(campos) == 2 and campos[0].strip():
                    correo = campos[0].strip()
                    clientes.append({
                        "Correo": correo,
                        "Nombre": nombres.get(correo.casefold(), {}).get("Nombre", "Sin datos"),
                    })
    return clientes


def listar_compras_administracion():
    """Lee las compras registradas agrupadas por pedido."""
    _requerir_administrador()
    if not ARCHIVO_COMPRAS.exists():
        return []
    pedidos = {}
    with ARCHIVO_COMPRAS.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) != 11:
                continue
            try:
                articulo = {
                    "Codigo": campos[3], "Nombre": campos[4], "Talla": campos[5],
                    "Cantidad": int(campos[6]), "Subtotal": float(campos[8]),
                }
                total = float(campos[9])
            except (TypeError, ValueError):
                continue
            pedido = pedidos.setdefault(campos[0], {
                "Pedido": campos[0], "Correo": campos[1], "Fecha": campos[2],
                "Total": total, "Estado": campos[10], "Articulos": [],
            })
            pedido["Articulos"].append(articulo)
    return list(pedidos.values())


def listar_alquileres_administracion():
    """Devuelve alquileres y devoluciones registrados para consulta administrativa."""
    _requerir_administrador()
    if not ARCHIVO_ALQUILERES.exists():
        return []
    alquileres = []
    with ARCHIVO_ALQUILERES.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) not in {8, 10}:
                continue
            alquileres.append({
                "Correo": campos[0], "Codigo": campos[1], "Nombre": campos[2],
                "Talla": campos[3], "FechaAlquiler": campos[4],
                "FechaProgramada": campos[5], "Estado": campos[6],
                "Precio": campos[7], "FechaReal": campos[9] if len(campos) == 10 else "",
            })
    return alquileres


def obtener_estadisticas_administracion():
    """Calcula indicadores únicamente a partir de los registros existentes."""
    _requerir_administrador()
    compras = listar_compras_administracion()
    alquileres = listar_alquileres_administracion()
    clientes = listar_clientes_administracion()
    productos, existencias = cargar_inventario_administracion()
    trajes = pd.read_excel(ARCHIVO_INVENTARIO_TRAJES) if ARCHIVO_INVENTARIO_TRAJES.exists() else pd.DataFrame()

    unidades_vendidas = sum(
        articulo["Cantidad"] for pedido in compras for articulo in pedido["Articulos"]
    )
    ventas_simuladas = sum(pedido["Total"] for pedido in compras)
    inventario_disponible = int((existencias["Cantidad"] > 0).sum())
    inventario_agotado = int((existencias["Cantidad"] == 0).sum())
    return {
        "Clientes registrados": len(clientes),
        "Compras confirmadas": len(compras),
        "Unidades vendidas": unidades_vendidas,
        "Ventas simuladas": ventas_simuladas,
        "Alquileres registrados": len(alquileres),
        "Alquileres activos": sum(a["Estado"].casefold() == "activo" for a in alquileres),
        "Devoluciones": sum(a["Estado"].casefold() == "devuelto" for a in alquileres),
        "Productos activos": int((productos["Estado"] == "Activo").sum()),
        "Variantes disponibles": inventario_disponible,
        "Variantes agotadas": inventario_agotado,
        "Trajes activos": int((trajes["Estado"] == "Activo").sum()) if "Estado" in trajes else 0,
    }
