"""Interfaz de terminal. La GUI futura debe llamar a los servicios de backend."""

import datetime
import getpass
import zipfile

from backend.sesion import current_session, require_user
from backend.usuarios import (
    authenticate_user, close_session, normalize_email, register_user,
    user_exists,
)
from backend.datos_personales import (
    read_personal_data, save_personal_data, delete_personal_data,
)
from backend.catalogo import (
    load_clothing_catalog, filter_clothing_catalog, load_suits,
)
from backend.alquileres import (
    check_rental_conflict, get_user_rentals, register_rental, return_rental,
)
from backend.carrito import (
    add_to_cart, update_cart_quantity, remove_from_cart, get_cart_details,
)
from backend.compras import (
    prepare_purchase, confirm_purchase, list_purchases, get_purchase_detail,
)
from backend.administracion import (
    is_administrator, load_admin_inventory, register_product, update_product,
    add_stock_variant, update_stock, deactivate_product,
)
from backend.favoritos import list_favorites, add_favorite, remove_favorite


def home():
    print("\n¡Bienvenidos a EFRATA MINI-MALL!")
    print("\nModa, alquiler de trajes y arreglos en un solo lugar")
    print("\nModa nacional e importada\nTrajes para toda ocasión\nArreglo de ropa\n")
    print("\nCali, Colombia\n3239655863")
    print("\n¡Será un placer atenderte!\n")


def _show_clothing(products):
    if not products:
        print("No se encontraron prendas con esos filtros.")
        return
    print("\nCATÁLOGO DE ROPA")
    for product in products:
        sizes = ", ".join(
            f"{v['Talla']}: {v['Cantidad']} unidades ({'Disponible' if v['Cantidad'] else 'Agotado'})"
            for v in product["Tallas"]
        ) or "Sin tallas registradas"
        print(
            f"\nCódigo: {product['Codigo']}\nNombre: {product['Nombre']}\n"
            f"Sección: {product['Seccion']}\nCategoría: {product['Tipo']}\n"
            f"Tallas y cantidades: {sizes}\nPrecio: ${product['Precio']:,.0f}\n"
            f"Disponibilidad: {product['Disponibilidad']}"
        )


def buscar():
    print("\nBUSCAR ROPA")
    try:
        catalog = load_clothing_catalog()
    except (ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
        print(f"No se pudo cargar el catálogo: {error}")
        return
    if not catalog:
        print("El catálogo no tiene productos activos registrados.")
        return
    sections = {"1": "Mujer", "2": "Hombre", "3": "Unisex"}
    while True:
        print("\n1. Mujer\n2. Hombre\n3. Unisex\n4. Todas las secciones\n5. Volver")
        selection = input("Seleccione una sección: ").strip()
        if selection == "5":
            return
        if selection not in {"1", "2", "3", "4"}:
            print("Opción inválida.")
            continue
        section = sections.get(selection)
        section_products = filter_clothing_catalog(catalog, section=section)
        if not section_products:
            print("No hay productos activos para esa sección.")
            continue
        categories = sorted({p["Tipo"] for p in section_products}, key=str.casefold)
        print("\n0. Todas las categorías")
        for index, category in enumerate(categories, start=1):
            print(f"{index}. {category}")
        back = str(len(categories) + 1)
        print(f"{back}. Volver a secciones")
        choice = input("Seleccione una categoría: ").strip()
        if choice == back:
            continue
        if choice == "0":
            category = None
        elif choice.isdigit() and 1 <= int(choice) <= len(categories):
            category = categories[int(choice) - 1]
        else:
            print("Opción inválida.")
            continue
        _show_clothing(filter_clothing_catalog(catalog, section, category))
        return


def sesion():
    print("\nEFRATA MINI-MALL\nInicia sesión o crea tu cuenta")
    try:
        email = normalize_email(input("Correo electrónico: "))
    except ValueError as error:
        print(error)
        return
    if user_exists(email):
        password = getpass.getpass("CONTRASEÑA: ")
        if not authenticate_user(email, password):
            print("La combinación de usuario y contraseña no es correcta.")
            return
        print("Inicio de sesión exitoso.")
    else:
        print(f"CREAR CUENTA\nCorreo electrónico: {email}")
        while True:
            password = getpass.getpass(
                "CONTRASEÑA (mínimo 8 caracteres, mayúscula, minúscula y número): "
            )
            try:
                register_user(email, password)
                break
            except ValueError as error:
                print(error)
        print("Cuenta creada exitosamente.")
    cuenta()


def _show_personal_data(data):
    print("\nMIS DATOS PERSONALES")
    for label, key in (("Nombre", "Nombre"), ("Apellidos", "Apellidos"),
                       ("Teléfono", "Telefono"), ("Tipo de documento", "TipoDocumento"),
                       ("Número de documento", "NumeroDocumento"),
                       ("Dirección", "Direccion"), ("Código postal", "CodigoPostal")):
        print(f"{label}: {data[key]}")


def mis_datos():
    try:
        email = require_user()
    except PermissionError as error:
        print(error)
        return
    while True:
        data = read_personal_data(email)
        if data is None:
            print("\nNo tienes datos personales registrados.\n1. Registrar mis datos\n2. Volver")
            option = input("Opción: ").strip()
            if option == "2":
                return
            if option != "1":
                print("Opción inválida.")
                continue
            current = {}
        else:
            print("\n1. Consultar datos\n2. Modificar datos\n3. Eliminar datos\n4. Volver")
            option = input("Opción: ").strip()
            if option == "1":
                _show_personal_data(data)
                continue
            if option == "3":
                if input("¿Deseas eliminar tus datos? (S/N): ").strip().upper() == "S":
                    delete_personal_data(email)
                    print("Datos personales eliminados.")
                else:
                    print("Eliminación cancelada.")
                continue
            if option == "4":
                return
            if option != "2":
                print("Opción inválida.")
                continue
            current = data
        labels = (("Nombre", "Nombre"), ("Apellidos", "Apellidos"),
                  ("Telefono", "Teléfono (+57, 10 dígitos)"),
                  ("TipoDocumento", "Tipo de documento (CC, CE, NIT)"),
                  ("NumeroDocumento", "Número de documento"), ("Direccion", "Dirección"),
                  ("CodigoPostal", "Código postal (6 dígitos)"))
        values = {}
        for key, label in labels:
            old = current.get(key, "")
            entered = input(f"{label}{f' [{old}]' if old else ''}: ").strip()
            values[key] = entered or old
        try:
            save_personal_data(email, values)
            print("Datos personales guardados.")
        except (ValueError, OSError) as error:
            print(f"No se pudieron guardar los datos: {error}")


def mis_compras(correo=None, seleccion=None):
    try:
        email = require_user(correo)
        orders = list_purchases(email)
    except (PermissionError, OSError) as error:
        print(error)
        return
    if not orders:
        print("Aún no tienes compras registradas.")
        return
    for i, order in enumerate(orders, 1):
        print(f"{i}. Pedido: {order['Pedido']} | Fecha: {order['Fecha']} | Total: ${order['Total']:,.2f}")
    selection = (input("Número de compra o ID del pedido (Enter para volver): ").strip()
                 if seleccion is None else str(seleccion).strip())
    if not selection:
        return orders
    order = next((o for o in orders if o["Pedido"].casefold() == selection.casefold()), None)
    if order is None and selection.isdigit() and 1 <= int(selection) <= len(orders):
        order = orders[int(selection) - 1]
    if order is None:
        print("No se encontró ese pedido.")
        return orders
    print(f"\nDETALLE DEL PEDIDO {order['Pedido']}\nFecha: {order['Fecha']}")
    for item in order["Articulos"]:
        print(f"{item['Nombre']} | Código: {item['Codigo']} | Talla: {item['Talla']} | "
              f"Cantidad: {item['Cantidad']} | Precio: ${item['Precio']:,.2f} | "
              f"Subtotal: ${item['Subtotal']:,.2f}")
    print(f"Total: ${order['Total']:,.2f}")
    return orders


def mis_compras_ui():
    return mis_compras(current_session.email)


def cuenta():
    while True:
        print(f"\nBIENVENIDO, {current_session.email}\n\nMI CUENTA\n1. Mis compras\n2. Mis datos\n3. Cerrar sesión\n4. Salir")
        option = input("Ingrese una opción: ").strip()
        if option == "1":
            mis_compras_ui()
        elif option == "2":
            mis_datos()
        elif option == "3":
            close_session()
            print("Sesión cerrada.")
            return
        elif option == "4":
            return
        else:
            print("Opción inválida.")


def _show_suits():
    suits = load_suits()
    if not suits:
        print("No hay trajes registrados.")
    for suit in suits:
        print(f"Código: {suit[0]} | Traje: {suit[1]} | Tallas: {suit[2]} | Precio: ${suit[3]:,}")


def consultar_alquileres():
    try:
        email = require_user()
        rentals = get_user_rentals(email)
    except (PermissionError, OSError) as error:
        print(error)
        return
    if not rentals:
        print("No tienes alquileres registrados.")
        return
    print("\nMIS ALQUILERES")
    for position, rental in enumerate(rentals, 1):
        print(f"{position}. {rental['Estado']} | {rental['Nombre']} | Código: {rental['Codigo']} | "
              f"Talla: {rental['Talla']} | Alquiler: {rental['FechaAlquiler']} | "
              f"Devolución programada: {rental['FechaProgramada']} | Precio: ${rental['Precio']}")
        if rental["FechaReal"]:
            print(f"   Fecha real de devolución: {rental['FechaReal']}")
    choice = input("Número del alquiler para ver detalle (Enter para volver): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(rentals):
        rental = rentals[int(choice) - 1]
        print(f"\nDETALLE: {rental['Nombre']} ({rental['Codigo']}) | Talla {rental['Talla']} | "
              f"Alquiler {rental['FechaAlquiler']} | Programada {rental['FechaProgramada']} | "
              f"Precio ${rental['Precio']} | Estado {rental['Estado']} | "
              f"Real {rental['FechaReal'] or 'Pendiente/no registrada'} | ID {rental['Id'] or 'histórico'}")
    elif choice:
        print("Selección inválida.")


def devolver_traje():
    try:
        email = require_user()
        active = [r for r in get_user_rentals(email) if r["Estado"].casefold() == "activo"]
    except (PermissionError, OSError) as error:
        print(error)
        return
    if not active:
        print("No tienes alquileres pendientes de devolución.")
        return
    for i, item in enumerate(active, 1):
        print(f"{i}. Código: {item['Codigo']} | Traje: {item['Nombre']} | Talla: {item['Talla']} | "
              f"Alquiler: {item['FechaAlquiler']} | Devolución: {item['FechaProgramada']} | ID: {item['Id'] or 'histórico'}")
    code = input("Código del traje que quiere devolver: ").strip()
    size = input("Talla del alquiler que quiere devolver: ").strip().upper()
    candidates = [r for r in active if r["Codigo"] == code and r["Talla"].upper() == size]
    if not candidates:
        print("No tienes un alquiler activo con ese código y talla.")
        return
    if len(candidates) == 1:
        chosen = candidates[0]
    else:
        for i, item in enumerate(candidates, 1):
            print(f"{i}. Alquiler: {item['FechaAlquiler']} | Devolución: {item['FechaProgramada']} | ID: {item['Id'] or 'histórico'}")
        choice = input("Seleccione el número del alquiler: ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(candidates):
            print("Selección inválida.")
            return
        chosen = candidates[int(choice) - 1]
    token = chosen["Id"] or str(chosen["IndiceArchivo"])
    try:
        returned = return_rental(email, token)
        print(f"Traje devuelto: {returned['Nombre']}. Fecha real: {returned['FechaReal']}.")
        print("La talla queda en revisión durante dos días después de la devolución programada.")
    except (PermissionError, ValueError, OSError) as error:
        print(f"No se pudo completar la devolución: {error}")


def alquiler_trajes():
    try:
        require_user()
    except PermissionError as error:
        print(error)
        return
    while True:
        print("\nALQUILER DE TRAJES\n1. Ver trajes\n2. Consultar disponibilidad\n3. Registrar alquiler\n4. Consultar mis alquileres\n5. Devolver traje\n6. Salir")
        option = input("Opción: ").strip()
        try:
            if option == "1":
                _show_suits()
            elif option == "2":
                code = input("Código del traje: ").strip()
                size = input("Talla: ").strip().upper()
                start = datetime.datetime.strptime(input("Fecha de alquiler (DD/MM/AAAA): ").strip(), "%d/%m/%Y").date()
                end = datetime.datetime.strptime(input("Fecha de devolución (DD/MM/AAAA): ").strip(), "%d/%m/%Y").date()
                if end <= start:
                    print("La devolución debe ser posterior al alquiler.")
                    continue
                suit = next((s for s in load_suits() if s[0] == code), None)
                if suit is None or size not in {x.strip().upper() for x in str(suit[2]).split(",")}:
                    print("No existe ese traje o talla.")
                    continue
                print(f"{suit[1]} | Talla {size}: {'No disponible' if check_rental_conflict(code, size, start, end) else 'Disponible'}")
            elif option == "3":
                _show_suits()
                code = input("Seleccione el código del traje: ").strip()
                size = input("Talla: ").strip().upper()
                start = input("Fecha del alquiler (DD/MM/AAAA): ").strip()
                end = input("Fecha de devolución (DD/MM/AAAA): ").strip()
                rental = register_rental(current_session.email, code, size, start, end)
                print(f"Alquiler registrado: {rental['Nombre']} ({rental['Id']}).")
            elif option == "4":
                consultar_alquileres()
            elif option == "5":
                devolver_traje()
            elif option == "6":
                return
            else:
                print("Opción inválida.")
        except (ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def _show_cart(email):
    details = get_cart_details(email)
    if not details:
        print("Tu carrito está vacío.")
        return []
    total = 0
    complete = True
    print("\nMI CARRITO")
    for i, item in enumerate(details, 1):
        price = "No disponible" if item["Precio"] is None else f"${item['Precio']:,.0f}"
        subtotal = "No disponible" if item["Subtotal"] is None else f"${item['Subtotal']:,.0f}"
        print(f"{i}. {item['Nombre']} | Código: {item['Codigo']} | Talla: {item['Talla']} | "
              f"Cantidad: {item['Cantidad']} | Precio unitario: {price} | Subtotal: {subtotal}")
        if item["Aviso"]:
            print(f"   Aviso: {item['Aviso']}")
        if item["Subtotal"] is None:
            complete = False
        else:
            total += item["Subtotal"]
    print(f"Total del carrito: ${total:,.0f}" if complete else f"Total parcial: ${total:,.0f}")
    return details


def _show_purchase_summary(details, total):
    print("\nRESUMEN DE COMPRA")
    for item in details:
        print(f"{item['Nombre']} | Código: {item['Codigo']} | Talla: {item['Talla']} | "
              f"Cantidad: {item['Cantidad']} | Precio: ${item['Precio']:,.0f} | Subtotal: ${item['Subtotal']:,.0f}")
    print(f"TOTAL: ${total:,.0f}")


def confirmar_compra(correo, respuesta=None, fecha_hora=None):
    try:
        email = require_user(correo)
        details, total, error = prepare_purchase(email)
        if error:
            print(error)
            return False
        _show_purchase_summary(details, total)
        confirmed = (
            input("¿Confirmas la compra? (S/N): ").strip().upper() == "S"
            if respuesta is None else str(respuesta).strip().upper() == "S"
        )
        result = confirm_purchase(email, confirmed, fecha_hora)
        print(result["message"])
        if result.get("pedido"):
            print(f"Pedido: {result['pedido']}\nComprobante: {result['comprobante']}")
        if result.get("details") and not result["ok"]:
            _show_purchase_summary(result["details"], result["total"])
        return result["ok"]
    except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
        print(f"No se pudo confirmar la compra: {error}")
        return False


def carrito():
    try:
        email = require_user()
    except PermissionError as error:
        print(error)
        return
    while True:
        print("\nCARRITO DE COMPRAS\n1. Consultar carrito\n2. Agregar producto desde el catálogo\n3. Modificar cantidad\n4. Eliminar artículo\n5. Confirmar compra\n6. Volver")
        option = input("Opción: ").strip()
        try:
            if option == "1":
                _show_cart(email)
            elif option == "2":
                catalog = load_clothing_catalog()
                _show_clothing(catalog)
                code = input("Código del producto: ").strip()
                size = input("Talla: ").strip()
                amount = input("Cantidad: ").strip()
                add_to_cart(email, code, size, amount, catalog)
                print("Artículo agregado.")
            elif option in {"3", "4"}:
                details = _show_cart(email)
                if not details:
                    continue
                choice = input("Número del artículo: ").strip()
                if not choice.isdigit() or not 1 <= int(choice) <= len(details):
                    print("Selección inválida.")
                    continue
                item = details[int(choice)-1]
                if option == "3":
                    update_cart_quantity(email, item["Codigo"], item["Talla"], input("Nueva cantidad: ").strip())
                    print("Cantidad actualizada.")
                else:
                    remove_from_cart(email, item["Codigo"], item["Talla"])
                    print("Artículo eliminado.")
            elif option == "5":
                details, total, error = prepare_purchase(email)
                if error:
                    print(error)
                    continue
                _show_purchase_summary(details, total)
                confirmed = input("¿Confirmas la compra? (S/N): ").strip().upper() == "S"
                result = confirm_purchase(email, confirmed)
                print(result["message"])
                if result.get("pedido"):
                    print(f"Pedido: {result['pedido']}\nComprobante: {result['comprobante']}")
                if result.get("details") and not result["ok"]:
                    _show_purchase_summary(result["details"], result["total"])
            elif option == "6":
                return
            else:
                print("Opción inválida.")
        except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def _show_favorites(email):
    favorites = list_favorites(email)
    if not favorites:
        print("No tienes productos favoritos.")
    for index, item in enumerate(favorites, 1):
        if item["EstadoFavorito"] == "Activo":
            sizes = ", ".join(f"{v['Talla']}: {v['Cantidad']}" for v in item["Tallas"]) or "Sin tallas"
            print(f"{index}. {item['Nombre']} ({item['Codigo']}) | {item['Tipo']} | ${item['Precio']:,.0f} | {sizes} | {item['Disponibilidad']}")
        else:
            print(f"{index}. {item['Codigo']} | {item['EstadoFavorito']}")
    return favorites


def favoritos():
    try:
        email = require_user()
    except PermissionError as error:
        print(error)
        return
    while True:
        print("\nFAVORITOS\n1. Consultar\n2. Agregar desde catálogo\n3. Eliminar\n4. Volver")
        option = input("Opción: ").strip()
        try:
            if option == "1":
                _show_favorites(email)
            elif option == "2":
                catalog = load_clothing_catalog()
                _show_clothing(catalog)
                if not catalog:
                    continue
                choice = input("Número del producto para agregar (Enter cancela): ").strip()
                if choice and choice.isdigit() and 1 <= int(choice) <= len(catalog):
                    add_favorite(email, catalog[int(choice)-1]["Codigo"])
                    print("Producto agregado a Favoritos.")
                elif choice:
                    print("Selección inválida.")
            elif option == "3":
                items = _show_favorites(email)
                choice = input("Número del favorito para eliminar (Enter cancela): ").strip()
                if choice and choice.isdigit() and 1 <= int(choice) <= len(items):
                    if remove_favorite(email, items[int(choice)-1]["Codigo"]):
                        print("Favorito eliminado.")
                elif choice:
                    print("Selección inválida.")
            elif option == "4":
                return
            else:
                print("Opción inválida.")
        except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def _admin_inventory_display():
    products, stock = load_admin_inventory()
    for _, product in products.iterrows():
        variants = stock[stock["Codigo"].str.casefold() == str(product["Codigo"]).casefold()]
        sizes = ", ".join(f"{row.Talla}: {row.Cantidad}" for row in variants.itertuples(index=False)) or "Sin tallas"
        print(f"{product['Codigo']} | {product['Nombre']} | {product['Seccion']} | {product['Tipo']} | ${product['Precio']:,.0f} | {product['Estado']} | {sizes}")


def menu_administracion_inventario():
    if not is_administrator(current_session.email):
        print("Esta operación requiere una sesión administrativa autorizada.")
        return
    while True:
        print("\nADMINISTRACIÓN DE ROPA\n1. Consultar productos\n2. Registrar producto\n3. Modificar producto\n4. Agregar talla y existencias\n5. Modificar cantidad\n6. Desactivar producto\n7. Volver")
        option = input("Opción: ").strip()
        try:
            if option == "1":
                _admin_inventory_display()
            elif option == "2":
                register_product(input("Código: "), input("Nombre: "), input("Sección: "), input("Categoría: "), input("Precio: "))
                print("Producto registrado.")
            elif option == "3":
                code = input("Código: ").strip()
                update_product(code, input("Nuevo nombre (Enter conserva): ").strip() or None,
                               input("Nueva sección (Enter conserva): ").strip() or None,
                               input("Nueva categoría (Enter conserva): ").strip() or None,
                               input("Nuevo precio (Enter conserva): ").strip() or None)
                print("Producto actualizado.")
            elif option == "4":
                add_stock_variant(input("Código: "), input("Talla: "), input("Cantidad: "))
                print("Existencia agregada.")
            elif option == "5":
                update_stock(input("Código: "), input("Talla: "), input("Nueva cantidad: "))
                print("Existencia actualizada.")
            elif option == "6":
                code = input("Código: ").strip()
                if input(f"¿Desactivar {code}? (S/N): ").strip().upper() == "S":
                    deactivate_product(code)
                    print("Producto desactivado.")
            elif option == "7":
                return
            else:
                print("Opción inválida.")
        except (PermissionError, ValueError, OSError, ImportError, zipfile.BadZipFile) as error:
            print(f"No se pudo completar la operación: {error}")


def run_console():
    home()
    while True:
        print("\n1. Home\n2. Buscar\n3. Alquiler de trajes\n4. Carrito\n5. Favoritos\n6. Cuenta\n7. Salir")
        if current_session.active and is_administrator(current_session.email):
            print("8. Administración de ropa")
        option = input("Ingrese una opción: ").strip()
        if option == "1":
            home()
        elif option == "2":
            buscar()
        elif option == "3":
            alquiler_trajes()
        elif option == "4":
            carrito()
        elif option == "5":
            favoritos()
        elif option == "6":
            sesion()
        elif option == "7":
            print("Gracias por visitar EFRATA MINI-MALL.")
            return
        elif option == "8" and current_session.active and is_administrator(current_session.email):
            menu_administracion_inventario()
        else:
            print("Opción inválida.")


def mostrar_catalogo():
    _show_suits()


def mostrar_catalogo_ropa(products):
    _show_clothing(products)


def mostrar_carrito(email, catalog=None):
    return _show_cart(email)


if __name__ == "__main__":
    run_console()
