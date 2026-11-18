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


def guardar_producto_completo(
    codigo, nombre, seccion, categoria, precio, descripcion, estado,
    tallas, codigo_original=None
):
    _requerir_administrador()
    productos, existencias = cargar_inventario_administracion()
    codigo = str(codigo).strip().upper()
    clave_original = str(codigo_original or codigo).strip().upper().casefold()
    filas_originales = productos.index[
        productos["Codigo"].str.casefold() == clave_original
    ]

    if codigo_original is None:
        if len(filas_originales) != 0:
            raise ValueError("El código del producto ya está registrado.")
        producto_nuevo = pd.DataFrame([{
            "Codigo": codigo, "Nombre": str(nombre).strip(),
            "Seccion": str(seccion).strip(), "Tipo": str(categoria).strip(),
            "Precio": _validar_precio(precio), "Estado": str(estado).strip(),
            "Descripcion": str(descripcion).strip(),
        }])
        productos = pd.concat([productos, producto_nuevo], ignore_index=True)
        clave_existencias = codigo.casefold()
    else:
        if len(filas_originales) != 1:
            raise ValueError("No se encontró el código del producto.")
        clave_nueva = codigo.casefold()
        if clave_nueva != clave_original and productos["Codigo"].str.casefold().eq(clave_nueva).any():
            raise ValueError("El código del producto ya está registrado.")
        indice = filas_originales[0]
        productos.loc[indice, "Codigo"] = codigo
        productos.loc[indice, "Nombre"] = str(nombre).strip()
        productos.loc[indice, "Seccion"] = str(seccion).strip()
        productos.loc[indice, "Tipo"] = str(categoria).strip()
        productos.loc[indice, "Precio"] = _validar_precio(precio)
        productos.loc[indice, "Estado"] = str(estado).strip()
        productos.loc[indice, "Descripcion"] = str(descripcion).strip()
        clave_existencias = clave_original

    tallas_nuevas = {}
    for talla, cantidad in tallas:
        talla_normalizada = _normalizar_talla(talla)
        clave_talla = talla_normalizada.casefold()
        if not talla_normalizada or clave_talla in tallas_nuevas:
            raise ValueError("Cada talla debe ser válida y aparecer una sola vez.")
        tallas_nuevas[clave_talla] = (
            talla_normalizada, _validar_cantidad(cantidad)
        )
    if not tallas_nuevas:
        raise ValueError("Debe registrarse al menos una talla.")

    indices_existencias = existencias.index[
        existencias["Codigo"].str.casefold() == clave_existencias
    ]
    tallas_actualizadas = set()
    for indice in indices_existencias:
        clave_talla = str(existencias.loc[indice, "Talla"]).strip().casefold()
        existencias.loc[indice, "Codigo"] = codigo
        if clave_talla in tallas_nuevas:
            talla_normalizada, cantidad = tallas_nuevas[clave_talla]
            existencias.loc[indice, "Talla"] = talla_normalizada
            existencias.loc[indice, "Cantidad"] = cantidad
            tallas_actualizadas.add(clave_talla)
        else:
            existencias.loc[indice, "Cantidad"] = 0

    nuevas_existencias = [
        {"Codigo": codigo, "Talla": talla, "Cantidad": cantidad}
        for clave_talla, (talla, cantidad) in tallas_nuevas.items()
        if clave_talla not in tallas_actualizadas
    ]
    if nuevas_existencias:
        existencias = pd.concat(
            [existencias, pd.DataFrame(nuevas_existencias)],
            ignore_index=True,
        )

    guardar_inventario_administracion(productos, existencias)
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

    administradores = set()
    if ARCHIVO_ADMINISTRADORES.exists():
        with ARCHIVO_ADMINISTRADORES.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                if linea.strip() and not linea.lstrip().startswith("#"):
                    administradores.add(linea.strip().casefold())

    clientes = []
    if ARCHIVO_USUARIOS.exists():
        with ARCHIVO_USUARIOS.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                campos = linea.rstrip("\r\n").split("|")
                if len(campos) == 2 and campos[0].strip():
                    correo = campos[0].strip()
                    if correo.casefold() in administradores:
                        continue
                    clientes.append({
                        "Correo": correo,
                        "Nombre": nombres.get(correo.casefold(), {}).get("Nombre", "Sin datos"),
                    })
    return clientes


def listar_compras_administracion():
    _requerir_administrador()
    if not ARCHIVO_COMPRAS.exists():
        return []
    pedidos = {}
    with ARCHIVO_COMPRAS.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) not in {11, 13}:
                continue
            try:
                articulo = {
                    "Codigo": campos[3], "Nombre": campos[4], "Talla": campos[5],
                    "Cantidad": int(campos[6]), "Subtotal": float(campos[8]),
                }
                total = float(campos[9])
            except (TypeError, ValueError):
                continue
            if len(campos) == 11:
                metodo_pago = "Método no registrado"
                estado_pago = "Pago anterior no registrado"
            else:
                metodo_pago = campos[11].strip() or "Método no registrado"
                estado_pago = campos[12].strip() or "Estado de pago no registrado"
            pedido = pedidos.setdefault(campos[0], {
                "Pedido": campos[0], "Correo": campos[1], "Fecha": campos[2],
                "Total": total, "Estado": campos[10],
                "MetodoPago": metodo_pago, "EstadoPago": estado_pago,
                "Articulos": [],
            })
            pedido["Articulos"].append(articulo)
    return list(pedidos.values())


def listar_alquileres_administracion():
    _requerir_administrador()
    if not ARCHIVO_ALQUILERES.exists():
        return []

    datos_personales = {}
    if ARCHIVO_DATOS_PERSONALES.exists():
        with ARCHIVO_DATOS_PERSONALES.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                campos = linea.rstrip("\r\n").split("|")
                if len(campos) != 8:
                    continue
                nombre = " ".join((campos[1].strip(), campos[2].strip())).strip()
                datos_personales[campos[0].strip().casefold()] = {
                    "Nombre": nombre,
                    "Telefono": campos[3].strip(),
                    "Direccion": campos[6].strip(),
                }

    alquileres = []
    with ARCHIVO_ALQUILERES.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) not in {8, 10, 12, 13}:
                continue
            perfil = datos_personales.get(campos[0].strip().casefold(), {})
            alquileres.append({
                "Correo": campos[0], "Codigo": campos[1], "Nombre": campos[2],
                "Talla": campos[3], "FechaAlquiler": campos[4],
                "FechaProgramada": campos[5], "Estado": campos[6],
                "Precio": campos[7], "FechaReal": campos[9] if len(campos) in {10, 12, 13} else "",
                "MetodoPago": campos[10] if len(campos) in {12, 13} else "Método no registrado",
                "EstadoPago": campos[11] if len(campos) in {12, 13} else "Pago anterior no registrado",
                "NombreCliente": perfil.get("Nombre") or "Dato no registrado",
                "TelefonoCliente": perfil.get("Telefono") or "Dato no registrado",
                "DireccionCliente": perfil.get("Direccion") or "Dato no registrado",
            })
    return alquileres


def obtener_estadisticas_administracion():
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
