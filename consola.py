import datetime
import getpass
import zipfile

from backend.sesion import sesion_actual, requerir_usuario
from backend.usuarios import (
    autenticar_usuario, cerrar_sesion, normalizar_correo, registrar_usuario,
    existe_usuario,
)
from backend.datos_personales import (
    leer_datos_personales, guardar_datos_personales, eliminar_datos_personales,
)
from backend.catalogo import (
    cargar_catalogo_ropa, filtrar_catalogo_ropa, cargar_trajes,
)
from backend.alquileres import (
    hay_conflicto_alquiler, obtener_alquileres_usuario, registrar_alquiler, devolver_alquiler,
)
from backend.carrito import (
    agregar_al_carrito, actualizar_cantidad_carrito, eliminar_del_carrito, obtener_detalles_carrito,
)
from backend.compras import (
    preparar_compra, confirmar_compra, listar_compras, obtener_detalle_compra,
)
from backend.administracion import (
    es_administrador, cargar_inventario_administracion, registrar_producto, actualizar_producto,
    agregar_variante_existencias, actualizar_existencias, desactivar_producto,
)
from backend.favoritos import listar_favoritos, agregar_favorito, eliminar_favorito


def inicio_consola():
    print("\n¡Bienvenidos a EFRATA MINI-MALL!")
    print("\nModa, alquiler de trajes y arreglos en un solo lugar")
    print("\nModa nacional e importada\nTrajes para toda ocasión\nArreglo de ropa\n")
    print("\nCali, Colombia\n3239655863")
    print("\n¡Será un placer atenderte!\n")


def _mostrar_ropa(productos):
    if not productos:
        print("No se encontraron prendas con esos filtros.")
        return
    print("\nCATÁLOGO DE ROPA")
    for producto in productos:
        tallas = ", ".join(
            f"{elemento_v['Talla']}: {elemento_v['Cantidad']} unidades ({'Disponible' if elemento_v['Cantidad'] else 'Agotado'})"
            for elemento_v in producto["Tallas"]
        ) or "Sin tallas registradas"
        print(
            f"\nCódigo: {producto['Codigo']}\nNombre: {producto['Nombre']}\n"
            f"Sección: {producto['Seccion']}\nCategoría: {producto['Tipo']}\n"
            f"Tallas y cantidades: {tallas}\nPrecio: ${producto['Precio']:,.0f}\n"
            f"Disponibilidad: {producto['Disponibilidad']}"
        )


def buscar():
    print("\nBUSCAR ROPA")
    try:
        catalogo = cargar_catalogo_ropa()
    except (ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
        print(f"No se pudo cargar el catálogo: {error}")
        return
    if not catalogo:
        print("El catálogo no tiene productos activos registrados.")
        return
    secciones = {"1": "Mujer", "2": "Hombre", "3": "Unisex"}
    while True:
        print("\n1. Mujer\n2. Hombre\n3. Unisex\n4. Todas las secciones\n5. Volver")
        seleccion = input("Seleccione una sección: ").strip()
        if seleccion == "5":
            return
        if seleccion not in {"1", "2", "3", "4"}:
            print("Opción inválida.")
            continue
        seccion = secciones.get(seleccion)
        productos_seccion = filtrar_catalogo_ropa(catalogo, seccion=seccion)
        if not productos_seccion:
            print("No hay productos activos para esa sección.")
            continue
        categorias = sorted({producto_p["Tipo"] for producto_p in productos_seccion}, key=str.casefold)
        print("\n0. Todas las categorías")
        for indice, categoria in enumerate(categorias, fecha_inicio=1):
            print(f"{indice}. {categoria}")
        volver = str(len(categorias) + 1)
        print(f"{volver}. Volver a secciones")
        opcion = input("Seleccione una categoría: ").strip()
        if opcion == volver:
            continue
        if opcion == "0":
            categoria = None
        elif opcion.isdigit() and 1 <= int(opcion) <= len(categorias):
            categoria = categorias[int(opcion) - 1]
        else:
            print("Opción inválida.")
            continue
        _mostrar_ropa(filtrar_catalogo_ropa(catalogo, seccion, categoria))
        return


def sesion():
    print("\nEFRATA MINI-MALL\nInicia sesión o crea tu cuenta")
    try:
        correo = normalizar_correo(input("Correo electrónico: "))
    except ValueError as error:
        print(error)
        return
    if existe_usuario(correo):
        contrasena = getpass.getpass("CONTRASEÑA: ")
        if not autenticar_usuario(correo, contrasena):
            print("La combinación de usuario y contraseña no es correcta.")
            return
        print("Inicio de sesión exitoso.")
    else:
        print(f"CREAR CUENTA\nCorreo electrónico: {correo}")
        while True:
            contrasena = getpass.getpass(
                "CONTRASEÑA (mínimo 8 caracteres, mayúscula, minúscula y número): "
            )
            try:
                registrar_usuario(correo, contrasena)
                break
            except ValueError as error:
                print(error)
        print("Cuenta creada exitosamente.")
    cuenta()


def _mostrar_datos_personales(datos):
    print("\nMIS DATOS PERSONALES")
    for etiqueta, clave in (("Nombre", "Nombre"), ("Apellidos", "Apellidos"),
                       ("Teléfono", "Telefono"), ("Tipo de documento", "TipoDocumento"),
                       ("Número de documento", "NumeroDocumento"),
                       ("Dirección", "Direccion"), ("Código postal", "CodigoPostal")):
        print(f"{etiqueta}: {datos[clave]}")


def mis_datos():
    try:
        correo = requerir_usuario()
    except PermissionError as error:
        print(error)
        return
    while True:
        datos = leer_datos_personales(correo)
        if datos is None:
            print("\nNo tienes datos personales registrados.\n1. Registrar mis datos\n2. Volver")
            opcion = input("Opción: ").strip()
            if opcion == "2":
                return
            if opcion != "1":
                print("Opción inválida.")
                continue
            actual = {}
        else:
            print("\n1. Consultar datos\n2. Modificar datos\n3. Eliminar datos\n4. Volver")
            opcion = input("Opción: ").strip()
            if opcion == "1":
                _mostrar_datos_personales(datos)
                continue
            if opcion == "3":
                if input("¿Deseas eliminar tus datos? (S/N): ").strip().upper() == "S":
                    eliminar_datos_personales(correo)
                    print("Datos personales eliminados.")
                else:
                    print("Eliminación cancelada.")
                continue
            if opcion == "4":
                return
            if opcion != "2":
                print("Opción inválida.")
                continue
            actual = datos
        etiquetas = (("Nombre", "Nombre"), ("Apellidos", "Apellidos"),
                  ("Telefono", "Teléfono (+57, 10 dígitos)"),
                  ("TipoDocumento", "Tipo de documento (CC, CE, NIT)"),
                  ("NumeroDocumento", "Número de documento"), ("Direccion", "Dirección"),
                  ("CodigoPostal", "Código postal (6 dígitos)"))
        valores = {}
        for clave, etiqueta in etiquetas:
            anterior = actual.get(clave, "")
            ingresado = input(f"{etiqueta}{f' [{anterior}]' if anterior else ''}: ").strip()
            valores[clave] = ingresado or anterior
        try:
            guardar_datos_personales(correo, valores)
            print("Datos personales guardados.")
        except (ValueError, OSError) as error:
            print(f"No se pudieron guardar los datos: {error}")


def mis_compras(correo=None, seleccion=None):
    try:
        correo = requerir_usuario(correo)
        pedidos = listar_compras(correo)
    except (PermissionError, OSError) as error:
        print(error)
        return
    if not pedidos:
        print("Aún no tienes compras registradas.")
        return
    for indice_i, pedido in enumerate(pedidos, 1):
        print(f"{indice_i}. Pedido: {pedido['Pedido']} | Fecha: {pedido['Fecha']} | Total: ${pedido['Total']:,.2f}")
    seleccion = (input("Número de compra o ID del pedido (Enter para volver): ").strip()
                 if seleccion is None else str(seleccion).strip())
    if not seleccion:
        return pedidos
    pedido = next((opcion_o for opcion_o in pedidos if opcion_o["Pedido"].casefold() == seleccion.casefold()), None)
    if pedido is None and seleccion.isdigit() and 1 <= int(seleccion) <= len(pedidos):
        pedido = pedidos[int(seleccion) - 1]
    if pedido is None:
        print("No se encontró ese pedido.")
        return pedidos
    print(f"\nDETALLE DEL PEDIDO {pedido['Pedido']}\nFecha: {pedido['Fecha']}")
    for elemento in pedido["Articulos"]:
        print(f"{elemento['Nombre']} | Código: {elemento['Codigo']} | Talla: {elemento['Talla']} | "
              f"Cantidad: {elemento['Cantidad']} | Precio: ${elemento['Precio']:,.2f} | "
              f"Subtotal: ${elemento['Subtotal']:,.2f}")
    print(f"Total: ${pedido['Total']:,.2f}")
    return pedidos


def interfaz_mis_compras():
    return mis_compras(sesion_actual.correo)


def cuenta():
    while True:
        print(f"\nBIENVENIDO, {sesion_actual.correo}\n\nMI CUENTA\n1. Mis compras\n2. Mis datos\n3. Cerrar sesión\n4. Salir")
        opcion = input("Ingrese una opción: ").strip()
        if opcion == "1":
            interfaz_mis_compras()
        elif opcion == "2":
            mis_datos()
        elif opcion == "3":
            cerrar_sesion()
            print("Sesión cerrada.")
            return
        elif opcion == "4":
            return
        else:
            print("Opción inválida.")


def _mostrar_trajes():
    trajes = cargar_trajes()
    if not trajes:
        print("No hay trajes registrados.")
    for traje in trajes:
        print(f"Código: {traje[0]} | Traje: {traje[1]} | Tallas: {traje[2]} | Precio: ${traje[3]:,}")


def consultar_alquileres():
    try:
        correo = requerir_usuario()
        alquileres = obtener_alquileres_usuario(correo)
    except (PermissionError, OSError) as error:
        print(error)
        return
    if not alquileres:
        print("No tienes alquileres registrados.")
        return
    print("\nMIS ALQUILERES")
    for posicion, alquiler in enumerate(alquileres, 1):
        print(f"{posicion}. {alquiler['Estado']} | {alquiler['Nombre']} | Código: {alquiler['Codigo']} | "
              f"Talla: {alquiler['Talla']} | Alquiler: {alquiler['FechaAlquiler']} | "
              f"Devolución programada: {alquiler['FechaProgramada']} | Precio: ${alquiler['Precio']}")
        if alquiler["FechaReal"]:
            print(f"   Fecha real de devolución: {alquiler['FechaReal']}")
    opcion = input("Número del alquiler para ver detalle (Enter para volver): ").strip()
    if opcion.isdigit() and 1 <= int(opcion) <= len(alquileres):
        alquiler = alquileres[int(opcion) - 1]
        print(f"\nDETALLE: {alquiler['Nombre']} ({alquiler['Codigo']}) | Talla {alquiler['Talla']} | "
              f"Alquiler {alquiler['FechaAlquiler']} | Programada {alquiler['FechaProgramada']} | "
              f"Precio ${alquiler['Precio']} | Estado {alquiler['Estado']} | "
              f"Real {alquiler['FechaReal'] or 'Pendiente/no registrada'} | ID {alquiler['Id'] or 'histórico'}")
    elif opcion:
        print("Selección inválida.")


def devolver_traje():
    try:
        correo = requerir_usuario()
        activa = [registro_r for registro_r in obtener_alquileres_usuario(correo) if registro_r["Estado"].casefold() == "activo"]
    except (PermissionError, OSError) as error:
        print(error)
        return
    if not activa:
        print("No tienes alquileres pendientes de devolución.")
        return
    for indice_i, elemento in enumerate(activa, 1):
        print(f"{indice_i}. Código: {elemento['Codigo']} | Traje: {elemento['Nombre']} | Talla: {elemento['Talla']} | "
              f"Alquiler: {elemento['FechaAlquiler']} | Devolución: {elemento['FechaProgramada']} | ID: {elemento['Id'] or 'histórico'}")
    codigo = input("Código del traje que quiere devolver: ").strip()
    talla = input("Talla del alquiler que quiere devolver: ").strip().upper()
    candidatos = [registro_r for registro_r in activa if registro_r["Codigo"] == codigo and registro_r["Talla"].upper() == talla]
    if not candidatos:
        print("No tienes un alquiler activo con ese código y talla.")
        return
    if len(candidatos) == 1:
        elegido = candidatos[0]
    else:
        for indice_i, elemento in enumerate(candidatos, 1):
            print(f"{indice_i}. Alquiler: {elemento['FechaAlquiler']} | Devolución: {elemento['FechaProgramada']} | ID: {elemento['Id'] or 'histórico'}")
        opcion = input("Seleccione el número del alquiler: ").strip()
        if not opcion.isdigit() or not 1 <= int(opcion) <= len(candidatos):
            print("Selección inválida.")
            return
        elegido = candidatos[int(opcion) - 1]
    identificador = elegido["Id"] or str(elegido["IndiceArchivo"])
    try:
        devuelto = devolver_alquiler(correo, identificador)
        print(f"Traje devuelto: {devuelto['Nombre']}. Fecha real: {devuelto['FechaReal']}.")
        print("La talla queda en revisión durante dos días después de la devolución programada.")
    except (PermissionError, ValueError, OSError) as error:
        print(f"No se pudo completar la devolución: {error}")


def alquiler_trajes():
    try:
        requerir_usuario()
    except PermissionError as error:
        print(error)
        return
    while True:
        print("\nALQUILER DE TRAJES\n1. Ver trajes\n2. Consultar disponibilidad\n3. Registrar alquiler\n4. Consultar mis alquileres\n5. Devolver traje\n6. Salir")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                _mostrar_trajes()
            elif opcion == "2":
                codigo = input("Código del traje: ").strip()
                talla = input("Talla: ").strip().upper()
                fecha_inicio = datetime.datetime.strptime(input("Fecha de alquiler (DD/MM/AAAA): ").strip(), "%d/%m/%Y").date()
                fecha_fin = datetime.datetime.strptime(input("Fecha de devolución (DD/MM/AAAA): ").strip(), "%d/%m/%Y").date()
                if fecha_fin <= fecha_inicio:
                    print("La devolución debe ser posterior al alquiler.")
                    continue
                traje = next((elemento_s for elemento_s in cargar_trajes() if elemento_s[0] == codigo), None)
                if traje is None or talla not in {elemento_x.strip().upper() for elemento_x in str(traje[2]).split(",")}:
                    print("No existe ese traje o talla.")
                    continue
                print(f"{traje[1]} | Talla {talla}: {'No disponible' if hay_conflicto_alquiler(codigo, talla, fecha_inicio, fecha_fin) else 'Disponible'}")
            elif opcion == "3":
                _mostrar_trajes()
                codigo = input("Seleccione el código del traje: ").strip()
                talla = input("Talla: ").strip().upper()
                fecha_inicio = input("Fecha del alquiler (DD/MM/AAAA): ").strip()
                fecha_fin = input("Fecha de devolución (DD/MM/AAAA): ").strip()
                alquiler = registrar_alquiler(sesion_actual.correo, codigo, talla, fecha_inicio, fecha_fin)
                print(f"Alquiler registrado: {alquiler['Nombre']} ({alquiler['Id']}).")
            elif opcion == "4":
                consultar_alquileres()
            elif opcion == "5":
                devolver_traje()
            elif opcion == "6":
                return
            else:
                print("Opción inválida.")
        except (ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def _mostrar_carrito(correo):
    detalles = obtener_detalles_carrito(correo)
    if not detalles:
        print("Tu carrito está vacío.")
        return []
    total = 0
    completo = True
    print("\nMI CARRITO")
    for indice_i, elemento in enumerate(detalles, 1):
        precio = "No disponible" if elemento["Precio"] is None else f"${elemento['Precio']:,.0f}"
        subtotal = "No disponible" if elemento["Subtotal"] is None else f"${elemento['Subtotal']:,.0f}"
        print(f"{indice_i}. {elemento['Nombre']} | Código: {elemento['Codigo']} | Talla: {elemento['Talla']} | "
              f"Cantidad: {elemento['Cantidad']} | Precio unitario: {precio} | Subtotal: {subtotal}")
        if elemento["Aviso"]:
            print(f"   Aviso: {elemento['Aviso']}")
        if elemento["Subtotal"] is None:
            completo = False
        else:
            total += elemento["Subtotal"]
    print(f"Total del carrito: ${total:,.0f}" if completo else f"Total parcial: ${total:,.0f}")
    return detalles


def _mostrar_resumen_compra(detalles, total):
    print("\nRESUMEN DE COMPRA")
    for elemento in detalles:
        print(f"{elemento['Nombre']} | Código: {elemento['Codigo']} | Talla: {elemento['Talla']} | "
              f"Cantidad: {elemento['Cantidad']} | Precio: ${elemento['Precio']:,.0f} | Subtotal: ${elemento['Subtotal']:,.0f}")
    print(f"TOTAL: ${total:,.0f}")


def confirmar_compra(correo, respuesta=None, fecha_hora=None):
    try:
        correo = requerir_usuario(correo)
        detalles, total, error = preparar_compra(correo)
        if error:
            print(error)
            return False
        _mostrar_resumen_compra(detalles, total)
        confirmado = (
            input("¿Confirmas la compra? (S/N): ").strip().upper() == "S"
            if respuesta is None else str(respuesta).strip().upper() == "S"
        )
        resultado = confirmar_compra(correo, confirmado, fecha_hora)
        print(resultado["message"])
        if resultado.get("pedido"):
            print(f"Pedido: {resultado['pedido']}\nComprobante: {resultado['comprobante']}")
        if resultado.get("details") and not resultado["ok"]:
            _mostrar_resumen_compra(resultado["details"], resultado["total"])
        return resultado["ok"]
    except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
        print(f"No se pudo confirmar la compra: {error}")
        return False


def carrito():
    try:
        correo = requerir_usuario()
    except PermissionError as error:
        print(error)
        return
    while True:
        print("\nCARRITO DE COMPRAS\n1. Consultar carrito\n2. Agregar producto desde el catálogo\n3. Modificar cantidad\n4. Eliminar artículo\n5. Confirmar compra\n6. Volver")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                _mostrar_carrito(correo)
            elif opcion == "2":
                catalogo = cargar_catalogo_ropa()
                _mostrar_ropa(catalogo)
                codigo = input("Código del producto: ").strip()
                talla = input("Talla: ").strip()
                cantidad = input("Cantidad: ").strip()
                agregar_al_carrito(correo, codigo, talla, cantidad, catalogo)
                print("Artículo agregado.")
            elif opcion in {"3", "4"}:
                detalles = _mostrar_carrito(correo)
                if not detalles:
                    continue
                opcion = input("Número del artículo: ").strip()
                if not opcion.isdigit() or not 1 <= int(opcion) <= len(detalles):
                    print("Selección inválida.")
                    continue
                elemento = detalles[int(opcion)-1]
                if opcion == "3":
                    actualizar_cantidad_carrito(correo, elemento["Codigo"], elemento["Talla"], input("Nueva cantidad: ").strip())
                    print("Cantidad actualizada.")
                else:
                    eliminar_del_carrito(correo, elemento["Codigo"], elemento["Talla"])
                    print("Artículo eliminado.")
            elif opcion == "5":
                detalles, total, error = preparar_compra(correo)
                if error:
                    print(error)
                    continue
                _mostrar_resumen_compra(detalles, total)
                confirmado = input("¿Confirmas la compra? (S/N): ").strip().upper() == "S"
                resultado = confirmar_compra(correo, confirmado)
                print(resultado["message"])
                if resultado.get("pedido"):
                    print(f"Pedido: {resultado['pedido']}\nComprobante: {resultado['comprobante']}")
                if resultado.get("details") and not resultado["ok"]:
                    _mostrar_resumen_compra(resultado["details"], resultado["total"])
            elif opcion == "6":
                return
            else:
                print("Opción inválida.")
        except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def _mostrar_favoritos(correo):
    favoritos = listar_favoritos(correo)
    if not favoritos:
        print("No tienes productos favoritos.")
    for indice, elemento in enumerate(favoritos, 1):
        if elemento["EstadoFavorito"] == "Activo":
            tallas = ", ".join(f"{elemento_v['Talla']}: {elemento_v['Cantidad']}" for elemento_v in elemento["Tallas"]) or "Sin tallas"
            print(f"{indice}. {elemento['Nombre']} ({elemento['Codigo']}) | {elemento['Tipo']} | ${elemento['Precio']:,.0f} | {tallas} | {elemento['Disponibilidad']}")
        else:
            print(f"{indice}. {elemento['Codigo']} | {elemento['EstadoFavorito']}")
    return favoritos


def favoritos():
    try:
        correo = requerir_usuario()
    except PermissionError as error:
        print(error)
        return
    while True:
        print("\nFAVORITOS\n1. Consultar\n2. Agregar desde catálogo\n3. Eliminar\n4. Volver")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                _mostrar_favoritos(correo)
            elif opcion == "2":
                catalogo = cargar_catalogo_ropa()
                _mostrar_ropa(catalogo)
                if not catalogo:
                    continue
                opcion = input("Número del producto para agregar (Enter cancela): ").strip()
                if opcion and opcion.isdigit() and 1 <= int(opcion) <= len(catalogo):
                    agregar_favorito(correo, catalogo[int(opcion)-1]["Codigo"])
                    print("Producto agregado a Favoritos.")
                elif opcion:
                    print("Selección inválida.")
            elif opcion == "3":
                articulos = _mostrar_favoritos(correo)
                opcion = input("Número del favorito para eliminar (Enter cancela): ").strip()
                if opcion and opcion.isdigit() and 1 <= int(opcion) <= len(articulos):
                    if eliminar_favorito(correo, articulos[int(opcion)-1]["Codigo"]):
                        print("Favorito eliminado.")
                elif opcion:
                    print("Selección inválida.")
            elif opcion == "4":
                return
            else:
                print("Opción inválida.")
        except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def _mostrar_inventario_administracion():
    productos, existencias = cargar_inventario_administracion()
    for _, producto in productos.iterrows():
        variantes = existencias[existencias["Codigo"].str.casefold() == str(producto["Codigo"]).casefold()]
        tallas = ", ".join(f"{fila.Talla}: {fila.Cantidad}" for fila in variantes.itertuples(index=False)) or "Sin tallas"
        print(f"{producto['Codigo']} | {producto['Nombre']} | {producto['Seccion']} | {producto['Tipo']} | ${producto['Precio']:,.0f} | {producto['Estado']} | {tallas}")


def menu_administracion_inventario():
    if not es_administrador(sesion_actual.correo):
        print("Esta operación requiere una sesión administrativa autorizada.")
        return
    while True:
        print("\nADMINISTRACIÓN DE ROPA\n1. Consultar productos\n2. Registrar producto\n3. Modificar producto\n4. Agregar talla y existencias\n5. Modificar cantidad\n6. Desactivar producto\n7. Volver")
        opcion = input("Opción: ").strip()
        try:
            if opcion == "1":
                _mostrar_inventario_administracion()
            elif opcion == "2":
                registrar_producto(input("Código: "), input("Nombre: "), input("Sección: "), input("Categoría: "), input("Precio: "))
                print("Producto registrado.")
            elif opcion == "3":
                codigo = input("Código: ").strip()
                actualizar_producto(codigo, input("Nuevo nombre (Enter conserva): ").strip() or None,
                               input("Nueva sección (Enter conserva): ").strip() or None,
                               input("Nueva categoría (Enter conserva): ").strip() or None,
                               input("Nuevo precio (Enter conserva): ").strip() or None)
                print("Producto actualizado.")
            elif opcion == "4":
                agregar_variante_existencias(input("Código: "), input("Talla: "), input("Cantidad: "))
                print("Existencia agregada.")
            elif opcion == "5":
                actualizar_existencias(input("Código: "), input("Talla: "), input("Nueva cantidad: "))
                print("Existencia actualizada.")
            elif opcion == "6":
                codigo = input("Código: ").strip()
                if input(f"¿Desactivar {codigo}? (S/N): ").strip().upper() == "S":
                    desactivar_producto(codigo)
                    print("Producto desactivado.")
            elif opcion == "7":
                return
            else:
                print("Opción inválida.")
        except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def ejecutar_consola():
    inicio_consola()
    while True:
        print("\n1. Home\n2. Buscar\n3. Alquiler de trajes\n4. Carrito\n5. Favoritos\n6. Cuenta\n7. Salir")
        if sesion_actual.activa and es_administrador(sesion_actual.correo):
            print("8. Administración de ropa")
        opcion = input("Ingrese una opción: ").strip()
        if opcion == "1":
            inicio_consola()
        elif opcion == "2":
            buscar()
        elif opcion == "3":
            alquiler_trajes()
        elif opcion == "4":
            carrito()
        elif opcion == "5":
            favoritos()
        elif opcion == "6":
            sesion()
        elif opcion == "7":
            print("Gracias por visitar EFRATA MINI-MALL.")
            return
        elif opcion == "8" and sesion_actual.activa and es_administrador(sesion_actual.correo):
            menu_administracion_inventario()
        else:
            print("Opción inválida.")


def mostrar_catalogo():
    _mostrar_trajes()


def mostrar_catalogo_de_ropa(productos):
    _mostrar_ropa(productos)


def mostrar_carrito_usuario(correo, catalogo=None):
    return _mostrar_carrito(correo)


if __name__ == "__main__":
    ejecutar_consola()
