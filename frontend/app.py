import sys
from pathlib import Path
import datetime
from tkinter import messagebox
sys.path.append(str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from backend import authenticate_user, close_session, load_suits, register_rental, current_session, get_user_rentals, return_rental, register_user, read_personal_data, save_personal_data, load_clothing_catalog, filter_clothing_catalog, add_to_cart, get_cart_details, update_cart_quantity, remove_from_cart, prepare_purchase, confirm_purchase, list_purchases, list_favorites, add_favorite, remove_favorite


morado = "#4A2560"
fondo = "#F4F2F7"
blanco = "#FFFFFF"
texto = "#24152E"
gris = "#6A5D74"
borde = "#E1DAE8"
rojo = "#B42318"
verde = "#1D7348"
morado_oscuro = "#3A1C4C"
letra_titulo = "Georgia"
letra_texto = "Segoe UI"

#Crear la ventana 
ventana = ctk.CTk()
ventana.title("EFRATA Mini-Mall")
ventana.geometry("420x760")
ventana.configure(fg_color=fondo)

encabezado = ctk.CTkFrame(ventana, fg_color=morado, corner_radius=0, height=70)
encabezado.pack(fill="x")

tulo = ctk.CTkLabel(encabezado, text="EFRATA Mini-Mall", text_color=blanco, font=ctk.CTkFont(family=letra_titulo, size=22, weight="bold"))
tulo.place(relx=0.5, rely=0.5, anchor="center")

pantalla_login = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)
pantalla_login.pack(fill="both", expand=True)

pantalla_actual = pantalla_login  

def mostrar(pantalla_nueva):
    global pantalla_actual
    pantalla_actual.pack_forget()
    pantalla_nueva.pack(fill="both", expand=True)
    pantalla_actual = pantalla_nueva


#Inicio de sesión
ctk.CTkLabel(pantalla_login, text="Iniciar sesión", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(28, 16))
ctk.CTkLabel(pantalla_login, text="Correo electrónico", text_color=texto, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), anchor="w").pack(fill="x", padx=24)
caja_correo= ctk.CTkEntry(pantalla_login, placeholder_text="tunombre@gmail.com", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
caja_correo.pack(fill="x", padx=24, pady=(6, 14))

ctk.CTkLabel(pantalla_login, text="Contraseña", text_color=texto, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), anchor="w").pack(fill="x", padx=24)
caja_clave= ctk.CTkEntry(pantalla_login, placeholder_text="********", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto, show="*")
caja_clave.pack(fill="x", padx=24, pady=(6, 14))

#Mensaje de error
mensaje= ctk.CTkLabel(pantalla_login, text="", text_color=rojo, font=ctk.CTkFont(family=letra_texto, size=13), wraplength=372, justify="left", anchor="w")
mensaje.pack(fill="x", padx=24)

def entrar():
    correo = caja_correo.get().strip()
    clave = caja_clave.get()

    if correo == "" or clave == "":
        mensaje.configure(text="Correo o contraseña inválidos.", text_color=rojo)
        return

    try:
        correcto = authenticate_user(correo, clave)
    except ValueError as problema:
        mensaje.configure(text=str(problema), text_color=rojo)
        return

    if not correcto:
        mensaje.configure(text="Correo electrónico o contraseña incorrectos", text_color=rojo)
        return

    bienvenida.configure(text=f"Bienvenida, {correo}")
    mostrar(pantalla_menu)

#botón entrar

boton_entrar= ctk.CTkButton(pantalla_login, text="Entrar", command=entrar, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold"))
boton_entrar.pack(fill="x", padx=24, pady=(8, 6))

pantalla_menu = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkLabel(pantalla_menu, text="¿Qué quieres hacer hoy?", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(28, 4))
bienvenida = ctk.CTkLabel(pantalla_menu, text="", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=13), anchor="w")
bienvenida.pack(fill="x", padx=24, pady=(0, 12))

#OPCIONES

def abrir_opcion(nombre):
    if nombre == "Alquilar trajes":
        ver_trajes()
    elif nombre == "Consultar alquileres" or nombre == "Devolver traje":
        ver_alquileres()
    elif nombre == "Mis datos":
        ver_datos()
    elif nombre == "Buscar ropa":
        ver_ropa()
    elif nombre == "Ver carrito":
        ver_carrito()
    elif nombre == "Mis compras":
        ver_compras()
    elif nombre == "Ver favoritos":
        ver_favoritos()
    elif nombre == "Inicio":
        mostrar(pantalla_inicio)     
    else:
        aviso.configure(text=f"La opción '{nombre}' aún no está disponible.", text_color=gris)

for opcion in ["Inicio", "Buscar ropa", "Alquilar trajes", "Consultar alquileres", "Devolver traje", "Ver carrito", "Ver favoritos", "Mis datos", "Mis compras"]:
    ctk.CTkButton(pantalla_menu, text=opcion, command=lambda o=opcion: abrir_opcion(o), height=40, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=24, pady= 4)

aviso = ctk.CTkLabel(pantalla_menu, text="", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=13))
aviso.pack(pady=(6, 0))

def cerrar_sesion():
    close_session()                   
    caja_correo.delete(0, "end")  
    caja_clave.delete(0, "end")         
    mensaje.configure(text="")          
    mostrar(pantalla_login)

ctk.CTkButton(pantalla_menu, text="Cerrar sesión", command=cerrar_sesion, fg_color="transparent", hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(pady=(8, 0))

#Pantalla trajes
pantalla_trajes = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_trajes, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(12, 0))
ctk.CTkLabel(pantalla_trajes, text="Trajes para alquilar", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(4, 12))

lista_trajes = ctk.CTkScrollableFrame(pantalla_trajes, fg_color=fondo)
lista_trajes.pack(fill="both", expand=True, padx=12, pady=(0, 12))

def ver_trajes():
    for tarjeta in lista_trajes.winfo_children():
        tarjeta.destroy()

    trajes = load_suits()
    for codigo, nombre, tallas, precio, estado in trajes:
        tarjeta = ctk.CTkFrame(lista_trajes, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(tarjeta, text=nombre, text_color=texto, anchor="w",  font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(tarjeta, text=f"Código {codigo} · Tallas: {tallas}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=12)).pack(fill="x", padx=14)
        ctk.CTkLabel(tarjeta, text=f"${precio:,}".replace(",", "."), text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=14)
       
        if estado == "Activo":
            texto_estado = "Disponible"
            color_estado = verde
        else:
            texto_estado = "No disponible"
            color_estado = rojo
        ctk.CTkLabel(tarjeta, text=texto_estado, text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")).pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkButton(tarjeta, text="Alquilar", height=36, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold"), command=lambda c=codigo, n=nombre, t=tallas, p=precio: abrir_alquiler(c, n, t, p)).pack(fill="x", padx=14, pady=(0, 12))

    mostrar(pantalla_trajes)

pantalla_alquiler = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_alquiler, text="← Volver a los trajes", command=lambda: mostrar(pantalla_trajes), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(12, 0))
ctk.CTkLabel(pantalla_alquiler, text="Alquilar traje", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(0, 12))

#Traje seleccionado
traje_seleccionado = ctk.CTkLabel(pantalla_alquiler, text="", text_color=texto, anchor="w", justify= "left", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold"))
traje_seleccionado.pack(fill="x", padx=24, pady=(0, 16))

#Tallas
ctk.CTkLabel(pantalla_alquiler, text="Talla", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=24)
selector_talla = ctk.CTkOptionMenu(pantalla_alquiler, values=[""], height= 40, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, font=ctk.CTkFont(family=letra_texto, size=14))
selector_talla.pack(fill="x", padx=24, pady=(6, 14))

#Fechas de alquiler
ctk.CTkLabel(pantalla_alquiler, text="Fecha de alquiler", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=24)
caja_fecha1 = ctk.CTkEntry(pantalla_alquiler, placeholder_text="dd/mm/aaaa", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
caja_fecha1.pack(fill="x", padx=24, pady=(6, 14))

ctk.CTkLabel(pantalla_alquiler, text="Fecha de devolución", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=24)
caja_fecha2 = ctk.CTkEntry(pantalla_alquiler, placeholder_text="dd/mm/aaaa", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
caja_fecha2.pack(fill="x", padx=24, pady=(6, 14))

#Error o mensaje de éxito
mensaje_alquiler = ctk.CTkLabel(pantalla_alquiler, text="", text_color=rojo, wraplength=372, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_alquiler.pack(fill="x", padx=24)

#Formulario
codigo_elegido = ""

def abrir_alquiler(codigo, nombre, tallas, precio):
    global codigo_elegido
    codigo_elegido = codigo

    precio_texto = f"${precio:,}".replace(",", ".")
    traje_seleccionado.configure(text=f"{nombre}\n{precio_texto}")

    lista_tallas = tallas.split(", ")
    selector_talla.configure(values=lista_tallas)
    selector_talla.set("Elija una talla")

    caja_fecha1.delete(0, "end")
    caja_fecha2.delete(0, "end")
    mensaje_alquiler.configure(text="")
    mostrar(pantalla_alquiler)

#Confrimar alquiler
def confirmar_alquiler():
    talla = selector_talla.get()
    fecha1 = caja_fecha1.get().strip()
    fecha2 = caja_fecha2.get().strip()

    if talla == "Elija una talla":
        mensaje_alquiler.configure(text="Elija una talla.", text_color=rojo)
        return

    try:
        datetime.datetime.strptime(fecha1, "%d/%m/%Y")
        datetime.datetime.strptime(fecha2, "%d/%m/%Y")
    except ValueError:
        mensaje_alquiler.configure(text="Formato de fecha inválido. Use dd/mm/aaaa.", text_color=rojo)
        return

    try:
        alquiler= register_rental (current_session.email, codigo_elegido, talla, fecha1, fecha2)
    except ValueError as problema:
        mensaje_alquiler.configure(text=str(problema), text_color=rojo)
        return

    mensaje_alquiler.configure(
        text=f"¡Alquiler registrado exitosamente!\n{alquiler['Nombre']} · Talla {alquiler['Talla']}\nDel {alquiler['FechaAlquiler']} al {alquiler['FechaProgramada']}",
        text_color= verde)

bonton_confirmar = ctk.CTkButton(pantalla_alquiler, text="Confirmar alquiler", command=confirmar_alquiler, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold"))
bonton_confirmar.pack(fill="x", padx=24, pady=(8, 6))

#Mis alquileres
pantalla_alquileres = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

boton_volver_menu2 = ctk.CTkButton(pantalla_alquileres, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold"))
boton_volver_menu2.pack(fill="x", padx=16, pady=(16, 0))

titulo_alquileres = ctk.CTkLabel(pantalla_alquileres, text="Mis alquileres", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold"), anchor="w")
titulo_alquileres.pack(fill="x", padx=24, pady=(4, 10))

mensaje_devolucion = ctk.CTkLabel(pantalla_alquileres, text="", text_color=verde, wraplength=372, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_devolucion.pack(fill="x", padx=24)


lista_alquileres = ctk.CTkScrollableFrame(pantalla_alquileres, fg_color=fondo)
lista_alquileres.pack(fill="both", expand=True, padx=12, pady=(0,16))

def ver_alquileres():
    mensaje_devolucion.configure(text="")
    for tarjeta in lista_alquileres.winfo_children():
        tarjeta.destroy()

    alquileres = get_user_rentals(current_session.email)

    if len (alquileres)== 0:
        ctk.CTkLabel(lista_alquileres, text="Todavía no tienes alquileres.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for alquiler in alquileres:
        tarjeta = ctk.CTkFrame(lista_alquileres, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(tarjeta, text=alquiler["Nombre"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(tarjeta, text=f"Talla: {alquiler['Talla']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)
        ctk.CTkLabel(tarjeta, text=f"Del {alquiler['FechaAlquiler']} al {alquiler['FechaProgramada']}", text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)

        if alquiler["Estado"] == "Activo":
            color_estado= verde
            ctk.CTkButton(tarjeta, text="Devolver traje", height=36, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold"), command=lambda i=alquiler["IndiceArchivo"]: devolver(i)).pack(fill="x", padx=14, pady=(0, 12))

        else:
            color_estado = gris
        ctk.CTkLabel(tarjeta, text=alquiler["Estado"], text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=14, pady=(2, 12))

    mostrar(pantalla_alquileres)

#Devolver traje
def devolver(indice):
    try:
        traje= return_rental(current_session.email, indice)
    except ValueError as problema:
        mensaje_devolucion.configure(text=str(problema), text_color=rojo)
        return
    
    ver_alquileres()
    mensaje_devolucion.configure(text=f"¡{traje['Nombre']} devuelto exitosamente el {traje['FechaReal']}!", text_color=verde) 

#CREAR CUENTA
pantalla_registro = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkLabel(pantalla_registro, text="Crear cuenta", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(28, 16))

ctk.CTkLabel(pantalla_registro, text="Correo electrónico", text_color=texto, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), anchor="w").pack(fill="x", padx=24)
registro_correo = ctk.CTkEntry(pantalla_registro, placeholder_text="tunombre@gmail.com", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
registro_correo.pack(fill="x", padx=24, pady=(6, 14))

ctk.CTkLabel(pantalla_registro, text="Contraseña", text_color=texto, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), anchor="w").pack(fill="x", padx=24)
registro_clave = ctk.CTkEntry(pantalla_registro, placeholder_text="Mínimo 8, con mayúscula, minúscula y número", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto, show="*")
registro_clave.pack(fill="x", padx=24, pady=(6, 14))


ctk.CTkLabel(pantalla_registro, text="Repite la contraseña", text_color=texto, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), anchor="w").pack(fill="x", padx=24)
registro_clave2 = ctk.CTkEntry(pantalla_registro, placeholder_text="********", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto, show="*")
registro_clave2.pack(fill="x", padx=24, pady=(6, 14))

mensaje_registro = ctk.CTkLabel(pantalla_registro, text="", text_color=rojo, font=ctk.CTkFont(family=letra_texto, size=13), wraplength=372, justify="left", anchor="w")
mensaje_registro.pack(fill="x", padx=24)


def crear_cuenta():
    correo = registro_correo.get().strip()
    clave = registro_clave.get()
    clave2 = registro_clave2.get()

    if clave != clave2:
        mensaje_registro.configure(text="Las dos contraseñas no son iguales.")
        return
    
    try:
        register_user(correo, clave)
    except ValueError as problema:
        mensaje_registro.configure(text=str(problema))
        return

    bienvenida.configure(text=f"Bienvenida, {correo}")
    mostrar(pantalla_menu)

ctk.CTkButton(pantalla_registro, text="Crear cuenta", command=crear_cuenta, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=24, pady=(8, 6))
ctk.CTkButton(pantalla_registro, text="¿Ya tienes cuenta? Inicia sesión", command=lambda: mostrar(pantalla_login), fg_color="transparent", hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(pady=(4, 0))

def ir_a_registro():
    registro_correo.delete(0, "end")
    registro_clave.delete(0, "end")
    registro_clave2.delete(0, "end")
    mensaje_registro.configure(text="")
    mostrar(pantalla_registro)

ctk.CTkButton(pantalla_login, text="¿Primera vez aquí? Crea una cuenta", command=ir_a_registro, fg_color="transparent", hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(pady=(4, 0))

#MIS DATOS

pantalla_datos = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_datos, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_datos, text="Mis datos", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

formulario = ctk.CTkScrollableFrame(pantalla_datos, fg_color=fondo)
formulario.pack(fill="both", expand=True, padx=8, pady=(0, 16))

def campo(etiqueta, ejemplo):
    ctk.CTkLabel(formulario, text=etiqueta, text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=16)
    caja = ctk.CTkEntry(formulario, placeholder_text=ejemplo, height=42, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
    caja.pack(fill="x", padx=16, pady=(6, 12))
    return caja

caja_nombre = campo("Nombre", "Ej: Isabella")
caja_apellidos = campo("Apellidos", "Ej: Caro López")
caja_telefono = campo("Teléfono", "10 dígitos")

ctk.CTkLabel(formulario, text="Tipo de documento", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=16)
selector_documento = ctk.CTkOptionMenu(formulario, values=["CC", "CE", "NIT"], height=42, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
selector_documento.pack(fill="x", padx=16, pady=(6, 12))

caja_documento = campo("Número de documento", "Solo números")
caja_direccion = campo("Dirección", "Ej: Calle 5 # 10-20")
caja_postal = campo("Código postal", "6 dígitos")

mensaje_datos = ctk.CTkLabel(formulario, text="", text_color=rojo, wraplength=340, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_datos.pack(fill="x", padx=16)


def llenar(caja, valor):
    caja.delete(0, "end")
    if valor:
        caja.insert(0, valor)

def ver_datos():
    datos = read_personal_data(current_session.email)
    if datos is None:     
        datos = {}

    llenar(caja_nombre, datos.get("Nombre", ""))
    llenar(caja_apellidos, datos.get("Apellidos", ""))
    llenar(caja_telefono, datos.get("Telefono", ""))
    selector_documento.set(datos.get("TipoDocumento", "CC"))
    llenar(caja_documento, datos.get("NumeroDocumento", ""))
    llenar(caja_direccion, datos.get("Direccion", ""))
    llenar(caja_postal, datos.get("CodigoPostal", ""))

    mensaje_datos.configure(text="")
    mostrar(pantalla_datos)

def guardar_datos():
    datos = {
        "Nombre": caja_nombre.get(),
        "Apellidos": caja_apellidos.get(),
        "Telefono": caja_telefono.get(),
        "TipoDocumento": selector_documento.get(),
        "NumeroDocumento": caja_documento.get(),
        "Direccion": caja_direccion.get(),
        "CodigoPostal": caja_postal.get(),
    }

    try:
        save_personal_data(current_session.email, datos)
    except ValueError as problema:
        mensaje_datos.configure(text=str(problema), text_color=rojo)
        return

    mensaje_datos.configure(text="¡Datos guardados exitosamente!", text_color=verde)

ctk.CTkButton(formulario, text="Guardar datos", command=guardar_datos, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=16, pady=(8, 12))

#BUSCAR ROPA
pantalla_buscar = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_buscar, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_buscar, text="Buscar ropa", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

filtros = ctk.CTkFrame(pantalla_buscar, fg_color=fondo)
filtros.pack(fill="x", padx=24, pady=(0, 8))

selector_seccion = ctk.CTkOptionMenu(filtros, values=["Todas", "Mujer", "Hombre", "Unisex"], command=lambda valor: mostrar_ropa(), width=170, height=38, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
selector_seccion.pack(side="left", padx=(0, 8))

selector_tipo = ctk.CTkOptionMenu(filtros, values=["Todos"], command=lambda valor: mostrar_ropa(), width=170, height=38, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
selector_tipo.pack(side="left")

mensaje_buscar = ctk.CTkLabel(pantalla_buscar, text="", text_color=rojo, wraplength=372, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_buscar.pack(fill="x", padx=24)

lista_ropa = ctk.CTkScrollableFrame(pantalla_buscar, fg_color=fondo)
lista_ropa.pack(fill="both", expand=True, padx=16, pady=(0, 16))

catalogo = []

def ver_ropa():
    global catalogo
    mensaje_buscar.configure(text="")
    try:
        catalogo = load_clothing_catalog()
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema))
        catalogo = []

    tipos = ["Todos"]
    for producto in catalogo:
        if producto["Tipo"] not in tipos:
            tipos.append(producto["Tipo"])
    selector_tipo.configure(values=tipos)

    selector_seccion.set("Todas")
    selector_tipo.set("Todos")
    mostrar_ropa()
    mostrar(pantalla_buscar)

def mostrar_ropa():
    for tarjeta in lista_ropa.winfo_children():
        tarjeta.destroy()

    seccion = selector_seccion.get()
    tipo = selector_tipo.get()
    if seccion == "Todas":
        seccion = None
    if tipo == "Todos":
        tipo = None

    productos = filter_clothing_catalog(catalogo, seccion, tipo)

    if len(productos) == 0:
        ctk.CTkLabel(lista_ropa, text="No hay prendas con esos filtros.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for producto in productos:
        tarjeta = ctk.CTkFrame(lista_ropa, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        texto_tallas = ""
        tallas_disponibles = []
        for talla in producto["Tallas"]:
            if talla["Cantidad"] > 0:
                texto_tallas = texto_tallas + talla["Talla"] + "   "
                tallas_disponibles.append(talla["Talla"])

        precio_texto = f"${producto['Precio']:,.0f}".replace(",", ".")

        ctk.CTkLabel(tarjeta, text=producto["Nombre"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(tarjeta, text=f"{producto['Seccion']} · {producto['Tipo']} · Código {producto['Codigo']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)
        ctk.CTkLabel(tarjeta, text=f"Tallas: {texto_tallas}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)
        ctk.CTkLabel(tarjeta, text=precio_texto, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=14, pady=(4, 0))

        if producto["Disponibilidad"] == "Disponible":
            color_estado = verde
        else:
            color_estado = rojo
        ctk.CTkLabel(tarjeta, text=producto["Disponibilidad"], text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=14, pady=(2, 12))

        if len(tallas_disponibles) > 0:
            fila = ctk.CTkFrame(tarjeta, fg_color=blanco)
            fila.pack(fill="x", padx=14, pady=(0, 12))

            selector = ctk.CTkOptionMenu(fila, values=tallas_disponibles, width=90, height=36, corner_radius=10, fg_color=fondo, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
            selector.pack(side="left", padx=(0, 8))

            ctk.CTkButton(fila, text="Agregar al carrito", height=36, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold"), command=lambda c=producto["Codigo"], s=selector: agregar_carrito(c, s.get())).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(tarjeta, text="♡ Agregar a favoritos", height=30, fg_color="transparent", hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), command=lambda c=producto["Codigo"]: agregar_favorito(c)).pack(anchor="w", padx=8, pady=(0, 10))
#AGREGAR AL CARRITO

def agregar_carrito(codigo, talla):
    try:
        cantidad = add_to_cart(current_session.email, codigo, talla, 1, catalogo)
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema), text_color=rojo)
        return

    mensaje_buscar.configure(text=f"¡Agregado al carrito! (talla {talla}, llevas {cantidad})", text_color=verde)

def pesos(valor):
    return f"${valor:,.0f}".replace(",", ".")

#VER MI CARRITO 

pantalla_carrito = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_carrito, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_carrito, text="Mi carrito", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

mensaje_carrito = ctk.CTkLabel(pantalla_carrito, text="", text_color=rojo, wraplength=372, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_carrito.pack(fill="x", padx=24)

lista_carrito = ctk.CTkScrollableFrame(pantalla_carrito, fg_color=fondo)
lista_carrito.pack(fill="both", expand=True, padx=16, pady=(0, 8))

total_carrito = ctk.CTkLabel(pantalla_carrito, text="", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=18, weight="bold"))
total_carrito.pack(fill="x", padx=24, pady=(0, 8))


def ver_carrito():
    mensaje_carrito.configure(text="")
    for tarjeta in lista_carrito.winfo_children():
        tarjeta.destroy()

    detalles = get_cart_details(current_session.email)
    total=0

    if len(detalles) == 0:
        ctk.CTkLabel(lista_carrito, text="Tu carrito está vacío.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for detalle in detalles:
        tarjeta = ctk.CTkFrame(lista_carrito, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(tarjeta, text=detalle["Nombre"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(tarjeta, text=f"Talla: {detalle['Talla']} · Código {detalle['Codigo']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)

        if detalle ["Subtotal"] is None:
            subtotal_texto = "Precio no disponible"
        else:
            subtotal_texto = f"{pesos(detalle['Precio'])} c/u · Subtotal {pesos(detalle['Subtotal'])}"
            total = total + detalle["Subtotal"]
        ctk.CTkLabel(tarjeta, text=subtotal_texto, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=14, pady=(4, 0))

        if detalle["Aviso"]!= "":
            ctk.CTkLabel(tarjeta, text=detalle["Aviso"], text_color=rojo, wraplength=320, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=12)).pack(fill="x", padx=14)

        fila = ctk.CTkFrame(tarjeta, fg_color=blanco)
        fila.pack(fill="x", padx=14, pady=(8, 12))

        ctk.CTkButton(fila, text="−", width=36, height=32, corner_radius=8, fg_color=fondo, hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=16, weight="bold"), command=lambda c=detalle["Codigo"], t=detalle["Talla"], n=detalle["Cantidad"] - 1: cambiar_cantidad(c, t, n)).pack(side="left")
        ctk.CTkLabel(fila, text=str(detalle["Cantidad"]), width=36, text_color=texto, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(side="left")
        ctk.CTkButton(fila, text="+", width=36, height=32, corner_radius=8, fg_color=fondo, hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=16, weight="bold"), command=lambda c=detalle["Codigo"], t=detalle["Talla"], n=detalle["Cantidad"] + 1: cambiar_cantidad(c, t, n)).pack(side="left")

        ctk.CTkButton(fila, text="Quitar", width=70, height=32, fg_color="transparent", hover_color=borde, text_color=rojo, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), command=lambda c=detalle["Codigo"], t=detalle["Talla"]: quitar(c, t)).pack(side="right")

    total_carrito.configure(text=f"Total: {pesos(total)}")
    mostrar(pantalla_carrito)

def cambiar_cantidad(codigo,talla,nueva):
    if nueva < 0:
        quitar(codigo, talla)
        return
    try:
        update_cart_quantity(current_session.email, codigo, talla, nueva)
    except ValueError as problema:
        mensaje_carrito.configure(text=str(problema), text_color=rojo)
        return
    ver_carrito()

def quitar(codigo, talla):
    remove_from_cart(current_session.email, codigo, talla)
    ver_carrito()

#CONFIRMAR COMPRA

def comprar():
    detalles, total, error = prepare_purchase(current_session.email)
    if error:
        mensaje_carrito.configure(text=error, text_color=rojo)
        return

    respuesta = messagebox.askyesno("Confirmar compra", f"¿Desea confirmar la compra por {pesos(total)}?")

    resultado = confirm_purchase(current_session.email, respuesta)

    if resultado["ok"]:
        ver_carrito()
        mensaje_carrito.configure(text=f"¡Compra confirmada! Pedido {resultado['pedido']}", text_color=verde)
    else:
        mensaje_carrito.configure(text=resultado["message"], text_color=rojo)

ctk.CTkButton(pantalla_carrito, text="Confirmar compra", command=comprar, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=24, pady=(0, 16))


#MIS COMPRAS
pantalla_compras = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_compras, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_compras, text="Mis compras", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

lista_compras = ctk.CTkScrollableFrame(pantalla_compras, fg_color=fondo)
lista_compras.pack(fill="both", expand=True, padx=16, pady=(0, 16))

def ver_compras():
    for tarjeta in lista_compras.winfo_children():
        tarjeta.destroy()

    pedidos = list_purchases(current_session.email)

    if len(pedidos) == 0:
        ctk.CTkLabel(lista_compras, text="Aún no tienes compras registradas.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for pedido in pedidos:
        tarjeta = ctk.CTkFrame(lista_compras, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(tarjeta, text=pedido["Fecha"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(tarjeta, text=f"Pedido {pedido['Pedido']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=11)).pack(fill="x", padx=14, pady=(0, 6))

        for articulo in pedido["Articulos"]:
            ctk.CTkLabel(tarjeta, text=f"• {articulo['Nombre']} (talla {articulo['Talla']}) x{articulo['Cantidad']}  —  {pesos(articulo['Subtotal'])}", text_color=texto, anchor="w", justify="left", wraplength=320, font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)

        ctk.CTkLabel(tarjeta, text=f"Total: {pesos(pedido['Total'])}", text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=14, pady=(6, 12))

    mostrar(pantalla_compras)

#FAVORITOS

def agregar_favorito(codigo):
    try:
        add_favorite(current_session.email, codigo)
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema), text_color=rojo)
        return
    mensaje_buscar.configure(text="¡Agregado a favoritos! ♡", text_color=verde)

pantalla_favoritos = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_favoritos, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_favoritos, text="Mis favoritos", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

lista_favoritos = ctk.CTkScrollableFrame(pantalla_favoritos, fg_color=fondo)
lista_favoritos.pack(fill="both", expand=True, padx=16, pady=(0, 16))


def ver_favoritos():
    for tarjeta in lista_favoritos.winfo_children():
        tarjeta.destroy()

    favoritos = list_favorites(current_session.email)

    if len(favoritos) == 0:
        ctk.CTkLabel(lista_favoritos, text="No tienes productos favoritos.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for favorito in favoritos:
        tarjeta = ctk.CTkFrame(lista_favoritos, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        if favorito["EstadoFavorito"] == "Activo":
            ctk.CTkLabel(tarjeta, text=favorito["Nombre"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
            ctk.CTkLabel(tarjeta, text=f"{favorito['Seccion']} · {favorito['Tipo']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)
            ctk.CTkLabel(tarjeta, text=pesos(favorito["Precio"]), text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=14, pady=(4, 0))
            if favorito["Disponibilidad"] == "Disponible":
                color_estado = verde
            else:
                color_estado = rojo
            ctk.CTkLabel(tarjeta, text=favorito["Disponibilidad"], text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=14)
        else:
            # El producto ya no está en el catálogo
            ctk.CTkLabel(tarjeta, text=f"{favorito['Nombre']} ({favorito['Codigo']})", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
            ctk.CTkLabel(tarjeta, text="Ya no está disponible en la tienda.", text_color=rojo, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)

        ctk.CTkButton(tarjeta, text="Quitar de favoritos", height=30, fg_color="transparent", hover_color=borde, text_color=rojo, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), command=lambda c=favorito["Codigo"]: quitar_favorito(c)).pack(anchor="w", padx=8, pady=(4, 10))

    mostrar(pantalla_favoritos)


def quitar_favorito(codigo):
    remove_favorite(current_session.email, codigo)
    ver_favoritos()

#INICIO

pantalla_inicio = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_inicio, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))

ctk.CTkLabel(pantalla_inicio, text="¡Bienvenidos a\nEFRATA Mini-Mall!", text_color=morado, justify="center", font=ctk.CTkFont(family=letra_titulo, size=28, weight="bold")).pack(pady=(24, 8))
ctk.CTkLabel(pantalla_inicio, text="Moda, alquiler de trajes y arreglos\nen un solo lugar", text_color=gris, justify="center", font=ctk.CTkFont(family=letra_texto, size=15)).pack(pady=(0, 20))

servicios = ctk.CTkFrame(pantalla_inicio, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
servicios.pack(fill="x", padx=24, pady=(0, 16))
for servicio in ["👗  Moda nacional e importada", "🤵  Trajes para toda ocasión", "🧵  Arreglo de ropa"]:
    ctk.CTkLabel(servicios, text=servicio, text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15)).pack(fill="x", padx=18, pady=8)

contacto = ctk.CTkFrame(pantalla_inicio, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
contacto.pack(fill="x", padx=24, pady=(0, 16))
ctk.CTkLabel(contacto, text="📍  Cali, Colombia", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15)).pack(fill="x", padx=18, pady=(12, 4))
ctk.CTkLabel(contacto, text="📞  323 965 5863", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15)).pack(fill="x", padx=18, pady=(4, 12))

ctk.CTkLabel(pantalla_inicio, text="¡Será un placer atenderte! 💜", text_color=morado, font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(pady=(8, 0))



def run():
    ventana.mainloop()


if __name__ == "__main__":
    run()



