import datetime
import pandas as pd
import os

trajes_iniciales = [
    ["1", "Esmoquin clásico", "S, M, L", 120000, "Disponible"],
    ["2", "Traje azul elegante", "M, L, XL", 100000, "Disponible"],
    ["3", "Vestido de gala", "S, M", 150000, "Disponible"],
    ["4", "Traje formal gris", "M, L, XL", 90000, "Disponible"]
]

# CREAR AUTOMÁTICAMENTE LOS ARCHIVOS TXT SI NO EXISTEN
for nombre_archivo in [
    "usuarios.txt",
    "trajesdisponibles.txt",
    "consultardisponibilidad.txt",
    "registraralquiler.txt",
    "iniciossesion.txt"
]:
    if not os.path.exists(nombre_archivo):
        with open(nombre_archivo, "a", encoding="utf-8"):
            pass

# CREAR EL EXCEL INICIAL DE TRAJES
if not os.path.exists("inventario.xlsx"):
    datos = pd.DataFrame(
        trajes_iniciales,
        columns=["Codigo", "Nombre", "Tallas", "Precio", "Estado"]
    )
    datos.to_excel("inventario.xlsx", index=False)


# INVENTARIO DE ROPA NORMAL

ropa_inicial = [
    ["R001", "Blusa básica", "Mujer", "Blusa", "S, M, L", 45000, 10, "Disponible"],
    ["R002", "Jean clásico", "Mujer", "Pantalón", "6, 8, 10", 85000, 5, "Disponible"],
    ["R003", "Falda casual", "Mujer", "Falda", "S, M, L", 55000, 4, "Disponible"],
    ["R004", "Vestido casual", "Mujer", "Vestido", "S, M, L", 75000, 3, "Disponible"],
    ["R005", "Chaqueta femenina", "Mujer", "Chaqueta", "S, M, L", 95000, 2, "Disponible"],
    ["R006", "Camisa casual", "Hombre", "Camisa", "S, M, L, XL", 60000, 8, "Disponible"],
    ["R007", "Camiseta básica", "Hombre", "Camiseta", "S, M, L, XL", 35000, 12, "Disponible"],
    ["R008", "Jean azul", "Hombre", "Pantalón", "30, 32, 34, 36", 90000, 6, "Disponible"],
    ["R009", "Short casual", "Hombre", "Short", "M, L, XL", 50000, 4, "Disponible"],
    ["R010", "Chaqueta masculina", "Hombre", "Chaqueta", "M, L, XL", 110000, 3, "Disponible"],
    ["R011", "Buzo básico", "Hombre", "Buzo", "S, M, L, XL", 70000, 5, "Disponible"]
]

# CREAR EL EXCEL DE ROPA SI NO EXISTE
if not os.path.exists("ropa.xlsx"):
    datos_ropa = pd.DataFrame(
        ropa_inicial,
        columns=[
            "Codigo", "Nombre", "Sexo", "Tipo",
            "Tallas", "Precio", "Cantidad", "Estado"
        ]
    )
    datos_ropa.to_excel("ropa.xlsx", index=False)


# CARGAR LA ROPA DEL EXCEL

def cargar_ropa():
    datos = pd.read_excel("ropa.xlsx")
    prendas = []

    for fila in datos.values:
        cantidad = int(fila[6])

        if cantidad > 0:
            estado = "Disponible"
        else:
            estado = "Agotado"

        prendas.append([
            str(fila[0]),
            str(fila[1]),
            str(fila[2]),
            str(fila[3]),
            str(fila[4]),
            int(fila[5]),
            cantidad,
            estado
        ])

    return prendas


# CARGAR LOS TRAJES DEL EXCEL

def cargar_trajes():
    datos = pd.read_excel("inventario.xlsx")
    trajes = []

    for fila in datos.values:
        trajes.append([
            str(fila[0]),
            fila[1],
            fila[2],
            int(fila[3]),
            fila[4]
        ])

    return trajes


# GUARDAR LOS CAMBIOS DE LOS TRAJES

def guardar_trajes(trajes):
    datos = pd.DataFrame(
        trajes,
        columns=["Codigo", "Nombre", "Tallas", "Precio", "Estado"]
    )

    datos.to_excel("inventario.xlsx", index=False)


# ACTUALIZAR EL ARCHIVO DE DISPONIBILIDAD

def actualizar_disponibilidad():
    trajes = cargar_trajes()

    with open(
        "consultardisponibilidad.txt", "w", encoding="utf-8"
    ) as archivo:
        for traje in trajes:
            archivo.write(
                f"{traje[0]}|{traje[1]}|{traje[4]}\n"
            )


# MOSTRAR EL CATÁLOGO DE TRAJES

def mostrar_catalogo():
    trajes = cargar_trajes()

    print("\nCATÁLOGO DE TRAJES")
    print("-" * 45)

    if not trajes:
        print("No hay trajes registrados.")
        return

    for traje in trajes:
        print(f"Código: {traje[0]}")
        print(f"Traje: {traje[1]}")
        print(f"Tallas: {traje[2]}")
        print(f"Precio de alquiler: ${traje[3]:,}")
        print(f"Estado: {traje[4]}")
        print("-" * 45)


# SESIÓN DE USUARIO

usuario = ""
contraseña = ""
sesion_activa = False


def sesion():
    global sesion_activa, usuario, contraseña

    while True:
        print("\nEFRATA MINI-MALL")
        print("Inicia sesión o crea tu cuenta\n")

        usuario_provisional = input("E-MAIL: ").strip().lower()

        if not (
            usuario_provisional.endswith("@gmail.com")
            or usuario_provisional.endswith("@hotmail.com")
        ):
            print("El formato de e-mail no es válido.")
            continue

        # LEER LAS CUENTAS REGISTRADAS
        usuarios = []

        with open("usuarios.txt", "r", encoding="utf-8") as archivo:
            for linea in archivo:
                datos = linea.strip().split("|")

                if len(datos) == 2:
                    usuarios.append(datos)

        # COMPROBAR SI EL CORREO YA EXISTE
        contraseña_guardada = None

        for datos in usuarios:
            if datos[0] == usuario_provisional:
                contraseña_guardada = datos[1]
                break

        # INICIAR SESIÓN
        if contraseña_guardada is not None:
            print(f"\nINICIAR SESIÓN\nE-MAIL: {usuario_provisional}")
            contraseña_provisional = input("CONTRASEÑA: ")

            if contraseña_provisional == contraseña_guardada:
                usuario = usuario_provisional
                contraseña = contraseña_provisional
                sesion_activa = True

                print("\nInicio de sesión exitoso.")
                cuenta()
                return

            else:
                print(
                    "\nLa combinación de usuario y contraseña "
                    "no es correcta."
                )
                continue

        # CREAR CUENTA
        print(f"\nCREAR CUENTA\nE-MAIL: {usuario_provisional}")

        while True:
            contraseña_provisional = input(
                "CONTRASEÑA (mínimo 8 caracteres, "
                "con mayúscula, minúscula y número): "
            )

            tiene_mayus = False
            tiene_minus = False
            tiene_num = False

            for letra in contraseña_provisional:
                if letra.isupper():
                    tiene_mayus = True

                if letra.islower():
                    tiene_minus = True

                if letra.isdigit():
                    tiene_num = True

            if (
                len(contraseña_provisional) >= 8
                and tiene_mayus
                and tiene_minus
                and tiene_num
            ):
                break

            print(
                "\nContraseña inválida. Debe tener al menos "
                "8 caracteres, una mayúscula, una minúscula "
                "y un número."
            )

        # GUARDAR LA CUENTA
        with open("usuarios.txt", "a", encoding="utf-8") as archivo:
            archivo.write(
                f"{usuario_provisional}|{contraseña_provisional}\n"
            )

        usuario = usuario_provisional
        contraseña = contraseña_provisional
        sesion_activa = True

        fecha_hora = datetime.datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        with open(
            "iniciossesion.txt", "a", encoding="utf-8"
        ) as archivo:
            archivo.write(f"{usuario}|{fecha_hora}\n")

        print("\nCuenta creada exitosamente.")

        cuenta()
        return


# MENÚ DE LA CUENTA

def cuenta():
    global sesion_activa, usuario, contraseña

    while True:
        print(f"\nBIENVENIDO, {usuario}")

        print("\nMI CUENTA")
        print("1. Mis compras")
        print("2. Mis datos")
        print("3. Cerrar sesión")
        print("4. Salir")

        try:
            opcion = int(input("\nIngrese una opción: "))

            if opcion == 1:
                print("\nAún no tienes compras online.")

            elif opcion == 2:
                print("\nMIS DATOS PERSONALES")
                print(f"Usuario: {usuario}")

                nombre = input("Nombre: ").strip()
                apellidos = input("Apellidos: ").strip()
                telefono = input("Teléfono (+57): ").strip()

                print("\nDIRECCIÓN DE FACTURACIÓN")

                tipo_documento = input(
                    "Tipo de documento (CC, CE, NIT): "
                ).strip().upper()

                numero_documento = input(
                    "Número de documento: "
                ).strip()

                direccion = input("Dirección: ").strip()
                codigo_postal = input("Código postal: ").strip()

                opcion_datos = input(
                    "\n¿Desea guardar los datos? (S/N): "
                ).strip().upper()

                if opcion_datos == "S":
                    with open(
                        "datos_personales.txt",
                        "a",
                        encoding="utf-8"
                    ) as archivo:
                        archivo.write(
                            f"{usuario}|{nombre}|{apellidos}|{telefono}|"
                            f"{tipo_documento}|{numero_documento}|"
                            f"{direccion}|{codigo_postal}\n"
                        )

                    print("\nDatos guardados exitosamente.")

                elif opcion_datos == "N":
                    print("\nDatos no guardados.")

                else:
                    print("\nOpción inválida.")

            elif opcion == 3:
                print("\nCerrando sesión...")
                sesion_activa = False
                usuario = ""
                contraseña = ""
                break

            elif opcion == 4:
                print("\nSaliendo de mi cuenta.")
                return

            else:
                print("\nOpción inválida.")

        except ValueError:
            print("\nOpción inválida.")


# HOME

def home():
    print("\n¡Bienvenidos a EFRATA MINI-MALL!")
    print("\nModa, alquiler de trajes y arreglos en un solo lugar")
    print("\nModa nacional e importada\n""Trajes para toda ocasión\n""Arreglo de ropa\n")
    print("\nCali, Colombia\n3239655863")
    print("\n¡Será un placer atenderte!\n")


# BUSCAR ROPA

def buscar():
    while True:
        print("\nBUSCAR ROPA")
        print("\n1. Mujer")
        print("2. Hombre")
        print("3. Salir")

        try:
            opcion = int(input("\nSeleccionar: "))

            if opcion == 1:
                sexo = "Mujer"

            elif opcion == 2:
                sexo = "Hombre"

            elif opcion == 3:
                print("\nSaliendo de la búsqueda...")
                break

            else:
                print("\nOpción inválida.")
                continue

            prendas = cargar_ropa()

            # FILTRAR LA ROPA SEGÚN EL SEXO ELEGIDO
            prendas_sexo = [
                prenda for prenda in prendas
                if prenda[2].strip().lower() == sexo.lower()
            ]

            if not prendas_sexo:
                print(f"\nNo hay ropa registrada para {sexo.lower()}.")
                continue

            # OBTENER LOS TIPOS DE PRENDAS SIN REPETIRLOS
            tipos = []

            for prenda in prendas_sexo:
                tipo = prenda[3]
                repetido = False

                for tipo_guardado in tipos:
                    if tipo == tipo_guardado:
                        repetido = True

                if repetido == False:
                    tipos.append(tipo)

            print(f"\nROPA DE {sexo.upper()}")
            print("\nTipos de prendas:")
            print("1. Todas las prendas")

            numero = 2

            for tipo in tipos:
                print(f"{numero}. {tipo}")
                numero = numero + 1

            print(f"{len(tipos) + 2}. Volver")

            try:
                opcion_tipo = int(input("\nSeleccionar tipo: "))

            except ValueError:
                print("\nDebes ingresar un número válido.")
                continue

            if opcion_tipo == len(tipos) + 2:
                continue

            if opcion_tipo == 1:
                prendas_filtradas = prendas_sexo

            elif (
                opcion_tipo >= 2
                and opcion_tipo < len(tipos) + 2
            ):
                numero = 2
                tipo_elegido = ""

                for tipo in tipos:
                    if numero == opcion_tipo:
                        tipo_elegido = tipo

                    numero = numero + 1

                prendas_filtradas = [
                    prenda for prenda in prendas_sexo
                    if prenda[3] == tipo_elegido
                ]

            else:
                print("\nOpción inválida.")
                continue

            print(f"\nRESULTADOS DE ROPA DE {sexo.upper()}")
            print("-" * 45)

            for prenda in prendas_filtradas:
                print(f"Código: {prenda[0]}")
                print(f"Prenda: {prenda[1]}")
                print(f"Sexo: {prenda[2]}")
                print(f"Tipo: {prenda[3]}")
                print(f"Tallas: {prenda[4]}")
                print(f"Precio: ${prenda[5]:,}")
                print(f"Cantidad disponible: {prenda[6]}")
                print(f"Estado: {prenda[7]}")
                print("-" * 45)

        except ValueError:
            print("\nOpción inválida.")


# ALQUILER DE TRAJES

def alquiler_trajes():
    global usuario

    if not sesion_activa:
        print("\nDebes iniciar sesión antes de alquilar un traje.")
        return

    while True:
        print(
            "\nALQUILER DE TRAJES\n"
            "\n1. Ver trajes"
            "\n2. Consultar disponibilidad"
            "\n3. Registrar alquiler"
            "\n4. Consultar mis alquileres"
            "\n5. Devolver traje"
            "\n6. Salir\n"
        )

        try:
            opcion = int(input("Opción: "))

            if opcion == 1:
                mostrar_catalogo()

            elif opcion == 2:
                print("\nCONSULTAR DISPONIBILIDAD")

                actualizar_disponibilidad()

                codigo = input(
                    "Ingrese el código del traje: "
                ).strip()

                trajes = cargar_trajes()
                encontrado = False

                for traje in trajes:
                    if traje[0] == codigo:
                        print(f"{traje[1]}: {traje[4]}")
                        encontrado = True

                if not encontrado:
                    print(
                        "No se encontró un traje con ese código."
                    )

            elif opcion == 3:
                print("\nREGISTRAR ALQUILER\n")
                mostrar_catalogo()

                codigo = input(
                    "\nSeleccione el código del traje: "
                ).strip()

                trajes = cargar_trajes()
                traje_elegido = None

                for traje in trajes:
                    if traje[0] == codigo:
                        traje_elegido = traje
                        break

                if traje_elegido is None:
                    print("Seleccione un traje válido.")
                    continue

                if traje_elegido[4].lower() != "disponible":
                    print("Este traje no está disponible.")
                    continue

                print(f"Traje seleccionado: {traje_elegido[1]}")

                talla = input(
                    "Talla que necesita: "
                ).strip().upper()

                tallas_disponibles = []

                for talla_disponible in traje_elegido[2].split(","):
                    tallas_disponibles.append(
                        talla_disponible.strip().upper()
                    )

                if talla not in tallas_disponibles:
                    print(
                        "La talla no está disponible para este traje."
                    )
                    continue

                fecha_alquiler = input(
                    "Fecha del alquiler (DD/MM/AAAA): "
                ).strip()

                fecha_devolucion = input(
                    "Fecha de devolución (DD/MM/AAAA): "
                ).strip()

                with open(
                    "registraralquiler.txt",
                    "a",
                    encoding="utf-8"
                ) as archivo:
                    archivo.write(
                        f"{usuario}|{codigo}|{traje_elegido[1]}|{talla}|"
                        f"{fecha_alquiler}|{fecha_devolucion}|Activo|"
                        f"{traje_elegido[3]}\n"
                    )

                traje_elegido[4] = "No disponible"

                guardar_trajes(trajes)
                actualizar_disponibilidad()

                print("\nAlquiler registrado exitosamente.")

            elif opcion == 4:
                consultar_alquileres()

            elif opcion == 5:
                devolver_traje()

            elif opcion == 6:
                print("\nSALIENDO...\n")
                return

            else:
                print("\nIngrese una opción válida.\n")

        except ValueError:
            print("\nOpción inválida.\n")


# CONSULTAR ALQUILERES

def consultar_alquileres():
    global usuario

    print("\nMIS ALQUILERES\n")
    encontrados = False

    with open(
        "registraralquiler.txt", "r", encoding="utf-8"
    ) as archivo:
        for linea in archivo:
            datos = linea.strip().split("|")

            if len(datos) == 8 and datos[0] == usuario:
                print(
                    f"Traje: {datos[2]} | Talla: {datos[3]} | "
                    f"Alquiler: {datos[4]} | "
                    f"Devolución: {datos[5]} | "
                    f"Estado: {datos[6]} | "
                    f"Precio: ${int(datos[7]):,}"
                )

                encontrados = True

    if not encontrados:
        print("No tienes alquileres registrados.")


# DEVOLVER TRAJE

def devolver_traje():
    global usuario

    print("\nDEVOLVER TRAJE\n")

    alquileres = []
    activos = []

    with open(
        "registraralquiler.txt", "r", encoding="utf-8"
    ) as archivo:
        for linea in archivo:
            datos = linea.strip().split("|")

            if len(datos) == 8:
                alquileres.append(datos)

                if datos[0] == usuario and datos[6] == "Activo":
                    activos.append(datos)

    if not activos:
        print("No tienes alquileres pendientes de devolución.")
        return

    print("Tus alquileres pendientes:")

    for alquiler in activos:
        print(
            f"Código: {alquiler[1]} | "
            f"Traje: {alquiler[2]} | "
            f"Talla: {alquiler[3]}"
        )

    codigo = input(
        "Seleccione el código del traje que quiere devolver: "
    ).strip()

    alquiler_seleccionado = None

    for alquiler in activos:
        if alquiler[1] == codigo:
            alquiler_seleccionado = alquiler
            break

    if alquiler_seleccionado is None:
        print("No tienes un alquiler activo con ese código.")
        return

    alquiler_seleccionado[6] = "Devuelto"

    with open(
        "registraralquiler.txt", "w", encoding="utf-8"
    ) as archivo:
        for alquiler in alquileres:
            archivo.write("|".join(alquiler) + "\n")

    trajes = cargar_trajes()

    for traje in trajes:
        if traje[0] == codigo:
            traje[4] = "Disponible"
            break

    guardar_trajes(trajes)
    actualizar_disponibilidad()

    print(
        f"\nTraje devuelto exitosamente: "
        f"{alquiler_seleccionado[2]}"
    )
    print("Estado: disponible")


# CARRITO

def carrito():
    print("\nCARRITO")
    print("La funcionalidad del carrito todavía está pendiente.")


# FAVORITOS

def favoritos():
    print("\nFAVORITOS")
    print("La funcionalidad de favoritos todavía está pendiente.")


# MENÚ PRINCIPAL

while True:
    print(
        "\n1. Home"
        "\n2. Buscar"
        "\n3. Alquiler de trajes"
        "\n4. Carrito"
        "\n5. Favoritos"
        "\n6. Cuenta"
        "\n7. Salir\n"
    )

    try:
        opcion = int(input("Ingrese una opción: "))

        if opcion == 1:
            home()

        elif opcion == 2:
            buscar()

        elif opcion == 3:
            alquiler_trajes()

        elif opcion == 4:
            carrito()

        elif opcion == 5:
            favoritos()

        elif opcion == 6:
            sesion()

        elif opcion == 7:
            print("Gracias por visitar EFRATA MINI-MALL.")
            break

        else:
            print("Ingrese una opción válida.")

    except ValueError:
        print("Opción inválida.")