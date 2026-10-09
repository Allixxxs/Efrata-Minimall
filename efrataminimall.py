# CREAR AUTOMÁTICAMENTE LOS ARCHIVOS TXT SI NO EXISTEN
for nombre_archivo in ["trajesdisponibles.txt", "consultardisponibilidad.txt", "registraralquiler.txt"]:
    with open(nombre_archivo, "a", encoding="utf-8"):
        pass


usuario = ""
contraseña = ""
sesion_activa = False

def sesion():
    global sesion_activa, usuario, contraseña 

    while True:
        print("\nEFRATA MINI-MALL")
        print("Inicia sesión o crea tu cuenta\n")

        usuario_provisional = input("E-MAIL: ")

        if not (usuario_provisional.endswith("@gmail.com") or usuario_provisional.endswith("@hotmail.com")):
            print("El formato de e-mail no es válido")
            continue

        if usuario_provisional == usuario and usuario != "":
            print(f"\nINICIAR SESIÓN\nE-MAIL: {usuario_provisional}")
            contraseña_provisional = input("CONTRASEÑA: ")
            if contraseña_provisional == contraseña:
                print("\nInicio de sesión exitoso")
                sesion_activa = True
                cuenta()
                return
            else:
                print("\nLa combinación de usuario y contraseña no es correcta")

        else:
            print(f"\nCREAR CUENTA\nE-MAIL: {usuario_provisional}")
            contraseña_provisional = input("CONTRASEÑA (Mínimo 8 caracteres incluyendo minúscula, mayúscula y un número): ")

            tiene_mayus = False
            tiene_minus = False
            tiene_num = False

            for i in range(len(contraseña_provisional)):
                letra = contraseña_provisional[i]

                if letra.isupper():
                    tiene_mayus = True
                if letra.islower():
                    tiene_minus = True
                if letra.isdigit():
                    tiene_num = True

            if len(contraseña_provisional) >= 8 and tiene_mayus and tiene_minus and tiene_num:
                usuario = usuario_provisional
                contraseña = contraseña_provisional
                sesion_activa = True
                print("\nCuenta creada exitosamente")
                break
            else:
                print("\nContraseña inválida")

def cuenta():
    global sesion_activa

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
                print("\nAún no tienes compras online")
            elif opcion == 2:
                print("\nDATOS PERSONALES")
                nombre = input("Nombre: ")
                apellidos = input("Apellidos: ")
                telefono = input("Teléfono (+57): ")

                print("\nDIRECCIÓN DE FACTURACIÓN")
                tipo_documento = input("Tipo de documento (CC, CE, NIT): ")
                numero_documento = int(input("Número de documento: "))
                direccion = input("Dirección (calle y número): ")
                direccion_complemento = input("Escalera, piso... (opcional): ")
                codigo_postal = int(input("Código postal: "))

                print("\nDATOS DE LA CUENTA")
                print(f"{usuario}, CAMBIAR")
                print(f"{contraseña}, CAMBIAR")
                print("Eliminar cuenta")
            elif opcion == 3:
                print("\nCerrar sesión") 
                sesion_activa = False
                break
            elif opcion == 4:
                print("\nSaliendo")
                return
            else:
                print("\nOpción inválida")

        except ValueError:
            print("Opción invalida")

def home():
    global sesion_activa, usuario, contraseña
    print("\nSección home")

def buscar():
    global sesion_activa, usuario, contraseña
    while True: 
        print("\n1. Mujer\n2. Hombre\n3. Salir\n")
        try:
            opcion = int(input("Seleccionar: "))
            if opcion == 1:
                print("\nRopa de mujer")
            elif opcion == 2:
                print("\nRopa de hombre")
            elif opcion == 3:
                print("\nSaliendo")
                break
            else:
                print("\nOpción inválida")
        except ValueError:
            print("\nOpción inválida")

def alquiler_trajes():
    while True: 
        print("\nALQUILER DE TRAJES\n")
        print("1. Ver trajes\n2. Consultar disponibilidad\n3. Registrar alquiler\n4. Consultar mis alquileres\n5. Devolver traje\n6. Salir\n")

        try:
            opcion = int(input("Opción: "))

            if opcion == 1:
                print("\nVER TRAJES\n")
                try: 
                    with open("trajesdisponibles.txt", 'r', encoding='utf-8') as archivo:
                        catalogo = archivo.read()
                    print(f"CATÁLOGO: \n{catalogo}")
                except FileNotFoundError:
                    pass
                    return

            elif opcion == 2:
                print("\nCONSULTAR DISPONIBILIDAD\n")
                try:
                    with open("consultardisponibilidad.txt", 'r', encoding='utf-8') as archivo: 
                        disponibilidad = archivo.read()
                    print(f"DISPONIBILIDAD: \n{disponibilidad}")
                except FileNotFoundError:
                    pass
                    return

            elif opcion == 3: 
                print("\nREGISTRAR ALQUILER\n")
                try:
                    with open("consultardisponibilidad.txt", 'r', encoding='utf-8') as archivo:
                        disponibilidad = archivo.read()
                    print(disponibilidad)
                except FileNotFoundError:
                    print("No se encontró el archivo de disponibilidad.")
                try: 
                    registrar = int(input("\nSeleccione el traje: "))
                except ValueError:
                    print("Seleccione un traje válido")
                fecha_alquiler = input("\nFecha del alquiler: ")
                fecha_devolucion = input("Fecha de devolución: ")

                with open("registraralquiler.txt", 'a', encoding='utf-8') as archivo: 
                    archivo.write(f"\nHas alquilado el traje: {registrar}; desde el {fecha_alquiler} hasta el {fecha_devolucion}.\n")

                print("\nAlquiler registrado exitosamente")

            elif opcion == 4:
                print("\nMIS ALQUILERES\n")
                with open("registraralquiler.txt", 'r', encoding='utf-8') as archivo:
                    alquilados = archivo.read()
                print(f"Trajes alquilados: \n{alquilados}")

            elif opcion == 5:
                print("\nDEVOLVER TRAJE\n")
                with open("registraralquiler.txt", 'r', encoding='utf-8') as archivo:
                    registro = (archivo.read())
                print(registro)
                try:
                    devolucion = int(input("Seleccione el traje que quiere devolver: "))
                except ValueError: 
                    print("Seleccione un traje válido")
                else:
                    with open("registraralquiler.txt", 'a', encoding='utf-8') as archivo:
                        archivo.write(f"Traje devuelto: {devolucion}; estado: disponible.\n")

                print(f"\nTraje devuelto exitosamente. Se ha develto el traje: {devolucion}\n")
                print("\nEstado: disponible")

            elif opcion == 6:
                print("\nSALIENDO...\n")
                return
            else:
                print("\nIngrese una opción válida\n")
        except ValueError:
            print("\nOpción inválida\n")

def carrito():
    global sesion_activa, usuario, contraseña
    print("Carrito")

def favoritos():
    global sesion_activa, usuario, contraseña
    print("Favoritos")


while True:
    print("\n¡Bienvenidos a EFRATA MINI-MALL!")
    print("\nModa, alquiler de trajes y arreglos en un solo lugar")
    print("\nModa nacional e importada\nTrajes para toda ocasión\nArreglo de ropa")
    print("\nCali, Colombia\n3239655863")
    print("\n¡Será un placer atenderte!\n")

    print("\n1. Home\n2. Buscar\n3. Alquiler de trajes\n4. Carrito\n5. Favoritos\n6. Cuenta\n")

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

        else:
            print("Ingrese una opción válida")

    except ValueError:
        print("Opción inválida")