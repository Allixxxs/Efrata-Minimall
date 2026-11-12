import sys
import shutil
import logging
from pathlib import Path
import datetime
from tkinter import filedialog, messagebox
sys.path.append(str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from PIL import Image, ImageOps
from tkcalendar import Calendar
from backend import (
    autenticar_usuario, cerrar_sesion, cargar_trajes, registrar_alquiler,
    sesion_actual, obtener_alquileres_usuario, devolver_alquiler,
    registrar_usuario, leer_datos_personales, guardar_datos_personales,
    cargar_catalogo_ropa, filtrar_catalogo_ropa, agregar_al_carrito,
    obtener_detalles_carrito, actualizar_cantidad_carrito, eliminar_del_carrito,
    preparar_compra, confirmar_compra, listar_compras, listar_favoritos,
    agregar_favorito, eliminar_favorito, cargar_descripciones_trajes,
    es_administrador, cargar_inventario_administracion,
    listar_clientes_administracion, listar_compras_administracion,
    listar_alquileres_administracion, obtener_estadisticas_administracion,
    registrar_producto, actualizar_producto, agregar_variante_existencias,
    actualizar_existencias, desactivar_producto,
    cargar_trajes_administracion, registrar_traje, actualizar_traje,
)

logger = logging.getLogger(__name__)

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
    if pantalla_nueva is globals().get("pantalla_admin"):
        encabezado.pack_forget()
    elif not encabezado.winfo_manager():
        encabezado.pack(fill="x")
    pantalla_nueva.pack(fill="both", expand=True)
    pantalla_actual = pantalla_nueva

carpeta_imagenes = Path(__file__).resolve().parent / "imagenes"

iconos_ropa = {"Blusa": "👚", "Vestido": "👗", "Camisa": "👔", "Pantalón": "👖", "Chaqueta": "🧥", "Falda": "👗"}

def mostrar_foto_producto(contenedor, codigo, icono):
    ruta = None
    for extension in [".jpg", ".jpeg", ".png"]:
        posible = carpeta_imagenes / (codigo + extension)
        if posible.exists():
            ruta = posible

    if ruta is None:
        recuadro = ctk.CTkFrame(contenedor, fg_color=borde, corner_radius=10, height=220)
        recuadro.pack(fill="x", padx=14, pady=(14, 4))
        recuadro.pack_propagate(False)
        ctk.CTkLabel(recuadro, text=icono, font=ctk.CTkFont(size=50)).pack(expand=True)
        return

    imagen = Image.open(ruta)
    imagen = ImageOps.pad(imagen, (620, 440), color=blanco)   # la foto completa, centrada, sin recortar
    foto = ctk.CTkImage(light_image=imagen, size=(310, 220))
    ctk.CTkLabel(contenedor, image=foto, text="").pack(padx=14, pady=(14, 4))

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

def iniciar_sesion_interfaz():
    correo = caja_correo.get().strip()
    clave = caja_clave.get()

    if correo == "" or clave == "":
        mensaje.configure(text="Correo o contraseña inválidos.", text_color=rojo)
        return

    try:
        correcto = autenticar_usuario(correo, clave)
    except ValueError as problema:
        mensaje.configure(text=str(problema), text_color=rojo)
        return

    if not correcto:
        mensaje.configure(text="Correo electrónico o contraseña incorrectos", text_color=rojo)
        return

    bienvenida.configure(text=f"Bienvenida, {correo}")
    if es_administrador(correo):
        boton_panel_admin.pack(fill="x", padx=24, pady=4, before=boton_cerrar_sesion)
    else:
        boton_panel_admin.pack_forget()
    mostrar(pantalla_menu)

#botón entrar

boton_entrar= ctk.CTkButton(pantalla_login, text="Entrar", command=iniciar_sesion_interfaz, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold"))
boton_entrar.pack(fill="x", padx=24, pady=(8, 6))

pantalla_menu = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkLabel(pantalla_menu, text="¿Qué quieres hacer hoy?", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(28, 4))
bienvenida = ctk.CTkLabel(pantalla_menu, text="", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=13), anchor="w")
bienvenida.pack(fill="x", padx=24, pady=(0, 12))

#OPCIONES

def abrir_opcion_menu(nombre):
    if nombre == "Alquilar trajes":
        mostrar_trajes()
    elif nombre == "Consultar alquileres" or nombre == "Devolver traje":
        mostrar_alquileres()
    elif nombre == "Mis datos":
        mostrar_datos_personales()
    elif nombre == "Buscar ropa":
        mostrar_catalogo_ropa()
    elif nombre == "Ver carrito":
        mostrar_carrito()
    elif nombre == "Mis compras":
        mostrar_compras()
    elif nombre == "Ver favoritos":
        mostrar_favoritos()
    elif nombre == "Inicio":
        mostrar(pantalla_inicio)
    else:
        aviso.configure(text=f"La opción '{nombre}' aún no está disponible.", text_color=gris)

for opcion in ["Inicio", "Buscar ropa", "Alquilar trajes", "Consultar alquileres", "Devolver traje", "Ver carrito", "Ver favoritos", "Mis datos", "Mis compras"]:
    ctk.CTkButton(pantalla_menu, text=opcion, command=lambda opcion_o=opcion: abrir_opcion_menu(opcion_o), height=40, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=24, pady= 4)

aviso = ctk.CTkLabel(pantalla_menu, text="", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=13))
aviso.pack(pady=(6, 0))

boton_panel_admin = ctk.CTkButton(
    pantalla_menu, text="Panel administrativo", command=lambda: mostrar_panel_admin("Dashboard"),
    height=40, corner_radius=10, fg_color=morado, hover_color=morado_oscuro,
    text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")
)

def cerrar_sesion_interfaz():
    cerrar_sesion()
    caja_correo.delete(0, "end")
    caja_clave.delete(0, "end")
    mensaje.configure(text="")
    boton_panel_admin.pack_forget()
    mostrar(pantalla_login)

boton_cerrar_sesion = ctk.CTkButton(
    pantalla_menu, text="Cerrar sesión", command=cerrar_sesion_interfaz,
    fg_color="transparent", hover_color=borde, text_color=morado,
    font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")
)
boton_cerrar_sesion.pack(pady=(8, 0))

#Pantalla trajes
pantalla_trajes = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_trajes, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(12, 0))
ctk.CTkLabel(pantalla_trajes, text="Trajes para alquilar", text_color=texto, font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(4, 12))

lista_trajes = ctk.CTkScrollableFrame(pantalla_trajes, fg_color=fondo)
lista_trajes.pack(fill="both", expand=True, padx=12, pady=(0, 12))

def mostrar_trajes():
    for tarjeta in lista_trajes.winfo_children():
        tarjeta.destroy()

    trajes = cargar_trajes()
    descripciones = cargar_descripciones_trajes()
    for codigo, nombre, tallas, precio, estado in trajes:
        tarjeta = ctk.CTkFrame(lista_trajes, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)
        mostrar_foto_producto(tarjeta, codigo, "🤵")

        ctk.CTkLabel(tarjeta, text=nombre, text_color=texto, anchor="w",  font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(tarjeta, text=f"Código {codigo} · Tallas: {tallas}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=12)).pack(fill="x", padx=14)
        ctk.CTkLabel(tarjeta, text=descripciones.get(codigo, ""), text_color=texto, anchor="w", justify="left", wraplength=310, font=ctk.CTkFont(family=letra_texto, size=12)).pack(fill="x", padx=14, pady=(4, 2))
        ctk.CTkLabel(tarjeta, text=f"${precio:,}".replace(",", "."), text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=14)

        if estado == "Activo":
            texto_estado = "Disponible"
            color_estado = verde
            estado_boton= "normal"
            color_boton = morado
            texto_boton = "Alquilar"
        else:
            texto_estado = "No disponible"
            color_estado = rojo
            estado_boton= "disabled"
            color_boton = borde
            texto_boton = "No disponible"
        ctk.CTkLabel(tarjeta, text=texto_estado, text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")).pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkButton(tarjeta, text=texto_boton, height=36, state=estado_boton, text_color_disabled=gris, corner_radius=10, fg_color=color_boton, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold"), command=lambda caracter_c=codigo, numero_n=nombre, talla_t=tallas, producto_p=precio: abrir_formulario_alquiler(caracter_c, numero_n, talla_t, producto_p)).pack(fill="x", padx=14, pady=(0, 12))

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
fecha_alquiler = ctk.StringVar()
fila_fecha1 = ctk.CTkFrame(pantalla_alquiler, fg_color=fondo)
fila_fecha1.pack(fill="x", padx=24, pady=(6, 14))
caja_fecha1 = ctk.CTkEntry(fila_fecha1, textvariable=fecha_alquiler, state="readonly", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
caja_fecha1.pack(side="left", fill="x", expand=True)
ctk.CTkButton(fila_fecha1, text="📅", width=46, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(size=18), command=lambda: abrir_calendario(fecha_alquiler)).pack(side="left", padx=(8, 0))

ctk.CTkLabel(pantalla_alquiler, text="Fecha de devolución", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=24)
fecha_devolucion = ctk.StringVar()
fila_fecha2 = ctk.CTkFrame(pantalla_alquiler, fg_color=fondo)
fila_fecha2.pack(fill="x", padx=24, pady=(6, 14))
caja_fecha2 = ctk.CTkEntry(fila_fecha2, textvariable=fecha_devolucion, state="readonly", height=46, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
caja_fecha2.pack(side="left", fill="x", expand=True)
ctk.CTkButton(fila_fecha2, text="📅", width=46, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(size=18), command=lambda: abrir_calendario(fecha_devolucion)).pack(side="left", padx=(8, 0))

#Error o mensaje de éxito
mensaje_alquiler = ctk.CTkLabel(pantalla_alquiler, text="", text_color=rojo, wraplength=372, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_alquiler.pack(fill="x", padx=24)

#Formulario
codigo_elegido = ""

def abrir_formulario_alquiler(codigo, nombre, tallas, precio):
    global codigo_elegido
    codigo_elegido = codigo

    precio_texto = f"${precio:,}".replace(",", ".")
    traje_seleccionado.configure(text=f"{nombre}\n{precio_texto}")

    lista_tallas = tallas.split(", ")
    selector_talla.configure(values=lista_tallas)
    selector_talla.set("Elija una talla")

    fecha_alquiler.set(datetime.date.today().strftime("%d/%m/%Y"))
    fecha_devolucion.set((datetime.date.today() + datetime.timedelta(days=1)).strftime("%d/%m/%Y"))
    mensaje_alquiler.configure(text="")
    mostrar(pantalla_alquiler)

#Confrimar alquiler
def confirmar_alquiler_interfaz():
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
        alquiler= registrar_alquiler (sesion_actual.correo, codigo_elegido, talla, fecha1, fecha2)
    except ValueError as problema:
        mensaje_alquiler.configure(text=str(problema), text_color=rojo)
        return

    mensaje_alquiler.configure(
        text=f"¡Alquiler registrado exitosamente!\n{alquiler['Nombre']} · Talla {alquiler['Talla']}\nDel {alquiler['FechaAlquiler']} al {alquiler['FechaProgramada']}",
        text_color= verde)

bonton_confirmar = ctk.CTkButton(pantalla_alquiler, text="Confirmar alquiler", command=confirmar_alquiler_interfaz, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold"))
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

def mostrar_alquileres():
    mensaje_devolucion.configure(text="")
    for tarjeta in lista_alquileres.winfo_children():
        tarjeta.destroy()

    alquileres = obtener_alquileres_usuario(sesion_actual.correo)

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
            ctk.CTkButton(tarjeta, text="Devolver traje", height=36, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold"), command=lambda indice_i=alquiler["IndiceArchivo"]: devolver(indice_i)).pack(fill="x", padx=14, pady=(0, 12))

        else:
            color_estado = gris
        ctk.CTkLabel(tarjeta, text=alquiler["Estado"], text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=14, pady=(2, 12))

    mostrar(pantalla_alquileres)

#Devolver traje
def devolver(indice):
    if not messagebox.askyesno("Confirmar devolución", "¿Seguro que quieres devolver este traje?"):
        return
    try:
        traje= devolver_alquiler(sesion_actual.correo, indice)
    except ValueError as problema:
        mensaje_devolucion.configure(text=str(problema), text_color=rojo)
        return

    mostrar_alquileres()
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


def crear_cuenta_interfaz():
    correo = registro_correo.get().strip()
    clave = registro_clave.get()
    clave2 = registro_clave2.get()

    if clave != clave2:
        mensaje_registro.configure(text="Las dos contraseñas no son iguales.")
        return

    try:
        registrar_usuario(correo, clave)
    except ValueError as problema:
        mensaje_registro.configure(text=str(problema))
        return

    bienvenida.configure(text=f"Bienvenida, {correo}")
    mostrar(pantalla_menu)

ctk.CTkButton(pantalla_registro, text="Crear cuenta", command=crear_cuenta_interfaz, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=24, pady=(8, 6))
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

def crear_campo(etiqueta, ejemplo):
    ctk.CTkLabel(formulario, text=etiqueta, text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=16)
    caja = ctk.CTkEntry(formulario, placeholder_text=ejemplo, height=42, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
    caja.pack(fill="x", padx=16, pady=(6, 12))
    return caja

caja_nombre = crear_campo("Nombre", "Ej: Isabella")
caja_apellidos = crear_campo("Apellidos", "Ej: Caro López")
caja_telefono = crear_campo("Teléfono", "10 dígitos")

ctk.CTkLabel(formulario, text="Tipo de documento", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=16)
selector_documento = ctk.CTkOptionMenu(formulario, values=["CC", "CE", "NIT"], height=42, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
selector_documento.pack(fill="x", padx=16, pady=(6, 12))

caja_documento = crear_campo("Número de documento", "Solo números")
caja_direccion = crear_campo("Dirección", "Ej: Calle 5 # 10-20")
caja_postal = crear_campo("Código postal", "6 dígitos")

mensaje_datos = ctk.CTkLabel(formulario, text="", text_color=rojo, wraplength=340, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_datos.pack(fill="x", padx=16)


def llenar_campo(caja, valor):
    caja.delete(0, "end")
    if valor:
        caja.insert(0, valor)

def mostrar_datos_personales():
    datos = leer_datos_personales(sesion_actual.correo)
    if datos is None:
        datos = {}

    llenar_campo(caja_nombre, datos.get("Nombre", ""))
    llenar_campo(caja_apellidos, datos.get("Apellidos", ""))
    llenar_campo(caja_telefono, datos.get("Telefono", ""))
    selector_documento.set(datos.get("TipoDocumento", "CC"))
    llenar_campo(caja_documento, datos.get("NumeroDocumento", ""))
    llenar_campo(caja_direccion, datos.get("Direccion", ""))
    llenar_campo(caja_postal, datos.get("CodigoPostal", ""))

    mensaje_datos.configure(text="")
    mostrar(pantalla_datos)

def guardar_datos_interfaz():
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
        guardar_datos_personales(sesion_actual.correo, datos)
    except ValueError as problema:
        mensaje_datos.configure(text=str(problema), text_color=rojo)
        return

    mensaje_datos.configure(text="¡Datos guardados exitosamente!", text_color=verde)

ctk.CTkButton(formulario, text="Guardar datos", command=guardar_datos_interfaz, height=46, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=16, pady=(8, 12))

#BUSCAR ROPA
pantalla_buscar = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_buscar, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_buscar, text="Buscar ropa", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

filtros = ctk.CTkFrame(pantalla_buscar, fg_color=fondo)
filtros.pack(fill="x", padx=24, pady=(0, 8))

selector_seccion = ctk.CTkOptionMenu(filtros, values=["Todas", "Mujer", "Hombre", "Unisex"], command=lambda valor: mostrar_productos_ropa(), width=170, height=38, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
selector_seccion.pack(side="left", padx=(0, 8))

selector_tipo = ctk.CTkOptionMenu(filtros, values=["Todos"], command=lambda valor: mostrar_productos_ropa(), width=170, height=38, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
selector_tipo.pack(side="left")

filtros2 = ctk.CTkFrame(pantalla_buscar, fg_color=fondo)
filtros2.pack(fill="x", padx=24, pady=(0, 8))

caja_busqueda = ctk.CTkEntry(filtros2, placeholder_text="🔍 Nombre o código", width=210, height=38, corner_radius=10, fg_color=blanco, border_color=borde, text_color=texto)
caja_busqueda.pack(side="left", padx=(0, 8))
caja_busqueda.bind("<KeyRelease>", lambda evento: mostrar_productos_ropa())

selector_disponibilidad= ctk.CTkOptionMenu(filtros2, values=["Todas", "Disponible", "Agotado"], command=lambda valor: mostrar_productos_ropa(), width=130, height=38, corner_radius=10, fg_color=blanco, button_color=morado, button_hover_color=morado_oscuro, text_color=texto, dropdown_fg_color=blanco, dropdown_text_color=texto)
selector_disponibilidad.pack(side="left")


mensaje_buscar = ctk.CTkLabel(pantalla_buscar, text="", text_color=rojo, wraplength=372, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=13))
mensaje_buscar.pack(fill="x", padx=24)

lista_ropa = ctk.CTkScrollableFrame(pantalla_buscar, fg_color=fondo)
lista_ropa.pack(fill="both", expand=True, padx=16, pady=(0, 16))

catalogo = []

def mostrar_catalogo_ropa():
    global catalogo
    mensaje_buscar.configure(text="")
    try:
        catalogo = cargar_catalogo_ropa()
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema))
        catalogo = []

    tipos = ["Todos"]
    for producto in catalogo:
        if producto["Tipo"] not in tipos:
            tipos.append(producto["Tipo"])
    selector_tipo.configure(values=tipos)

    selector_disponibilidad.set("Todas")
    caja_busqueda.delete(0, "end")
    mostrar_productos_ropa()
    mostrar(pantalla_buscar)

def mostrar_productos_ropa():
    for tarjeta in lista_ropa.winfo_children():
        tarjeta.destroy()

    seccion = selector_seccion.get()
    tipo = selector_tipo.get()
    if seccion == "Todas":
        seccion = None
    if tipo == "Todos":
        tipo = None

    productos = filtrar_catalogo_ropa(catalogo, seccion, tipo)

    busqueda= caja_busqueda.get().strip().lower()
    disponibilidad = selector_disponibilidad.get()

    productos_filtrados = []
    for producto in productos:
        coincide_texto = busqueda in producto["Nombre"].lower() or busqueda in producto["Codigo"].lower()
        coincide_disponibilidad = disponibilidad == "Todas" or producto["Disponibilidad"] == disponibilidad

        if coincide_texto and coincide_disponibilidad:
            productos_filtrados.append(producto)
    productos = productos_filtrados

    if len(productos) == 0:
        ctk.CTkLabel(lista_ropa, text="No hay prendas con esos filtros.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for producto in productos:
        tarjeta = ctk.CTkFrame(lista_ropa, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)
        mostrar_foto_producto(tarjeta, producto["Codigo"], iconos_ropa.get(producto["Tipo"], "🛍️"))

        texto_tallas = ""
        tallas_disponibles = []
        for talla in producto["Tallas"]:
            if talla["Cantidad"] > 0:
                texto_tallas = texto_tallas + talla["Talla"] + "   "
                tallas_disponibles.append(talla["Talla"])

        precio_texto = f"${producto['Precio']:,.0f}".replace(",", ".")

        ctk.CTkLabel(tarjeta, text=producto["Nombre"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(tarjeta, text=f"{producto['Seccion']} · {producto['Tipo']} · Código {producto['Codigo']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)
        ctk.CTkLabel(tarjeta, text=producto["Descripcion"], text_color=texto, anchor="w", justify="left", wraplength=310, font=ctk.CTkFont(family=letra_texto, size=12)).pack(fill="x", padx=14, pady=(4, 2))
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

            ctk.CTkButton(fila, text="Agregar al carrito", height=36, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold"), command=lambda caracter_c=producto["Codigo"], elemento_s=selector: agregar_producto_carrito(caracter_c, elemento_s.get())).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(tarjeta, text="♡ Agregar a favoritos", height=30, fg_color="transparent", hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), command=lambda caracter_c=producto["Codigo"]: agregar_producto_favorito(caracter_c)).pack(anchor="w", padx=8, pady=(0, 10))
#AGREGAR AL CARRITO

def agregar_producto_carrito(codigo, talla):
    try:
        cantidad = agregar_al_carrito(sesion_actual.correo, codigo, talla, 1, catalogo)
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema), text_color=rojo)
        return

    mensaje_buscar.configure(text=f"¡Agregado al carrito! (talla {talla}, llevas {cantidad})", text_color=verde)

def formatear_pesos(valor):
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


def mostrar_carrito():
    mensaje_carrito.configure(text="")
    for tarjeta in lista_carrito.winfo_children():
        tarjeta.destroy()

    detalles = obtener_detalles_carrito(sesion_actual.correo)
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
            subtotal_texto = f"{formatear_pesos(detalle['Precio'])} c/u · Subtotal {formatear_pesos(detalle['Subtotal'])}"
            total = total + detalle["Subtotal"]
        ctk.CTkLabel(tarjeta, text=subtotal_texto, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=14, pady=(4, 0))

        if detalle["Aviso"]!= "":
            ctk.CTkLabel(tarjeta, text=detalle["Aviso"], text_color=rojo, wraplength=320, justify="left", anchor="w", font=ctk.CTkFont(family=letra_texto, size=12)).pack(fill="x", padx=14)

        fila = ctk.CTkFrame(tarjeta, fg_color=blanco)
        fila.pack(fill="x", padx=14, pady=(8, 12))

        ctk.CTkButton(fila, text="−", width=36, height=32, corner_radius=8, fg_color=fondo, hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=16, weight="bold"), command=lambda caracter_c=detalle["Codigo"], talla_t=detalle["Talla"], numero_n=detalle["Cantidad"] - 1: cambiar_cantidad_carrito(caracter_c, talla_t, numero_n)).pack(side="left")
        ctk.CTkLabel(fila, text=str(detalle["Cantidad"]), width=36, text_color=texto, font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(side="left")
        ctk.CTkButton(fila, text="+", width=36, height=32, corner_radius=8, fg_color=fondo, hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=16, weight="bold"), command=lambda caracter_c=detalle["Codigo"], talla_t=detalle["Talla"], numero_n=detalle["Cantidad"] + 1: cambiar_cantidad_carrito(caracter_c, talla_t, numero_n)).pack(side="left")

        ctk.CTkButton(fila, text="Quitar", width=70, height=32, fg_color="transparent", hover_color=borde, text_color=rojo, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), command=lambda caracter_c=detalle["Codigo"], talla_t=detalle["Talla"]: quitar(caracter_c, talla_t)).pack(side="right")

    total_carrito.configure(text=f"Total: {formatear_pesos(total)}")
    mostrar(pantalla_carrito)

def cambiar_cantidad_carrito(codigo,talla,nueva):
    if nueva <= 0:
        quitar(codigo, talla)
        return
    try:
        actualizar_cantidad_carrito(sesion_actual.correo, codigo, talla, nueva)
    except ValueError as problema:
        mensaje_carrito.configure(text=str(problema), text_color=rojo)
        return
    mostrar_carrito()

def quitar(codigo, talla):
    eliminar_del_carrito(sesion_actual.correo, codigo, talla)
    mostrar_carrito()

#CONFIRMAR COMPRA

def comprar():
    detalles, total, error = preparar_compra(sesion_actual.correo)
    if error:
        mensaje_carrito.configure(text=error, text_color=rojo)
        return

    respuesta = messagebox.askyesno("Confirmar compra", f"¿Desea confirmar la compra por {formatear_pesos(total)}?")

    resultado = confirmar_compra(sesion_actual.correo, respuesta)

    if resultado["ok"]:
        mostrar_carrito()
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

def mostrar_compras():
    for tarjeta in lista_compras.winfo_children():
        tarjeta.destroy()

    pedidos = listar_compras(sesion_actual.correo)

    if len(pedidos) == 0:
        ctk.CTkLabel(lista_compras, text="Aún no tienes compras registradas.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for pedido in pedidos:
        tarjeta = ctk.CTkFrame(lista_compras, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(tarjeta, text=pedido["Fecha"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(tarjeta, text=f"Pedido {pedido['Pedido']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=11)).pack(fill="x", padx=14, pady=(0, 6))

        for articulo in pedido["Articulos"]:
            ctk.CTkLabel(tarjeta, text=f"• {articulo['Nombre']} (talla {articulo['Talla']}) x{articulo['Cantidad']}  —  {formatear_pesos(articulo['Subtotal'])}", text_color=texto, anchor="w", justify="left", wraplength=320, font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)

        ctk.CTkLabel(tarjeta, text=f"Total: {formatear_pesos(pedido['Total'])}", text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=14, pady=(6, 12))

    mostrar(pantalla_compras)

#FAVORITOS

def agregar_producto_favorito(codigo):
    try:
        agregar_favorito(sesion_actual.correo, codigo)
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema), text_color=rojo)
        return
    mensaje_buscar.configure(text="¡Agregado a favoritos! ♡", text_color=verde)

pantalla_favoritos = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_favoritos, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_favoritos, text="Mis favoritos", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

lista_favoritos = ctk.CTkScrollableFrame(pantalla_favoritos, fg_color=fondo)
lista_favoritos.pack(fill="both", expand=True, padx=16, pady=(0, 16))


def mostrar_favoritos():
    for tarjeta in lista_favoritos.winfo_children():
        tarjeta.destroy()

    favoritos = listar_favoritos(sesion_actual.correo)

    if len(favoritos) == 0:
        ctk.CTkLabel(lista_favoritos, text="No tienes productos favoritos.", text_color=gris, font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=20)

    for favorito in favoritos:
        tarjeta = ctk.CTkFrame(lista_favoritos, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
        tarjeta.pack(fill="x", padx=8, pady=6)

        if favorito["EstadoFavorito"] == "Activo":
            ctk.CTkLabel(tarjeta, text=favorito["Nombre"], text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
            ctk.CTkLabel(tarjeta, text=f"{favorito['Seccion']} · {favorito['Tipo']}", text_color=gris, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)
            ctk.CTkLabel(tarjeta, text=formatear_pesos(favorito["Precio"]), text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")).pack(fill="x", padx=14, pady=(4, 0))
            if favorito["Disponibilidad"] == "Disponible":
                color_estado = verde
            else:
                color_estado = rojo
            ctk.CTkLabel(tarjeta, text=favorito["Disponibilidad"], text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")).pack(fill="x", padx=14)
        else:
            # El producto ya no está en el catálogo
            ctk.CTkLabel(tarjeta, text=f"{favorito['Nombre']} ({favorito['Codigo']})", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(fill="x", padx=14, pady=(12, 2))
            ctk.CTkLabel(tarjeta, text="Ya no está disponible en la tienda.", text_color=rojo, anchor="w", font=ctk.CTkFont(family=letra_texto, size=13)).pack(fill="x", padx=14)

        ctk.CTkButton(tarjeta, text="Quitar de favoritos", height=30, fg_color="transparent", hover_color=borde, text_color=rojo, font=ctk.CTkFont(family=letra_texto, size=13, weight="bold"), command=lambda caracter_c=favorito["Codigo"]: quitar_producto_favorito(caracter_c)).pack(anchor="w", padx=8, pady=(4, 10))

    mostrar(pantalla_favoritos)


def quitar_producto_favorito(codigo):
    eliminar_favorito(sesion_actual.correo, codigo)
    mostrar_favoritos()

# PANEL ADMINISTRATIVO
# Reutiliza la identidad visual del cliente: morado, fondo claro, blanco y borde lavanda.
color_admin_negro = texto
color_admin_marfil = fondo
color_admin_dorado = morado
color_admin_dorado_oscuro = morado_oscuro

pantalla_admin = ctk.CTkFrame(ventana, fg_color=color_admin_marfil, corner_radius=0)
encabezado_admin = ctk.CTkFrame(pantalla_admin, fg_color=morado, corner_radius=0)
encabezado_admin.pack(fill="x")
ctk.CTkLabel(
    encabezado_admin, text="Panel administrativo", text_color=blanco,
    font=ctk.CTkFont(family=letra_titulo, size=22, weight="bold")
).pack(pady=(10, 10))

barra_admin = ctk.CTkFrame(pantalla_admin, fg_color=color_admin_marfil)
barra_admin.pack(fill="x", padx=8, pady=(7, 3))
for columna in range(2):
    barra_admin.grid_columnconfigure(columna, weight=1)
contenido_admin = ctk.CTkScrollableFrame(pantalla_admin, fg_color=color_admin_marfil)
contenido_admin.pack(fill="both", expand=True, padx=8, pady=(0, 7))
mensaje_admin = ctk.CTkLabel(
    pantalla_admin, text="", text_color="#9B241B", wraplength=380,
    justify="left", font=ctk.CTkFont(family=letra_texto, size=12)
)
mensaje_admin.pack(fill="x", padx=18, pady=(0, 4), before=contenido_admin)

def _limpiar_admin():
    for elemento in contenido_admin.winfo_children():
        elemento.destroy()
    mensaje_admin.configure(text="")


def _titulo_admin(texto):
    ctk.CTkLabel(
        contenido_admin, text=texto, text_color=color_admin_negro, anchor="w",
        font=ctk.CTkFont(family=letra_titulo, size=24, weight="bold")
    ).pack(fill="x", padx=10, pady=(8, 10))


def _tarjeta_admin(texto, detalle=""):
    tarjeta = ctk.CTkFrame(
        contenido_admin, fg_color=blanco, corner_radius=12,
        border_width=1, border_color=borde
    )
    tarjeta.pack(fill="x", padx=6, pady=4)
    ctk.CTkLabel(
        tarjeta, text=texto, text_color=color_admin_negro, anchor="w",
        justify="left", wraplength=360,
        font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")
    ).pack(fill="x", padx=16, pady=(13, 4))
    if detalle:
        ctk.CTkLabel(
            tarjeta, text=detalle, text_color=gris, anchor="w",
            justify="left", wraplength=360,
            font=ctk.CTkFont(family=letra_texto, size=13)
        ).pack(fill="x", padx=16, pady=(0, 13))
    return tarjeta


def _tarjeta_estadistica(contenedor, texto, valor):
    tarjeta = ctk.CTkFrame(
        contenedor, fg_color=blanco, corner_radius=12,
        border_width=1, border_color=borde
    )
    ctk.CTkLabel(
        tarjeta, text=texto, text_color=gris, anchor="w",
        justify="left", wraplength=150,
        font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
    ).pack(fill="x", padx=12, pady=(10, 2))
    ctk.CTkLabel(
        tarjeta, text=str(valor), text_color=morado, anchor="w",
        font=ctk.CTkFont(family=letra_titulo, size=18, weight="bold")
    ).pack(fill="x", padx=12, pady=(0, 10))
    return tarjeta


def _mostrar_dashboard():
    _limpiar_admin()
    _titulo_admin("Dashboard")
    try:
        estadisticas = obtener_estadisticas_administracion()
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return
    for nombre, valor in estadisticas.items():
        if nombre == "Ventas simuladas":
            valor = formatear_pesos(valor)
        _tarjeta_admin(nombre, str(valor))


def _mostrar_inventario(vista="prendas"):
    _limpiar_admin()
    _titulo_admin("Inventario")
    barra_inventario = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    barra_inventario.pack(fill="x", padx=4, pady=(0, 6))
    ctk.CTkButton(
        barra_inventario, text="Prendas",
        fg_color=morado if vista == "prendas" else blanco,
        hover_color=morado_oscuro, text_color=blanco if vista == "prendas" else morado,
        height=34,
        text_color_disabled=gris,
        command=lambda: _mostrar_inventario("prendas")
    ).pack(side="left", padx=(0, 6))
    ctk.CTkButton(
        barra_inventario, text="Trajes",
        fg_color=morado if vista == "trajes" else blanco,
        hover_color=morado_oscuro if vista == "trajes" else borde,
        text_color=blanco if vista == "trajes" else morado, height=34,
        command=lambda: _mostrar_inventario("trajes")
    ).pack(side="left")

    if vista == "trajes":
        _mostrar_trajes_admin_contenido()
        return

    controles = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    controles.pack(fill="x", padx=4, pady=(0, 8))
    busqueda = ctk.CTkEntry(
        controles, placeholder_text="Buscar por nombre o código",
        height=38, fg_color=blanco, border_color=borde, text_color=texto
    )
    busqueda.pack(side="left", fill="x", expand=True, padx=(0, 6))
    ctk.CTkButton(
        controles, text="+ Agregar prenda", height=38, fg_color=morado,
        hover_color=morado_oscuro, text_color=blanco,
        command=lambda: _abrir_formulario_prenda(actualizar_lista=cargar_prendas)    ).pack(side="right")

    lista_prendas = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    lista_prendas.pack(fill="x", padx=4)

    def cargar_prendas():
        for elemento in lista_prendas.winfo_children():
            elemento.destroy()
        try:
            productos, existencias = cargar_inventario_administracion()
        except (OSError, ValueError, PermissionError) as problema:
            mensaje_admin.configure(text=str(problema), text_color=rojo)
            return
        texto_busqueda = busqueda.get().strip().casefold()
        encontrados = productos[
            productos.apply(
                lambda fila: texto_busqueda in str(fila["Nombre"]).casefold()
                or texto_busqueda in str(fila["Codigo"]).casefold(), axis=1
            )
        ]
        if encontrados.empty:
            _tarjeta_admin("No hay prendas que coincidan con la búsqueda.")
            return
        for _, producto in encontrados.iterrows():
            variantes = existencias[
                existencias["Codigo"].astype(str).str.casefold()
                == str(producto["Codigo"]).casefold()
            ]
            tallas = ", ".join(
                f"{fila['Talla']}: {int(fila['Cantidad'])}"
                for _, fila in variantes.iterrows()
            ) or "Sin tallas registradas"
            tarjeta = ctk.CTkFrame(
                lista_prendas, fg_color=blanco, corner_radius=12,
                border_width=1, border_color=borde
            )
            tarjeta.pack(fill="x", pady=4)
            mostrar_foto_admin(tarjeta, str(producto["Codigo"]))
            ctk.CTkLabel(
                tarjeta, text=str(producto["Nombre"]), text_color=texto,
                anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")
            ).pack(fill="x", padx=14, pady=(10, 2))
            ctk.CTkLabel(
                tarjeta,
                text=f"Código: {producto['Codigo']} · Precio: {formatear_pesos(producto['Precio'])}",
                text_color=gris, anchor="w",
                font=ctk.CTkFont(family=letra_texto, size=12)
            ).pack(fill="x", padx=14)
            ctk.CTkLabel(
                tarjeta, text=f"Estado: {producto['Estado']} · Tallas: {tallas}",
                text_color=verde if producto["Estado"] == "Activo" else rojo,
                anchor="w", wraplength=360,
                font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
            ).pack(fill="x", padx=14, pady=(3, 5))
            acciones = ctk.CTkFrame(tarjeta, fg_color=blanco)
            acciones.pack(fill="x", padx=10, pady=(0, 10))
            ctk.CTkButton(
                acciones, text="Editar", height=30, fg_color=morado,
                hover_color=morado_oscuro, text_color=blanco,
                command=lambda producto_p=producto, variantes_v=variantes:
                    _abrir_formulario_prenda(producto_p, variantes_v, cargar_prendas)
            ).pack(side="left", expand=True, fill="x", padx=(0, 4))
            ctk.CTkButton(
                acciones, text="Desactivar", height=30, fg_color="transparent",
                hover_color=borde, text_color=rojo,
                state="disabled" if producto["Estado"] != "Activo" else "normal",
                command=lambda codigo_c=producto["Codigo"]: _desactivar_prenda(codigo_c, cargar_prendas)
            ).pack(side="left", expand=True, fill="x", padx=(4, 0))

    busqueda.bind("<KeyRelease>", lambda evento: cargar_prendas())
    cargar_prendas()


def _mostrar_trajes_admin_contenido():
    controles = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    controles.pack(fill="x", padx=4, pady=(0, 8))
    busqueda = ctk.CTkEntry(
        controles, placeholder_text="Buscar por nombre o código",
        height=38, fg_color=blanco, border_color=borde, text_color=texto
    )
    busqueda.pack(side="left", fill="x", expand=True, padx=(0, 6))
    ctk.CTkButton(
        controles, text="+ Agregar traje", height=38, fg_color=morado,
        hover_color=morado_oscuro, text_color=blanco,
        command=lambda: _abrir_formulario_traje(actualizar_lista=cargar_trajes_admin)
    ).pack(side="right")

    lista_trajes_admin = ctk.CTkFrame(
        contenido_admin, fg_color=color_admin_marfil
    )
    lista_trajes_admin.pack(fill="x", padx=4)

    def cargar_trajes_admin():
        for elemento in lista_trajes_admin.winfo_children():
            elemento.destroy()
        try:
            trajes = cargar_trajes_administracion()
        except (OSError, ValueError, PermissionError, ImportError) as problema:
            mensaje_admin.configure(
                text=f"No se pudieron cargar los trajes: {problema}",
                text_color=rojo
            )
            return

        texto_busqueda = busqueda.get().strip().casefold()
        if texto_busqueda:
            encontrados = trajes[
                trajes["Codigo"].astype(str).str.casefold().str.contains(texto_busqueda, regex=False)
                | trajes["Nombre"].astype(str).str.casefold().str.contains(texto_busqueda, regex=False)
            ]
        else:
            encontrados = trajes
        if encontrados.empty:
            ctk.CTkLabel(
                lista_trajes_admin, text="No hay trajes que coincidan con la búsqueda.",
                text_color=gris, anchor="w",
                font=ctk.CTkFont(family=letra_texto, size=14)
            ).pack(fill="x", padx=10, pady=20)
            return

        for _, traje in encontrados.iterrows():
            codigo = traje["Codigo"]
            nombre = traje["Nombre"]
            tallas = traje["Tallas"]
            precio = traje["Precio"]
            estado = traje["Estado"]
            descripcion = traje["Descripcion"]
            tarjeta = ctk.CTkFrame(
                lista_trajes_admin, fg_color=blanco, corner_radius=12,
                border_width=1, border_color=borde
            )
            tarjeta.pack(fill="x", pady=4)
            try:
                mostrar_foto_admin(tarjeta, str(codigo))
                ctk.CTkLabel(
                    tarjeta, text=str(nombre), text_color=texto,
                    anchor="w",
                    font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")
                ).pack(fill="x", padx=14, pady=(10, 2))
                ctk.CTkLabel(
                    tarjeta, text=f"Código: {codigo}",
                    text_color=gris, anchor="w",
                    font=ctk.CTkFont(family=letra_texto, size=12)
                ).pack(fill="x", padx=14)
                ctk.CTkLabel(
                    tarjeta, text=f"Precio: {formatear_pesos(precio)}",
                    text_color=morado, anchor="w",
                    font=ctk.CTkFont(family=letra_texto, size=15, weight="bold")
                ).pack(fill="x", padx=14, pady=(4, 0))
                ctk.CTkLabel(
                    tarjeta, text=f"Tallas: {tallas}", text_color=texto,
                    anchor="w", wraplength=360,
                    font=ctk.CTkFont(family=letra_texto, size=12)
                ).pack(fill="x", padx=14, pady=(3, 2))
                ctk.CTkLabel(
                    tarjeta, text=f"Estado: {estado}",
                    text_color=verde if str(estado).casefold() == "activo" else rojo,
                    anchor="w",
                    font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
                ).pack(fill="x", padx=14, pady=(0, 3))
                ctk.CTkLabel(
                    tarjeta, text=str(descripcion),
                    text_color=texto, anchor="w", justify="left",
                    wraplength=360,
                    font=ctk.CTkFont(family=letra_texto, size=12)
                ).pack(fill="x", padx=14, pady=(0, 10))
                ctk.CTkButton(
                    tarjeta, text="Editar", height=30, fg_color=morado,
                    hover_color=morado_oscuro, text_color=blanco,
                    command=lambda traje_p=traje: _abrir_formulario_traje(
                        traje_p, cargar_trajes_admin
                    )
                ).pack(fill="x", padx=10, pady=(0, 10))
            except (OSError, TypeError, ValueError, RuntimeError) as problema:
                logger.exception("No se pudo renderizar el traje %s", codigo)
                tarjeta.destroy()
                ctk.CTkLabel(
                    lista_trajes_admin,
                    text=f"No se pudo mostrar el traje {codigo}: {problema}",
                    text_color=rojo, anchor="w", wraplength=360,
                    font=ctk.CTkFont(family=letra_texto, size=13)
                ).pack(fill="x", padx=10, pady=8)

    busqueda.bind("<KeyRelease>", lambda evento: cargar_trajes_admin())
    cargar_trajes_admin()


def _mostrar_trajes_admin_pendiente():
    _mostrar_inventario("trajes")


def mostrar_foto_admin(contenedor, codigo):
    ruta = next(
        (carpeta_imagenes / f"{codigo}{extension}"
         for extension in (".jpg", ".jpeg", ".png")
         if (carpeta_imagenes / f"{codigo}{extension}").exists()),
        None
    )
    if ruta is None:
        ctk.CTkLabel(
            contenedor, text=iconos_ropa.get("Prenda", "🛍️"),
            text_color=gris, font=ctk.CTkFont(size=28)
        ).pack(anchor="w", padx=14, pady=(8, 0))
        return
    imagen = Image.open(ruta)
    imagen = ImageOps.pad(imagen, (120, 80), color=blanco)
    foto = ctk.CTkImage(light_image=imagen, size=(120, 80))
    etiqueta = ctk.CTkLabel(contenedor, image=foto, text="")
    etiqueta.image = foto
    etiqueta.pack(anchor="w", padx=14, pady=(8, 0))


def _desactivar_prenda(codigo, actualizar_lista):
    if not messagebox.askyesno("Desactivar prenda", f"¿Deseas desactivar {codigo}?"):
        return
    try:
        desactivar_producto(codigo)
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return
    mensaje_admin.configure(text=f"Prenda {codigo} desactivada.", text_color=verde)
    actualizar_lista()


def _abrir_formulario_traje(traje=None, actualizar_lista=None):
    editar = traje is not None
    ventana_formulario = ctk.CTkToplevel(ventana)
    ventana_formulario.title("Editar traje" if editar else "Agregar traje")
    ventana_formulario.configure(fg_color=fondo)
    ventana_formulario.transient(ventana)
    ancho_formulario, alto_formulario = 420, 620
    ventana.update_idletasks()
    posicion_x = ventana.winfo_rootx() + (ventana.winfo_width() - ancho_formulario) // 2
    posicion_y = ventana.winfo_rooty() + (ventana.winfo_height() - alto_formulario) // 2
    pantalla_ancho = ventana_formulario.winfo_screenwidth()
    pantalla_alto = ventana_formulario.winfo_screenheight()
    posicion_x = min(max(posicion_x, 0), pantalla_ancho - ancho_formulario)
    posicion_y = min(max(posicion_y, 0), pantalla_alto - alto_formulario)
    ventana_formulario.geometry(
        f"{ancho_formulario}x{alto_formulario}+{posicion_x}+{posicion_y}"
    )
    ventana_formulario.grab_set()

    formulario = ctk.CTkScrollableFrame(ventana_formulario, fg_color=fondo)
    formulario.pack(fill="both", expand=True, padx=12, pady=12)

    def campo(etiqueta, valor="", estado="normal"):
        ctk.CTkLabel(
            formulario, text=etiqueta, text_color=texto, anchor="w",
            font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
        ).pack(fill="x", pady=(5, 2))
        entrada = ctk.CTkEntry(
            formulario, height=38, fg_color=blanco, border_color=borde,
            text_color=texto, state=estado
        )
        entrada.pack(fill="x", pady=(0, 3))
        entrada.configure(state="normal")
        entrada.insert(0, str(valor))
        if estado == "disabled":
            entrada.configure(state="disabled")
        return entrada

    valor = lambda campo_nombre: traje[campo_nombre] if editar else ""
    codigo = campo("Código único", valor("Codigo"), "disabled" if editar else "normal")
    nombre = campo("Nombre", valor("Nombre"))
    precio = campo("Precio", valor("Precio"))
    descripcion = campo("Descripción", valor("Descripcion"))
    tallas = campo("Tallas disponibles", valor("Tallas"))

    def normalizar_mayusculas(entrada, evento=None):
        texto_actual = entrada.get()
        normalizado = texto_actual.upper()
        if texto_actual != normalizado:
            posicion = entrada.index("insert")
            entrada.delete(0, "end")
            entrada.insert(0, normalizado)
            entrada.icursor(min(posicion, len(normalizado)))

    codigo.bind("<KeyRelease>", lambda evento: normalizar_mayusculas(codigo, evento))
    tallas.bind("<KeyRelease>", lambda evento: normalizar_mayusculas(tallas, evento))

    ctk.CTkLabel(
        formulario, text="Estado", text_color=texto, anchor="w",
        font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
    ).pack(fill="x", pady=(5, 2))
    estado = ctk.CTkOptionMenu(
        formulario, values=["Activo", "Inactivo"], fg_color=blanco,
        button_color=morado, button_hover_color=morado_oscuro, text_color=texto
    )
    estado.pack(fill="x", pady=(0, 8))
    estado.set(valor("Estado") or "Activo")

    foto_seleccionada = {"ruta": None}
    vista_foto = ctk.CTkLabel(formulario, text="Sin fotografía nueva", text_color=gris)
    vista_foto.pack(fill="x", pady=(4, 4))

    def seleccionar_foto():
        ruta = filedialog.askopenfilename(
            title="Seleccionar fotografía",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        origen = Path(ruta)
        if origen.suffix.casefold() not in {".jpg", ".jpeg", ".png"}:
            messagebox.showerror("Formato no válido", "La fotografía debe ser JPG, JPEG o PNG.")
            return
        try:
            imagen = Image.open(origen)
            imagen.verify()
            imagen = Image.open(origen)
            foto = ctk.CTkImage(
                light_image=ImageOps.pad(imagen, (150, 100), color=blanco),
                size=(150, 100)
            )
        except (OSError, ValueError) as problema:
            messagebox.showerror("Imagen no válida", f"No se pudo abrir la imagen: {problema}")
            return
        foto_seleccionada["ruta"] = origen
        vista_foto.configure(image=foto, text="")
        vista_foto.image = foto

    ctk.CTkButton(
        formulario, text="Seleccionar fotografía", height=34, fg_color=morado,
        hover_color=morado_oscuro, text_color=blanco, command=seleccionar_foto
    ).pack(fill="x", pady=(2, 8))

    def guardar():
        codigo_valor = str(codigo.get()).strip().upper()
        try:
            if editar:
                actualizar_traje(
                    codigo_valor, nombre.get(), precio.get(), tallas.get(),
                    descripcion.get(), estado.get()
                )
            else:
                registrar_traje(
                    codigo_valor, nombre.get(), precio.get(), tallas.get(),
                    descripcion.get(), estado.get()
                )
            foto = foto_seleccionada["ruta"]
            if foto is not None:
                destinos = [
                    carpeta_imagenes / f"{codigo_valor}{extension}"
                    for extension in (".jpg", ".jpeg", ".png")
                ]
                if any(destino.exists() for destino in destinos):
                    confirmar = messagebox.askyesno(
                        "Reemplazar fotografía",
                        f"Ya existe una fotografía para {codigo_valor}. ¿Deseas reemplazarla?"
                    )
                    if not confirmar:
                        ventana_formulario.destroy()
                        if actualizar_lista:
                            actualizar_lista()
                        else:
                            _mostrar_inventario("trajes")
                        return
                _copiar_fotografia_producto(codigo_valor, foto)
        except (OSError, ValueError, PermissionError, ImportError) as problema:
            messagebox.showerror("No se pudo guardar el traje", str(problema))
            return
        ventana_formulario.destroy()
        if actualizar_lista:
            actualizar_lista()
        else:
            _mostrar_inventario("trajes")
        mensaje_admin.configure(text="¡Traje guardado exitosamente!", text_color=verde)

    ctk.CTkButton(
        formulario, text="Guardar traje", height=40, fg_color=morado,
        hover_color=morado_oscuro, text_color=blanco, command=guardar
    ).pack(fill="x", pady=(8, 3))
    ctk.CTkButton(
        formulario, text="Cancelar", height=34, fg_color="transparent",
        hover_color=borde, text_color=morado, command=ventana_formulario.destroy
    ).pack(fill="x", pady=(0, 8))


def _abrir_formulario_prenda(producto=None, variantes=None, actualizar_lista=None):
    editar = producto is not None
    ventana_formulario = ctk.CTkToplevel(ventana)
    ventana_formulario.title("Editar prenda" if editar else "Agregar prenda")
    ventana_formulario.configure(fg_color=fondo)
    ventana_formulario.transient(ventana)
    ancho_formulario = min(420, max(320, ventana_formulario.winfo_screenwidth() - 40))
    alto_formulario = min(680, max(520, ventana_formulario.winfo_screenheight() - 80))
    ventana.update_idletasks()
    ventana_formulario.update_idletasks()
    principal_x = ventana.winfo_rootx()
    principal_y = ventana.winfo_rooty()
    principal_ancho = ventana.winfo_width()
    principal_alto = ventana.winfo_height()
    pantalla_ancho = ventana_formulario.winfo_screenwidth()
    pantalla_alto = ventana_formulario.winfo_screenheight()
    posicion_x = principal_x + (principal_ancho - ancho_formulario) // 2
    posicion_y = principal_y + (principal_alto - alto_formulario) // 2
    posicion_x = min(max(posicion_x, 0), max(pantalla_ancho - ancho_formulario, 0))
    posicion_y = min(max(posicion_y, 0), max(pantalla_alto - alto_formulario, 0))
    ventana_formulario.geometry(
        f"{ancho_formulario}x{alto_formulario}+{posicion_x}+{posicion_y}"
    )
    ventana_formulario.grab_set()

    formulario = ctk.CTkScrollableFrame(ventana_formulario, fg_color=fondo)
    formulario.pack(fill="both", expand=True, padx=12, pady=12)

    def campo(etiqueta, valor="", estado="normal"):
        ctk.CTkLabel(
            formulario, text=etiqueta, text_color=texto, anchor="w",
            font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
        ).pack(fill="x", pady=(5, 2))
        entrada = ctk.CTkEntry(
            formulario, height=38, fg_color=blanco, border_color=borde,
            text_color=texto, state=estado
        )
        entrada.pack(fill="x", pady=(0, 3))
        if valor is not None:
            entrada.configure(state="normal")
            entrada.insert(0, str(valor))
            if estado == "disabled":
                entrada.configure(state="disabled")
        return entrada

    codigo = campo("Código único", producto["Codigo"] if editar else "", "disabled" if editar else "normal")

    def normalizar_codigo(evento=None):
        if editar or codigo.cget("state") == "disabled":
            return
        valor = codigo.get()
        normalizado = valor.upper()
        if valor != normalizado:
            posicion = codigo.index("insert")
            codigo.delete(0, "end")
            codigo.insert(0, normalizado)
            codigo.icursor(min(posicion, len(normalizado)))

    codigo.bind("<KeyRelease>", normalizar_codigo)
    nombre = campo("Nombre", producto["Nombre"] if editar else "")
    precio = campo("Precio", producto["Precio"] if editar else "")
    descripcion = campo("Descripción", producto["Descripcion"] if editar else "")
    ctk.CTkLabel(
        formulario, text="Sección", text_color=texto, anchor="w",
        font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
    ).pack(fill="x", pady=(5, 2))
    seccion = ctk.CTkOptionMenu(
        formulario, values=["Mujer", "Hombre", "Unisex"], fg_color=blanco,
        button_color=morado, button_hover_color=morado_oscuro, text_color=texto
    )
    seccion.pack(fill="x", pady=(5, 3))
    seccion.set(producto["Seccion"] if editar else "Mujer")
    tipo = campo("Tipo", producto["Tipo"] if editar else "")
    ctk.CTkLabel(
        formulario, text="Estado", text_color=texto, anchor="w",
        font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
    ).pack(fill="x", pady=(5, 2))
    estado = ctk.CTkOptionMenu(
        formulario, values=["Activo", "Inactivo"], fg_color=blanco,
        button_color=morado, button_hover_color=morado_oscuro, text_color=texto
    )
    estado.pack(fill="x", pady=(5, 3))
    estado.set(producto["Estado"] if editar else "Activo")

    foto_seleccionada = {"ruta": None}
    vista_foto = ctk.CTkLabel(formulario, text="Sin fotografía nueva", text_color=gris)
    vista_foto.pack(fill="x", pady=(8, 2))

    def seleccionar_foto():
        ruta = filedialog.askopenfilename(
            title="Seleccionar fotografía",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        if Path(ruta).suffix.casefold() not in {".jpg", ".jpeg", ".png"}:
            messagebox.showerror("Formato no válido", "La fotografía debe ser JPG, JPEG o PNG.")
            return
        try:
            imagen = Image.open(ruta)
            imagen.verify()
            imagen = Image.open(ruta)
            imagen = ImageOps.pad(imagen, (150, 100), color=blanco)
            foto = ctk.CTkImage(light_image=imagen, size=(150, 100))
        except (OSError, ValueError) as problema:
            messagebox.showerror("Imagen no válida", f"No se pudo abrir la imagen: {problema}")
            return
        foto_seleccionada["ruta"] = Path(ruta)
        vista_foto.configure(image=foto, text="")
        vista_foto.image = foto

    ctk.CTkButton(
        formulario, text="Seleccionar fotografía", height=34, fg_color=morado,
        hover_color=morado_oscuro, text_color=blanco, command=seleccionar_foto
    ).pack(fill="x", pady=(2, 8))

    ctk.CTkLabel(
        formulario, text="Tallas y existencias", text_color=texto, anchor="w",
        font=ctk.CTkFont(family=letra_titulo, size=18, weight="bold")
    ).pack(fill="x", pady=(4, 4))
    filas_tallas = ctk.CTkFrame(formulario, fg_color=fondo)
    filas_tallas.pack(fill="x")
    entradas_tallas = []

    def agregar_fila_talla(talla="", cantidad=""):
        fila = ctk.CTkFrame(filas_tallas, fg_color=fondo)
        fila.pack(fill="x", pady=2)
        talla_entrada = ctk.CTkEntry(
            fila, placeholder_text="Talla", height=34, fg_color=blanco,
            border_color=borde, text_color=texto, placeholder_text_color=gris
        )
        def normalizar_talla(evento=None):
            valor = talla_entrada.get()
            normalizado = valor.upper()
            if valor != normalizado:
                posicion = talla_entrada.index("insert")
                talla_entrada.delete(0, "end")
                talla_entrada.insert(0, normalizado)
                talla_entrada.icursor(min(posicion, len(normalizado)))

        talla_entrada.bind("<KeyRelease>", normalizar_talla)
        talla_entrada.pack(side="left", fill="x", expand=True, padx=(0, 4))
        cantidad_entrada = ctk.CTkEntry(
            fila, placeholder_text="Cantidad", height=34, fg_color=blanco,
            border_color=borde, text_color=texto, placeholder_text_color=gris
        )
        cantidad_entrada.pack(side="left", fill="x", expand=True)
        if talla:
            talla_entrada.insert(0, str(talla).upper())
        if cantidad != "":
            cantidad_entrada.insert(0, str(cantidad))
        entradas_tallas.append((talla_entrada, cantidad_entrada))

    variantes_iniciales = list(variantes.itertuples(index=False)) if variantes is not None else []
    for variante in variantes_iniciales:
        agregar_fila_talla(variante.Talla, variante.Cantidad)
    if not entradas_tallas:
        agregar_fila_talla()
    ctk.CTkButton(
        formulario, text="+ Agregar talla", height=30, fg_color="transparent",
        hover_color=borde, text_color=morado, command=agregar_fila_talla
    ).pack(anchor="w", pady=(3, 8))

    def guardar():
        datos_tallas = []
        vistas = set()
        for talla_entrada, cantidad_entrada in entradas_tallas:
            talla = talla_entrada.get().strip().upper()
            cantidad = cantidad_entrada.get().strip()
            if not talla and not cantidad:
                continue
            if not talla or not cantidad:
                messagebox.showerror("Datos incompletos", "Cada talla debe tener una cantidad.")
                return
            if talla.casefold() in vistas:
                messagebox.showerror("Talla repetida", "No puedes registrar la misma talla dos veces.")
                return
            vistas.add(talla.casefold())
            datos_tallas.append((talla, cantidad))
        if not datos_tallas:
            messagebox.showerror("Tallas requeridas", "Agrega al menos una talla con su cantidad.")
            return
        codigo_valor = codigo.get().strip() if not editar else str(producto["Codigo"])
        if foto_seleccionada["ruta"] is not None:
            destino_foto = carpeta_imagenes / (
                f"{codigo_valor}{foto_seleccionada['ruta'].suffix.casefold()}"
            )
            if destino_foto.exists() and not messagebox.askyesno(
                "Reemplazar fotografía",
                f"Ya existe una fotografía para {codigo_valor}. ¿Deseas reemplazarla?",
                parent=ventana_formulario
            ):
                return
        try:
            if editar:
                actualizar_producto(
                    codigo_valor, nombre.get().strip(), seccion.get(), tipo.get().strip(),
                    precio.get().strip(), descripcion.get().strip(), estado.get()
                )
                existentes = {
                    str(fila.Talla).casefold() for fila in variantes_iniciales
                }
                for talla, cantidad in datos_tallas:
                    if talla.casefold() in existentes:
                        actualizar_existencias(codigo_valor, talla, cantidad)
                    else:
                        agregar_variante_existencias(codigo_valor, talla, cantidad)
            else:
                registrar_producto(
                    codigo_valor, nombre.get().strip(), seccion.get(), tipo.get().strip(),
                    precio.get().strip(), descripcion.get().strip(), estado.get()
                )
                for talla, cantidad in datos_tallas:
                    agregar_variante_existencias(codigo_valor, talla, cantidad)
            _copiar_fotografia_producto(codigo_valor, foto_seleccionada["ruta"])
        except (OSError, ValueError, PermissionError) as problema:
            messagebox.showerror("No se pudo guardar", str(problema))
            return
        ventana_formulario.destroy()
        if actualizar_lista:
            actualizar_lista()
        else:
            _mostrar_inventario()
        mensaje_admin.configure(text="¡Prenda guardada exitosamente!", text_color=verde)

    ctk.CTkButton(
        formulario, text="Guardar prenda", height=40, fg_color=morado,
        hover_color=morado_oscuro, text_color=blanco, command=guardar
    ).pack(fill="x", pady=(8, 3))
    ctk.CTkButton(
        formulario, text="Cancelar", height=34, fg_color="transparent",
        hover_color=borde, text_color=morado, command=ventana_formulario.destroy
    ).pack(fill="x", pady=(0, 8))


def _copiar_fotografia_producto(codigo, origen):
    if origen is None:
        return
    carpeta_imagenes.mkdir(parents=True, exist_ok=True)
    extension = origen.suffix.casefold()
    destino = carpeta_imagenes / f"{codigo}{extension}"
    shutil.copy2(origen, destino)
    for otra_extension in (".jpg", ".jpeg", ".png"):
        otra = carpeta_imagenes / f"{codigo}{otra_extension}"
        if otra != destino and otra.exists():
            otra.unlink()


def _mostrar_compras_admin():
    _limpiar_admin()
    _titulo_admin("Compras")
    try:
        compras = listar_compras_administracion()
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return
    if not compras:
        _tarjeta_admin("No hay compras registradas.")
    for compra in reversed(compras):
        articulos = ", ".join(
            f"{articulo['Nombre']} x{articulo['Cantidad']}" for articulo in compra["Articulos"]
        )
        _tarjeta_admin(
            f"{compra['Pedido']} · {formatear_pesos(compra['Total'])}",
            f"Cliente: {compra['Correo']}\nFecha: {compra['Fecha']} · Estado: {compra['Estado']}\n{articulos}"
        )


def _mostrar_alquileres_admin(solo_devoluciones=False):
    _limpiar_admin()
    _titulo_admin("Devoluciones" if solo_devoluciones else "Alquileres")
    try:
        alquileres = listar_alquileres_administracion()
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return
    if solo_devoluciones:
        alquileres = [alquiler for alquiler in alquileres if alquiler["Estado"].casefold() == "devuelto"]
    if not alquileres:
        _tarjeta_admin("No hay registros para mostrar.")
    for alquiler in reversed(alquileres):
        detalle = (
            f"Cliente: {alquiler['Correo']}\n"
            f"Fechas: {alquiler['FechaAlquiler']} - {alquiler['FechaProgramada']} | "
            f"Talla: {alquiler['Talla']} | Estado: {alquiler['Estado']}"
        )
        if alquiler["FechaReal"]:
            detalle += f"\nDevolución real: {alquiler['FechaReal']}"
        _tarjeta_admin(
            f"{alquiler['Nombre']} · {alquiler['Codigo']} · {formatear_pesos(float(alquiler['Precio']))}",
            detalle
        )


def _mostrar_clientes_admin():
    _limpiar_admin()
    _titulo_admin("Clientes")
    try:
        clientes = listar_clientes_administracion()
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return
    if not clientes:
        _tarjeta_admin("No hay clientes registrados.")
    for cliente in clientes:
        nombre = cliente["Nombre"] if cliente["Nombre"] != "Sin datos" else "Perfil sin datos personales"
        _tarjeta_admin(nombre, cliente["Correo"])


def _mostrar_estadisticas_admin():
    _limpiar_admin()
    _titulo_admin("Estadísticas")
    try:
        estadisticas = obtener_estadisticas_administracion()
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return
    nombres = (
        "Compras confirmadas", "Unidades vendidas", "Ventas simuladas",
        "Alquileres registrados", "Alquileres activos", "Devoluciones",
        "Productos activos", "Trajes activos",
    )
    tarjetas_estadisticas = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    tarjetas_estadisticas.pack(fill="x", padx=4, pady=(0, 8))
    for columna in range(2):
        tarjetas_estadisticas.grid_columnconfigure(columna, weight=1)
    for indice, nombre in enumerate(nombres):
        valor = estadisticas[nombre]
        _tarjeta_estadistica(
            tarjetas_estadisticas, nombre,
            formatear_pesos(valor) if nombre == "Ventas simuladas" else valor
        ).grid(row=indice // 2, column=indice % 2, sticky="nsew", padx=4, pady=4)


def mostrar_panel_admin(seccion="Dashboard"):
    if not es_administrador(sesion_actual.correo):
        aviso.configure(text="No tienes permisos para acceder al panel administrativo.", text_color=rojo)
        return
    acciones = {
        "Dashboard": _mostrar_dashboard,
        "Inventario": _mostrar_inventario,
        "Compras": _mostrar_compras_admin,
        "Alquileres": lambda: _mostrar_alquileres_admin(False),
        "Devoluciones": lambda: _mostrar_alquileres_admin(True),
        "Clientes": _mostrar_clientes_admin,
        "Estadísticas": _mostrar_estadisticas_admin,
    }
    acciones.get(seccion, _mostrar_dashboard)()
    mostrar(pantalla_admin)


secciones_admin = ["Dashboard", "Inventario", "Compras", "Alquileres", "Devoluciones", "Clientes", "Estadísticas"]
for indice_seccion, nombre_seccion in enumerate(secciones_admin):
    ctk.CTkButton(
        barra_admin, text=nombre_seccion,
        command=lambda seccion=nombre_seccion: mostrar_panel_admin(seccion),
        height=30, fg_color=color_admin_dorado, hover_color=color_admin_dorado_oscuro,
        text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")
    ).grid(
        row=indice_seccion // 2,
        column=indice_seccion % 2,
        sticky="ew", padx=4, pady=3
    )

ctk.CTkButton(
    pantalla_admin, text="← Volver al menú cliente", command=lambda: mostrar(pantalla_menu),
    fg_color=morado, hover_color=morado_oscuro, text_color=blanco,
    font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")
).pack(fill="x", padx=18, pady=(0, 14))
ctk.CTkButton(
    pantalla_admin, text="Cerrar sesión", command=cerrar_sesion_interfaz,
    fg_color="transparent", hover_color=borde, text_color=morado,
    font=ctk.CTkFont(family=letra_texto, size=13, weight="bold")
).pack(pady=(0, 12))

#INICIO
# PANTALLA: INICIO
pantalla_inicio = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)

ctk.CTkButton(pantalla_inicio, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=morado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 8))

bienvenida_inicio = ctk.CTkFrame(pantalla_inicio, fg_color=morado, corner_radius=16)
bienvenida_inicio.pack(fill="x", padx=24, pady=(0, 18))

ctk.CTkLabel(bienvenida_inicio, text="¡Bienvenidos a\nEFRATA Mini-Mall!", text_color=blanco, justify="center", font=ctk.CTkFont(family=letra_titulo, size=26, weight="bold")).pack(pady=(22, 6))
ctk.CTkLabel(bienvenida_inicio, text="Moda, alquiler de trajes y arreglos\nen un solo lugar", text_color=borde, justify="center", font=ctk.CTkFont(family=letra_texto, size=14)).pack(pady=(0, 16))

# Botones de acceso rápido
accesos = ctk.CTkFrame(bienvenida_inicio, fg_color=morado)
accesos.pack(pady=(0, 22))
ctk.CTkButton(accesos, text="Ver ropa", command=mostrar_catalogo_ropa, width=140, height=40, corner_radius=10, fg_color=blanco, hover_color=borde, text_color=morado, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(side="left", padx=6)
ctk.CTkButton(accesos, text="Alquilar trajes", command=mostrar_trajes, width=140, height=40, corner_radius=10, fg_color="transparent", border_width=2, border_color=blanco, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(side="left", padx=6)

ctk.CTkLabel(pantalla_inicio, text="Lo que ofrecemos", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_titulo, size=18, weight="bold")).pack(fill="x", padx=24, pady=(0, 8))

fila_servicios = ctk.CTkFrame(pantalla_inicio, fg_color=fondo)
fila_servicios.pack(fill="x", padx=20, pady=(0, 18))

for icono, servicio in [("👗", "Moda nacional\ne importada"), ("🤵", "Trajes para\ntoda ocasión"), ("🧵", "Arreglo\nde ropa")]:
    tarjeta_servicio = ctk.CTkFrame(fila_servicios, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
    tarjeta_servicio.pack(side="left", fill="both", expand=True, padx=4)
    ctk.CTkLabel(tarjeta_servicio, text=icono, font=ctk.CTkFont(size=30)).pack(pady=(14, 2))
    ctk.CTkLabel(tarjeta_servicio, text=servicio, text_color=texto, justify="center", font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")).pack(padx=6, pady=(0, 14))


contacto = ctk.CTkFrame(pantalla_inicio, fg_color=blanco, corner_radius=12, border_width=1, border_color=borde)
contacto.pack(fill="x", padx=24, pady=(0, 16))
ctk.CTkLabel(contacto, text="📍  Cali, Colombia", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15)).pack(fill="x", padx=18, pady=(12, 4))
ctk.CTkLabel(contacto, text="📞  323 965 5863", text_color=texto, anchor="w", font=ctk.CTkFont(family=letra_texto, size=15)).pack(fill="x", padx=18, pady=(4, 12))

ctk.CTkLabel(pantalla_inicio, text="¡Será un placer atenderte! 💜", text_color=morado, font=ctk.CTkFont(family=letra_texto, size=16, weight="bold")).pack(pady=(4, 0))

#Ventana calendario GRANDE 

ventana_calendario = None

def abrir_calendario(variable):
    global ventana_calendario

    if ventana_calendario is not None and ventana_calendario.winfo_exists():
        ventana_calendario.lift()
        return

    ventana_calendario = ctk.CTkToplevel(ventana)
    ventana_calendario.title("Seleccionar fecha")
    ventana_calendario.geometry("390x400")
    ventana_calendario.resizable(False, False)
    ventana_calendario.configure(fg_color=fondo)
    ventana_calendario.transient(ventana)
    ventana_calendario.after(200, ventana_calendario.lift)

    calendario = Calendar(ventana_calendario, selectmode="day", date_pattern="dd/mm/yyyy", locale="es_ES",
                          mindate=datetime.date.today(), font=(letra_texto, 12),
                          background=morado, foreground=blanco, headersbackground=morado, headersforeground=blanco,
                          selectbackground=morado, selectforeground=blanco,
                          normalbackground=blanco, normalforeground=texto,
                          weekendbackground=borde, weekendforeground=texto)
    calendario.pack(padx=20, pady=20, fill="both", expand=True)

    def confirmar_fecha():
        fecha = calendario.selection_get()
        if fecha is not None:
            variable.set(fecha.strftime("%d/%m/%Y"))
        ventana_calendario.destroy()

    ctk.CTkButton(ventana_calendario, text="Confirmar fecha", command=confirmar_fecha, height=40, corner_radius=10, fg_color=morado, hover_color=morado_oscuro, text_color=blanco, font=ctk.CTkFont(family=letra_texto, size=14, weight="bold")).pack(padx=20, pady=(0, 20), fill="x")













def ejecutar_interfaz():
    ventana.mainloop()


if __name__ == "__main__":
    ejecutar_interfaz()
