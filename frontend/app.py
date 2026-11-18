import sys
import shutil
import logging
from pathlib import Path
import datetime
from tkinter import TclError, filedialog, messagebox
sys.path.append(str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps
from tkcalendar import Calendar
from backend import (
    autenticar_usuario, cerrar_sesion, cargar_trajes, registrar_alquiler,
    hay_conflicto_alquiler,
    sesion_actual, obtener_alquileres_usuario, devolver_alquiler,
    registrar_usuario, leer_datos_personales, guardar_datos_personales,
    validar_perfil_completo,
    cargar_catalogo_ropa, filtrar_catalogo_ropa, agregar_al_carrito,
    obtener_detalles_carrito, actualizar_cantidad_carrito, eliminar_del_carrito,
    preparar_compra, confirmar_compra, listar_compras, listar_favoritos,
    agregar_favorito, eliminar_favorito, cargar_descripciones_trajes,
    es_administrador, cargar_inventario_administracion,
    listar_clientes_administracion, listar_compras_administracion,
    listar_alquileres_administracion, obtener_estadisticas_administracion,
    guardar_producto_completo, desactivar_producto,
    cargar_trajes_administracion, registrar_traje, actualizar_traje,
)

logger = logging.getLogger(__name__)

# Identidad visual compartida: carbón, champagne, marfil y blanco.
champagne = "#B99A78"
champagne_oscuro = "#9D7D5D"
champagne_texto = "#76583A"
fondo = "#F3EEE5"
blanco = "#FFFFFF"
texto = "#151515"
gris = "#655C52"
borde = "#DED5C9"
rojo = "#B42318"
verde = "#1D7348"
letra_titulo = "Georgia"
letra_texto = "Segoe UI"
RADIO_CONTROL = 10
RADIO_TARJETA = 12
ANCHO_CONTENIDO_MAXIMO = 1360
PUNTO_QUIEBRE_ANCHO = 760

ctk.set_appearance_mode("light")


def fuente_titulo(size=24, weight=None):
    opciones = {"family": letra_titulo, "size": size}
    if weight:
        opciones["weight"] = weight
    return ctk.CTkFont(**opciones)


def fuente_texto(size=14, weight=None):
    opciones = {"family": letra_texto, "size": size}
    if weight:
        opciones["weight"] = weight
    return ctk.CTkFont(**opciones)


class Boton(ctk.CTkButton):
    VARIANTES = {
        "principal": {
            "height": 42, "corner_radius": RADIO_CONTROL,
            "fg_color": texto, "hover_color": "#333333",
            "text_color": blanco, "border_width": 1,
            "border_color": champagne,
        },
        "secundario": {
            "height": 38, "corner_radius": RADIO_CONTROL,
            "fg_color": "transparent", "hover_color": borde,
            "text_color": champagne_texto,
        },
        "destructivo": {
            "height": 38, "corner_radius": RADIO_CONTROL,
            "fg_color": "transparent", "hover_color": "#F5E5E1",
            "text_color": rojo, "border_width": 1,
            "border_color": rojo,
        },
    }

    def __init__(self, master, *, variant=None, **kwargs):
        if variant is None:
            variant = "secundario" if kwargs.get("fg_color") == "transparent" else "principal"
        opciones = dict(self.VARIANTES.get(variant, self.VARIANTES["principal"]))
        opciones.update(kwargs)
        opciones.setdefault("font", fuente_texto(14, "bold"))
        super().__init__(master, **opciones)


class CampoTexto(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        opciones = {
            "height": 42, "corner_radius": RADIO_CONTROL,
            "fg_color": blanco, "border_color": borde,
            "text_color": texto, "placeholder_text_color": gris,
            "font": fuente_texto(14),
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


def crear_campo_clave(parent, placeholder_text="", height=44):
    contenedor = ctk.CTkFrame(parent, fg_color=blanco)
    campo = CampoTexto(
        contenedor,
        placeholder_text=placeholder_text,
        height=height,
        show="*",
    )
    campo._entry.configure(show="*")
    campo.pack(side="left", fill="x", expand=True)
    mostrando = {"activo": False}

    def crear_icono_ojo(abierto):
        lienzo = Image.new("RGBA", (22, 22), (0, 0, 0, 0))
        dibujo = ImageDraw.Draw(lienzo)
        if abierto:
            dibujo.arc((3, 4, 19, 18), 25, 155, fill="#655C52", width=2)
            dibujo.arc((3, 4, 19, 18), 205, 335, fill="#655C52", width=2)
            dibujo.ellipse((8, 8, 14, 14), outline="#655C52", width=2)
        else:
            dibujo.arc((3, 5, 19, 17), 25, 155, fill="#655C52", width=2)
            dibujo.arc((3, 5, 19, 17), 205, 335, fill="#655C52", width=2)
            dibujo.line((4, 18, 18, 4), fill="#655C52", width=2)
        return ctk.CTkImage(light_image=lienzo, size=(22, 22))

    icono_ver = crear_icono_ojo(False)
    icono_ocultar = crear_icono_ojo(True)

    def alternar():
        mostrando["activo"] = not mostrando["activo"]
        campo._entry.configure(show="" if mostrando["activo"] else "*")
        boton_ojo.configure(image=icono_ocultar if mostrando["activo"] else icono_ver)

    boton_ojo = Boton(
        contenedor,
        text="",
        image=icono_ver,
        width=38,
        height=height,
        fg_color="transparent",
        hover_color=borde,
        command=alternar,
    )
    boton_ojo.pack(side="right", padx=(6, 0))
    return contenedor, campo


class Selector(ctk.CTkOptionMenu):
    def __init__(self, master, **kwargs):
        opciones = {
            "height": 40, "corner_radius": RADIO_CONTROL,
            "fg_color": blanco, "button_color": champagne,
            "button_hover_color": champagne_oscuro,
            "text_color": texto, "dropdown_fg_color": blanco,
            "dropdown_text_color": texto, "font": fuente_texto(14),
        }
        opciones.update(kwargs)
        super().__init__(master, **opciones)


def crear_tarjeta(parent, **kwargs):
    opciones = {
        "fg_color": blanco, "corner_radius": RADIO_TARJETA,
        "border_width": 1, "border_color": borde,
    }
    opciones.update(kwargs)
    return ctk.CTkFrame(parent, **opciones)


def crear_miniatura_producto(parent, codigo, size=(92, 118), icono="🛍️"):
    ancho, alto = size
    contenedor = ctk.CTkFrame(
        parent, fg_color=fondo, corner_radius=8, width=ancho, height=alto
    )
    contenedor.pack_propagate(False)
    ruta = next(
        (carpeta_imagenes / (codigo + extension)
         for extension in (".jpg", ".jpeg", ".png")
         if (carpeta_imagenes / (codigo + extension)).is_file()),
        None,
    )
    if ruta is None:
        ctk.CTkLabel(
            contenedor, text=icono, text_color=gris,
            font=ctk.CTkFont(size=28)
        ).pack(expand=True)
        return contenedor
    with Image.open(ruta) as original:
        imagen = ImageOps.exif_transpose(original).convert("RGB")
    imagen = ImageOps.contain(
        imagen, (ancho - 8, alto - 8), method=Image.Resampling.LANCZOS
    )
    clave_cache = (str(ruta), imagen.size)
    foto = cache_ctk_imagenes.get(clave_cache)
    if foto is None:
        foto = ctk.CTkImage(light_image=imagen, size=imagen.size)
        cache_ctk_imagenes[clave_cache] = foto
    etiqueta = ctk.CTkLabel(contenedor, image=foto, text="")
    etiqueta.image = foto
    etiqueta.bind("<Button-1>", lambda evento: ampliar_fotografia(codigo))
    etiqueta.configure(cursor="hand2")
    etiqueta.pack(expand=True)
    return contenedor


def vincular_ajuste_de_texto(contenedor, etiqueta, ancho_minimo=150, margen=8):
    def ajustar(evento=None):
        if evento is None or evento.widget is contenedor:
            nuevo_ancho = max(ancho_minimo, contenedor.winfo_width() - margen)
            if getattr(etiqueta, "_wraplength_actual", None) != nuevo_ancho:
                etiqueta.configure(wraplength=nuevo_ancho)
                etiqueta._wraplength_actual = nuevo_ancho
    contenedor.bind("<Configure>", ajustar, add="+")
    contenedor.after_idle(ajustar)


def ampliar_fotografia(codigo, icono="🛍️"):
    ruta = next(
        (carpeta_imagenes / (str(codigo) + extension)
         for extension in (".jpg", ".jpeg", ".png")
         if (carpeta_imagenes / (str(codigo) + extension)).is_file()),
        None,
    )
    dialogo = ctk.CTkToplevel(ventana)
    dialogo.title(f"Fotografía - {codigo}")
    dialogo.configure(fg_color=fondo)
    dialogo.transient(ventana)
    dialogo.resizable(True, True)

    contenido = crear_tarjeta(dialogo)
    contenido.pack(fill="both", expand=True, padx=14, pady=14)

    if ruta is None:
        ctk.CTkLabel(
            contenido,
            text=icono,
            text_color=gris,
            font=ctk.CTkFont(size=72),
        ).pack(expand=True, fill="both", padx=20, pady=20)
    else:
        with Image.open(ruta) as original:
            imagen = ImageOps.exif_transpose(original).convert("RGB")
        escala = contenido._get_widget_scaling()
        ancho_disponible = max(200, min(720, int((dialogo.winfo_screenwidth() - 100) / escala)))
        alto_disponible = max(200, min(620, int((dialogo.winfo_screenheight() - 200) / escala)))
        imagen = ImageOps.contain(
            imagen,
            (ancho_disponible, alto_disponible),
            method=Image.Resampling.LANCZOS,
        )
        clave_cache = (str(ruta), "ampliada", imagen.size)
        foto = cache_ctk_imagenes.get(clave_cache)
        if foto is None:
            foto = ctk.CTkImage(light_image=imagen, size=imagen.size)
            cache_ctk_imagenes[clave_cache] = foto
        etiqueta = ctk.CTkLabel(contenido, image=foto, text="")
        etiqueta.image = foto
        etiqueta.pack(expand=True, fill="both", padx=12, pady=12)

    Boton(dialogo, text="Cerrar", command=dialogo.destroy, width=120).pack(pady=(0, 12))

    ventana.update_idletasks()
    escala = dialogo._get_window_scaling()
    ancho = min(760, max(200, int((dialogo.winfo_screenwidth() - 40) / escala)))
    alto = min(700, max(200, int((dialogo.winfo_screenheight() - 100) / escala)))
    dialogo.geometry(f"{ancho}x{alto}")
    if not dialogo.winfo_viewable():
        dialogo.wait_visibility()
    dialogo.update_idletasks()
    ancho_real, alto_real = dialogo.winfo_width(), dialogo.winfo_height()
    x = ventana.winfo_rootx() + (ventana.winfo_width() - ancho_real) // 2
    y = ventana.winfo_rooty() + (ventana.winfo_height() - alto_real) // 2
    x = max(0, min(x, dialogo.winfo_screenwidth() - ancho_real - 20))
    y = max(0, min(y, dialogo.winfo_screenheight() - alto_real - 64))
    # Las posiciones y medidas de winfo están en píxeles de pantalla.
    # Evitar que CustomTkinter vuelva a escalar estas coordenadas.
    dialogo.tk.call("wm", "geometry", dialogo._w, f"+{x}+{y}")
    dialogo.grab_set()


def preguntar_confirmacion_cliente(titulo, mensaje):
    dialogo = ctk.CTkToplevel(ventana)
    dialogo.title(titulo)
    dialogo.configure(fg_color=fondo)
    dialogo.resizable(False, False)
    dialogo.transient(ventana)
    ventana.update_idletasks()
    pantalla_ancho = dialogo.winfo_screenwidth()
    pantalla_alto = dialogo.winfo_screenheight()
    ancho = min(400, max(320, pantalla_ancho - 32))
    alto = min(240, max(200, pantalla_alto - 48))
    x = ventana.winfo_rootx() + (ventana.winfo_width() - ancho) // 2
    y = ventana.winfo_rooty() + (ventana.winfo_height() - alto) // 2
    x = min(max(x, 0), max(pantalla_ancho - ancho, 0))
    y = min(max(y, 0), max(pantalla_alto - alto, 0))
    dialogo.geometry(f"{ancho}x{alto}+{x}+{y}")

    contenido = crear_tarjeta(dialogo)
    contenido.pack(fill="both", expand=True, padx=14, pady=14)
    ctk.CTkLabel(
        contenido, text=titulo, text_color=texto, anchor="w",
        justify="left", wraplength=ancho - 72,
        font=fuente_titulo(size=19, weight="bold")
    ).pack(fill="x", padx=16, pady=(14, 6))
    ctk.CTkLabel(
        contenido, text=mensaje, text_color=gris, anchor="w",
        justify="left", wraplength=ancho - 72,
        font=fuente_texto(size=14)
    ).pack(fill="both", expand=True, padx=16, pady=(0, 10))

    respuesta = {"confirmar": False}
    botones = ctk.CTkFrame(contenido, fg_color=blanco)
    botones.pack(fill="x", padx=14, pady=(0, 12))
    Boton(
        botones, text="Cancelar", variant="secundario", height=38,
        command=dialogo.destroy
    ).pack(side="right", padx=(6, 0))
    def confirmar():
        respuesta["confirmar"] = True
        dialogo.destroy()
    Boton(
        botones, text="Confirmar", variant="principal", height=38,
        command=confirmar
    ).pack(side="right")
    dialogo.protocol("WM_DELETE_WINDOW", dialogo.destroy)
    dialogo.bind("<Escape>", lambda evento: dialogo.destroy())
    dialogo.grab_set()
    dialogo.focus_force()
    ventana.wait_window(dialogo)
    return respuesta["confirmar"]


def _centrar_panel_formulario(pantalla, panel, ancho_maximo):
    pantalla.grid_columnconfigure(0, weight=1)
    pantalla.grid_columnconfigure(1, weight=0)
    pantalla.grid_columnconfigure(2, weight=1)
    pantalla.grid_rowconfigure(0, weight=1)

    def ajustar(evento=None):
        if evento is not None and evento.widget not in (pantalla, ventana):
            return
        ancho_area = pantalla.winfo_width()
        if ancho_area <= 1:
            ancho_area = ventana.winfo_width()
        ancho = max(300, min(ancho_maximo, ancho_area - 32))
        pantalla.grid_columnconfigure(1, weight=0, minsize=ancho)
        if not getattr(panel, "_formulario_fijo", False):
            alto = max(1, panel.winfo_reqheight())
            panel.configure(width=ancho, height=alto)
            panel.grid_propagate(False)
            panel._formulario_fijo = True
        else:
            panel.configure(width=ancho)
        if not panel.winfo_manager():
            panel.grid(row=0, column=1, sticky="ew")

    pantalla.bind("<Configure>", ajustar, add="+")
    pantalla.after_idle(ajustar)


def _organizar_tarjetas_adaptables(contenedor, ancho_minimo=280, columnas_maximas=4, separacion=16):
    if not getattr(contenedor, "_rejilla_adaptable_vinculada", False):
        def al_redimensionar(evento, objetivo=contenedor):
            if evento.widget is not objetivo or getattr(objetivo, "_rejilla_pendiente", False):
                return
            objetivo._rejilla_pendiente = True
            def aplicar():
                objetivo._rejilla_pendiente = False
                _organizar_tarjetas_adaptables(
                    objetivo, ancho_minimo, columnas_maximas, separacion
                )
            objetivo.after_idle(aplicar)
        contenedor.bind("<Configure>", al_redimensionar, add="+")
        contenedor._rejilla_adaptable_vinculada = True

    ancho = contenedor.winfo_width()
    if ancho <= 1:
        ancho = max(1, contenedor.winfo_reqwidth())
    columnas = max(1, min(
        columnas_maximas,
        (ancho + separacion) // (ancho_minimo + separacion)
    ))
    widgets = contenedor.winfo_children()
    if getattr(contenedor, "_limitar_columnas_a_elementos", False):
        elementos_visibles = sum(
            not getattr(widget, "_ocupar_columnas_adaptables", False)
            for widget in widgets
        )
        columnas = min(columnas, max(1, elementos_visibles))
    layout_actual = (
        columnas,
        tuple(str(widget) for widget in widgets),
    )
    if getattr(contenedor, "_layout_tarjetas_actual", None) == layout_actual:
        return
    contenedor._layout_tarjetas_actual = layout_actual
    for columna in range(columnas_maximas):
        contenedor.grid_columnconfigure(columna, weight=1 if columna < columnas else 0)

    for indice, widget in enumerate(widgets):
        span = columnas if getattr(widget, "_ocupar_columnas_adaptables", False) else 1
        widget.grid(
            row=indice // columnas, column=indice % columnas,
            columnspan=span, sticky="nsew",
            padx=separacion // 2, pady=separacion // 2
        )


def _distribuir_controles_adaptable(contenedor, controles):
    if not getattr(contenedor, "_filtros_adaptables_vinculados", False):
        def al_redimensionar(evento, objetivo=contenedor, elementos=tuple(controles)):
            if evento.widget is not objetivo or getattr(objetivo, "_filtros_pendientes", False):
                return
            objetivo._filtros_pendientes = True
            def aplicar():
                objetivo._filtros_pendientes = False
                _distribuir_controles_adaptable(objetivo, elementos)
            objetivo.after_idle(aplicar)
        contenedor.bind("<Configure>", al_redimensionar, add="+")
        contenedor._filtros_adaptables_vinculados = True

    ancho = contenedor.winfo_width()
    if ancho <= 1:
        ancho = max(1, contenedor.winfo_reqwidth())
    columnas = 4 if ancho >= 820 else (2 if ancho >= 450 else 1)
    for columna in range(4):
        contenedor.grid_columnconfigure(columna, weight=1 if columna < columnas else 0)
    for indice, control in enumerate(controles):
        control.grid(
            row=indice // columnas, column=indice % columnas,
            sticky="ew", padx=4, pady=4
        )


#Crear la ventana
carpeta_imagenes = Path(__file__).resolve().parent / "imagenes"
ruta_logo_marca = carpeta_imagenes / "efrata_logo_ui.png"
imagen_logo_marca = None
cache_ctk_imagenes = {}
if ruta_logo_marca.is_file():
    with Image.open(ruta_logo_marca) as original_logo:
        imagen_logo_marca = ImageOps.exif_transpose(original_logo).convert("RGB")

ventana = ctk.CTk()
ventana.title("EFRATA Mini-Mall")
ventana.geometry("420x760")
ventana.minsize(360, 560)
ventana.resizable(True, True)
ventana.configure(fg_color=fondo)

encabezado = ctk.CTkFrame(ventana, fg_color=texto, corner_radius=0, height=70)
encabezado.pack_propagate(False)
ctk.CTkLabel(
    encabezado, text="EFRATA Mini-Mall", text_color=champagne,
    font=fuente_titulo(size=22, weight="bold")
).place(relx=0.5, rely=0.5, anchor="center")

# Viewport centrado para conservar el formato compacto y limitar la lectura
# en pantallas amplias. Las siguientes etapas pueden activar cuadrículas aquí.
contenedor_vistas = ctk.CTkFrame(ventana, fg_color=fondo, corner_radius=0)


def ventana_amplia():
    return ventana.winfo_width() >= PUNTO_QUIEBRE_ANCHO


def _actualizar_layout(evento=None):
    if evento is not None and evento.widget is not ventana:
        return
    ancho_ventana = max(1, ventana.winfo_width())
    alto_ventana = max(1, ventana.winfo_height())
    pantalla_sin_encabezado = globals().get("pantalla_actual") in (
        globals().get("pantalla_login"), globals().get("pantalla_registro")
    )
    alto_encabezado = 0 if pantalla_sin_encabezado else encabezado.winfo_reqheight()
    ancho_vistas = min(ancho_ventana, ANCHO_CONTENIDO_MAXIMO)
    alto_vistas = max(1, alto_ventana - alto_encabezado)
    contenedor_vistas.place(
        relx=0.5, rely=0, anchor="n", y=alto_encabezado,
        relwidth=ancho_vistas / ancho_ventana,
        relheight=alto_vistas / alto_ventana,
    )

ventana.bind("<Configure>", _actualizar_layout, add="+")

pantalla_login = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)
pantalla_login.pack(fill="both", expand=True)
contenedor_login = ctk.CTkFrame(pantalla_login, fg_color=fondo, corner_radius=0)
logo_acceso = None
if imagen_logo_marca is not None:
    logo_acceso = ctk.CTkImage(
        light_image=imagen_logo_marca,
        size=(310, round(310 * imagen_logo_marca.height / imagen_logo_marca.width)),
    )

def agregar_espacio_logo_acceso(contenedor):
    espacio_logo = ctk.CTkFrame(
        contenedor, width=330, height=330, fg_color=fondo, corner_radius=0
    )
    espacio_logo.pack_propagate(False)
    if logo_acceso is not None:
        etiqueta_logo = ctk.CTkLabel(
            espacio_logo, text="", image=logo_acceso, fg_color=fondo
        )
        etiqueta_logo.image = logo_acceso
        etiqueta_logo.place(relx=0.5, rely=0.5, anchor="center")
    espacio_logo.pack(anchor="center", pady=(0, 12))
    return espacio_logo

if logo_acceso is not None:
    agregar_espacio_logo_acceso(contenedor_login)
_centrar_panel_formulario(pantalla_login, contenedor_login, 480)

pantalla_actual = pantalla_login
ventana.after(0, _actualizar_layout)

def mostrar(pantalla_nueva):
    global pantalla_actual
    pantalla_actual.pack_forget()
    if pantalla_nueva in (
        globals().get("pantalla_login"), globals().get("pantalla_registro")
    ):
        encabezado.pack_forget()
    elif not encabezado.winfo_manager():
        encabezado.pack(fill="x")
    pantalla_nueva.pack(fill="both", expand=True)
    pantalla_actual = pantalla_nueva
    _actualizar_layout()

iconos_ropa = {"Blusa": "👚", "Vestido": "👗", "Camisa": "👔", "Pantalón": "👖", "Chaqueta": "🧥", "Falda": "👗"}

def mostrar_foto_producto(contenedor, codigo, icono, alto_maximo=360):
    ruta = next(
        (carpeta_imagenes / (codigo + extension)
         for extension in (".jpg", ".jpeg", ".png")
         if (carpeta_imagenes / (codigo + extension)).exists()),
        None,
    )
    area_foto = ctk.CTkFrame(
        contenedor, fg_color=fondo, corner_radius=10, height=250
    )
    area_foto.pack(fill="x", padx=12, pady=(12, 6))
    area_foto.pack_propagate(False)
    etiqueta_foto = ctk.CTkLabel(
        area_foto, text=icono if ruta is None else "",
        font=ctk.CTkFont(size=48), text_color=gris
    )
    etiqueta_foto.pack(expand=True, fill="both")

    imagen_origen = None
    if ruta is not None:
        with Image.open(ruta) as original:
            imagen_origen = ImageOps.exif_transpose(original).convert("RGB")

    ultimo_tamano = None
    def ajustar_foto(evento=None):
        nonlocal ultimo_tamano
        if evento is not None and evento.widget is not area_foto:
            return
        ancho_disponible = min(480, max(150, area_foto.winfo_width() - 20))
        if imagen_origen is None:
            ancho, alto = ancho_disponible, min(alto_maximo, 250)
        else:
            proporcion = imagen_origen.width / imagen_origen.height
            ancho = min(ancho_disponible, round(proporcion * alto_maximo))
            alto = max(210, round(ancho / proporcion))
            if alto > alto_maximo:
                alto = alto_maximo
                ancho = max(1, round(alto * proporcion))
        tamano = (ancho, alto)
        if tamano == ultimo_tamano:
            return
        ultimo_tamano = tamano
        area_foto.configure(height=alto)
        if imagen_origen is not None:
            imagen_ajustada = ImageOps.contain(
                imagen_origen, tamano, method=Image.Resampling.LANCZOS
            )
            clave_cache = (str(ruta), imagen_ajustada.size)
            foto = cache_ctk_imagenes.get(clave_cache)
            if foto is None:
                foto = ctk.CTkImage(
                    light_image=imagen_ajustada, size=imagen_ajustada.size
                )
                cache_ctk_imagenes[clave_cache] = foto
            etiqueta_foto.configure(image=foto, text="")
            etiqueta_foto.image = foto
            etiqueta_foto.bind(
                "<Button-1>",
                lambda evento: ampliar_fotografia(
                    codigo, icono
                )
            )
            etiqueta_foto.configure(cursor="hand2")

    area_foto.bind("<Configure>", ajustar_foto, add="+")
    area_foto.after(0, ajustar_foto)
    return area_foto

# Inicio de sesión
panel_login = crear_tarjeta(contenedor_login)
panel_login.pack(fill="x")
ctk.CTkLabel(
    panel_login, text="Iniciar sesión", text_color=texto,
    font=fuente_titulo(size=25, weight="bold"), anchor="w"
).pack(fill="x", padx=20, pady=(18, 14))
ctk.CTkLabel(
    panel_login, text="Correo electrónico", text_color=texto,
    font=fuente_texto(size=13, weight="bold"), anchor="w"
).pack(fill="x", padx=20)
caja_correo = CampoTexto(
    panel_login, placeholder_text="tunombre@gmail.com", height=44
)
caja_correo.pack(fill="x", padx=20, pady=(5, 12))
ctk.CTkLabel(
    panel_login, text="Contraseña", text_color=texto,
    font=fuente_texto(size=13, weight="bold"), anchor="w"
).pack(fill="x", padx=20)
contenedor_clave_login, caja_clave = crear_campo_clave(
    panel_login, placeholder_text="********", height=44
)
contenedor_clave_login.pack(fill="x", padx=20, pady=(5, 10))
mensaje = ctk.CTkLabel(
    panel_login, text="", text_color=rojo, font=fuente_texto(size=13),
    wraplength=400, justify="left", anchor="w"
)
mensaje.pack(fill="x", padx=20, pady=(0, 4))
vincular_ajuste_de_texto(panel_login, mensaje, ancho_minimo=240, margen=40)

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


def cerrar_sesion_interfaz():
    cerrar_sesion()
    caja_correo.delete(0, "end")
    caja_clave.delete(0, "end")
    mensaje.configure(text="")
    boton_panel_admin.pack_forget()
    mostrar(pantalla_login)

boton_entrar = Boton(
    panel_login, text="Entrar", command=iniciar_sesion_interfaz,
    height=44, font=fuente_texto(size=15, weight="bold")
)
boton_entrar.pack(fill="x", padx=20, pady=(6, 4))

pantalla_menu = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)
menu_scroll = ctk.CTkScrollableFrame(pantalla_menu, fg_color=fondo)
menu_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 10))

ctk.CTkLabel(
    menu_scroll, text="¿Qué quieres hacer hoy?", text_color=texto,
    font=fuente_titulo(size=24, weight="bold"), anchor="w"
).pack(fill="x", padx=12, pady=(20, 2))
bienvenida = ctk.CTkLabel(
    menu_scroll, text="", text_color=gris, font=fuente_texto(size=13), anchor="w"
)
bienvenida.pack(fill="x", padx=12, pady=(0, 12))

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

avisos_menu = ctk.CTkLabel(
    menu_scroll, text="", text_color=gris, font=fuente_texto(size=13)
)
aviso = avisos_menu

grupos_menu = ctk.CTkFrame(menu_scroll, fg_color=fondo)
grupos_menu.pack(fill="x", padx=4, pady=(0, 8))
opciones_por_grupo = [
    ("Inicio y exploración", [("Inicio", "⌂"), ("Buscar ropa", "⌕")]),
    ("Comprar y alquilar", [("Alquilar trajes", "♙"), ("Ver carrito", "▣")]),
    ("Mis actividades", [("Consultar alquileres", "↻"), ("Devolver traje", "↩"), ("Mis compras", "≡")]),
    ("Mi espacio personal", [("Ver favoritos", "♡"), ("Mis datos", "○")]),
]
for indice_grupo, (titulo_grupo, opciones_grupo) in enumerate(opciones_por_grupo):
    grupo = crear_tarjeta(grupos_menu)
    grupo.grid(row=indice_grupo, column=0, sticky="ew", padx=8, pady=8)
    ctk.CTkLabel(
        grupo, text=titulo_grupo, text_color=texto, anchor="w",
        font=fuente_titulo(size=17, weight="bold")
    ).pack(fill="x", padx=14, pady=(12, 6))
    for opcion, icono in opciones_grupo:
        principal = opcion in ("Buscar ropa", "Alquilar trajes")
        Boton(
            grupo, text=f"{icono}   {opcion}",
            command=lambda opcion_o=opcion: abrir_opcion_menu(opcion_o),
            variant="principal" if principal else "secundario",
            height=44, anchor="w",
            fg_color=texto if principal else "transparent",
            hover_color="#333333" if principal else borde,
            text_color=blanco if principal else texto,
            font=fuente_texto(size=15 if principal else 14, weight="bold"),
        ).pack(fill="x", padx=12, pady=4)
_organizar_tarjetas_adaptables(grupos_menu, ancho_minimo=340, columnas_maximas=2)
avisos_menu.pack(fill="x", padx=12, pady=(0, 6))

pie_menu = ctk.CTkFrame(menu_scroll, fg_color=fondo)
pie_menu.pack(fill="x", padx=12, pady=(0, 14))
boton_panel_admin = Boton(
    pie_menu, text="Panel administrativo",
    command=lambda: mostrar_panel_admin("Dashboard"), height=40,
    fg_color=texto, hover_color="#333333", text_color=blanco,
    font=fuente_texto(size=14, weight="bold")
)
boton_cerrar_sesion = Boton(
    pie_menu, text="Cerrar sesión", command=cerrar_sesion_interfaz,
    variant="secundario", fg_color="transparent", hover_color=borde,
    text_color=champagne_texto, font=fuente_texto(size=14, weight="bold")
)
boton_cerrar_sesion.pack(fill="x", padx=4, pady=(6, 0))

#Pantalla trajes
pantalla_trajes = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)

Boton(pantalla_trajes, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold")).pack(fill="x", padx=16, pady=(12, 0))
ctk.CTkLabel(pantalla_trajes, text="Trajes para alquilar", text_color=texto, font=fuente_titulo(size=24, weight="bold"), anchor="w").pack(fill="x", padx=24, pady=(4, 12))

fecha_consulta_inicio = ctk.StringVar(
    value=datetime.date.today().strftime("%d/%m/%Y")
)
fecha_consulta_fin = ctk.StringVar(
    value=(datetime.date.today() + datetime.timedelta(days=1)).strftime("%d/%m/%Y")
)
panel_consulta_disponibilidad = crear_tarjeta(pantalla_trajes)
panel_consulta_disponibilidad.pack(fill="x", padx=16, pady=(0, 10))
ctk.CTkLabel(
    panel_consulta_disponibilidad, text="Consultar disponibilidad por fechas",
    text_color=texto, anchor="w", font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=12, pady=(8, 2))
fila_consulta_fechas = ctk.CTkFrame(panel_consulta_disponibilidad, fg_color="transparent")
fila_consulta_fechas.pack(fill="x", padx=8, pady=(0, 8))

def _crear_control_fecha_consulta(parent, etiqueta, variable):
    grupo = ctk.CTkFrame(parent, fg_color="transparent")
    grupo.pack(side="left", fill="x", expand=True, padx=4)
    ctk.CTkLabel(
        grupo, text=etiqueta, text_color=gris, anchor="w",
        font=fuente_texto(size=11, weight="bold")
    ).pack(fill="x", pady=(0, 2))
    fila = ctk.CTkFrame(grupo, fg_color="transparent")
    fila.pack(fill="x")
    CampoTexto(fila, textvariable=variable, state="readonly", height=36).pack(
        side="left", fill="x", expand=True
    )
    Boton(
        fila, text="📅", width=38, height=36,
        font=ctk.CTkFont(size=15),
        command=lambda: abrir_calendario(variable)
    ).pack(side="left", padx=(4, 0))
    return grupo

_crear_control_fecha_consulta(fila_consulta_fechas, "Desde", fecha_consulta_inicio)
_crear_control_fecha_consulta(fila_consulta_fechas, "Hasta", fecha_consulta_fin)
mensaje_consulta_disponibilidad = ctk.CTkLabel(
    panel_consulta_disponibilidad, text="",
    text_color=rojo, anchor="w", font=fuente_texto(size=12)
)
mensaje_consulta_disponibilidad.pack(fill="x", padx=12, pady=(0, 6))

lista_trajes = ctk.CTkScrollableFrame(pantalla_trajes, fg_color=fondo)
lista_trajes.pack(fill="both", expand=True, padx=12, pady=(0, 12))

def _consultar_tallas_libres(codigo, tallas):
    try:
        inicio = datetime.datetime.strptime(
            fecha_consulta_inicio.get().strip(), "%d/%m/%Y"
        ).date()
        fin = datetime.datetime.strptime(
            fecha_consulta_fin.get().strip(), "%d/%m/%Y"
        ).date()
    except ValueError:
        return None
    if inicio < datetime.date.today() or fin <= inicio:
        return None
    return [
        talla.strip().upper()
        for talla in tallas.split(",")
        if talla.strip() and not hay_conflicto_alquiler(
            codigo, talla.strip(), inicio, fin
        )
    ]

def mostrar_trajes():
    for tarjeta in lista_trajes.winfo_children():
        tarjeta.destroy()

    try:
        inicio_consulta = datetime.datetime.strptime(
            fecha_consulta_inicio.get().strip(), "%d/%m/%Y"
        ).date()
        fin_consulta = datetime.datetime.strptime(
            fecha_consulta_fin.get().strip(), "%d/%m/%Y"
        ).date()
        consulta_valida = inicio_consulta >= datetime.date.today() and fin_consulta > inicio_consulta
    except ValueError:
        consulta_valida = False
    mensaje_consulta_disponibilidad.configure(
        text="" if consulta_valida else "Selecciona fechas válidas; la devolución debe ser posterior al alquiler."
    )

    try:
        trajes = cargar_trajes()
        descripciones = cargar_descripciones_trajes()
    except (OSError, ValueError, ImportError, UnicodeError) as problema:
        mensaje_consulta_disponibilidad.configure(
            text=f"No se pudieron cargar los trajes: {problema}",
            text_color=rojo
        )
        return
    if not trajes:
        vacio = ctk.CTkLabel(
            lista_trajes, text="No hay trajes disponibles para mostrar.",
            text_color=gris, font=fuente_texto(size=14)
        )
        vacio._ocupar_columnas_adaptables = True
        vacio.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
    for codigo, nombre, tallas, precio, estado in trajes:
        tarjeta = crear_tarjeta(lista_trajes)
        tarjeta.grid(row=len(lista_trajes.winfo_children()), column=0, sticky="nsew", padx=8, pady=8)
        mostrar_foto_producto(tarjeta, codigo, "🤵", alto_maximo=380)

        nombre_traje = ctk.CTkLabel(
            tarjeta, text=nombre, text_color=texto, anchor="w",
            justify="left", wraplength=320,
            font=fuente_titulo(size=19, weight="bold")
        )
        nombre_traje.pack(fill="x", padx=16, pady=(10, 2))
        def ajustar_nombre_traje(evento, objetivo=tarjeta, etiqueta=nombre_traje):
            if evento.widget is objetivo:
                etiqueta.configure(wraplength=max(180, objetivo.winfo_width() - 36))
        tarjeta.bind("<Configure>", ajustar_nombre_traje, add="+")
        ctk.CTkLabel(
            tarjeta, text=f"Tallas: {tallas}", text_color=gris, anchor="w",
            font=fuente_texto(size=13)
        ).pack(fill="x", padx=16, pady=(0, 6))
        precio_fila = ctk.CTkFrame(tarjeta, fg_color=blanco)
        precio_fila.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(
            precio_fila, text="Alquiler", text_color=gris, anchor="w",
            font=fuente_texto(size=12, weight="bold")
        ).pack(side="left")
        ctk.CTkLabel(
            precio_fila, text=f"${precio:,}".replace(",", "."),
            text_color=champagne_texto, anchor="e",
            font=fuente_titulo(size=19, weight="bold")
        ).pack(side="right")
        descripcion_texto = descripciones.get(codigo, "").strip()
        if descripcion_texto:
            descripcion = ctk.CTkLabel(
                tarjeta, text=descripcion_texto, text_color=gris,
                anchor="w", justify="left", wraplength=320,
                font=fuente_texto(size=13)
            )
            descripcion.pack(fill="x", padx=16, pady=(2, 8))
            vincular_ajuste_de_texto(
                tarjeta, descripcion, ancho_minimo=180, margen=36
            )

        estado_activo = estado == "Activo"
        tallas_libres = _consultar_tallas_libres(codigo, tallas) if consulta_valida else []
        pie_traje = ctk.CTkFrame(tarjeta, fg_color=blanco)
        pie_traje.pack(side="bottom", fill="x", padx=16, pady=(4, 14))
        texto_estado = (
            "No disponible" if not estado_activo else
            ("Disponible" if tallas_libres else "Sin tallas para estas fechas")
        )
        disponible_periodo = estado_activo and bool(tallas_libres)
        estado_label = ctk.CTkLabel(
            pie_traje, text=texto_estado,
            text_color=verde if disponible_periodo else rojo,
            fg_color="#E8F1E9" if disponible_periodo else "#F5E8E5",
            corner_radius=8, font=fuente_texto(size=12, weight="bold")
        )
        estado_label.pack(anchor="w", pady=(0, 8))
        if estado_activo and tallas_libres:
            ctk.CTkLabel(
                pie_traje, text=f"Tallas libres: {', '.join(tallas_libres)}",
                text_color=gris, anchor="w", font=fuente_texto(size=12)
            ).pack(fill="x", pady=(0, 6))
        Boton(
            pie_traje, text="Alquilar" if disponible_periodo else "No disponible",
            height=40, state="normal" if disponible_periodo else "disabled",
            text_color_disabled=gris, fg_color=texto if disponible_periodo else borde,
            hover_color="#333333", text_color=blanco,
            font=fuente_texto(size=14, weight="bold"),
            command=lambda caracter_c=codigo, numero_n=nombre, talla_t=tallas, producto_p=precio:
                abrir_formulario_alquiler(
                    caracter_c, numero_n, talla_t, producto_p,
                    fecha_consulta_inicio.get(), fecha_consulta_fin.get()
                )
        ).pack(fill="x")

    _organizar_tarjetas_adaptables(lista_trajes, ancho_minimo=320, columnas_maximas=3)
    mostrar(pantalla_trajes)

fecha_consulta_inicio.trace_add("write", lambda *_: mostrar_trajes())
fecha_consulta_fin.trace_add("write", lambda *_: mostrar_trajes())

pantalla_alquiler = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)
panel_formulario_alquiler = crear_tarjeta(pantalla_alquiler)
_centrar_panel_formulario(pantalla_alquiler, panel_formulario_alquiler, 640)
Boton(
    panel_formulario_alquiler, text="← Volver a los trajes",
    command=lambda: mostrar(pantalla_trajes), variant="secundario",
    anchor="w", font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=18, pady=(14, 4))
ctk.CTkLabel(
    panel_formulario_alquiler, text="Alquilar traje", text_color=texto,
    font=fuente_titulo(size=24, weight="bold"), anchor="w"
).pack(fill="x", padx=20, pady=(2, 10))

# Traje seleccionado
traje_seleccionado = ctk.CTkLabel(
    panel_formulario_alquiler, text="", text_color=texto, anchor="w",
    justify="left", font=fuente_texto(size=15, weight="bold")
)
traje_seleccionado.pack(fill="x", padx=20, pady=(0, 12))

ctk.CTkLabel(
    panel_formulario_alquiler, text="Talla", text_color=texto, anchor="w",
    font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=20)
selector_talla = Selector(
    panel_formulario_alquiler, values=[""], height=40
)
selector_talla.pack(fill="x", padx=20, pady=(5, 10))

ctk.CTkLabel(
    panel_formulario_alquiler, text="Fecha de alquiler", text_color=texto,
    anchor="w", font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=20)
fecha_alquiler = ctk.StringVar()
fila_fecha1 = ctk.CTkFrame(panel_formulario_alquiler, fg_color=blanco)
fila_fecha1.pack(fill="x", padx=20, pady=(5, 10))
caja_fecha1 = CampoTexto(
    fila_fecha1, textvariable=fecha_alquiler, state="readonly", height=44
)
caja_fecha1.pack(side="left", fill="x", expand=True)
Boton(
    fila_fecha1, text="📅", width=44, height=44,
    font=ctk.CTkFont(size=17), command=lambda: abrir_calendario(fecha_alquiler)
).pack(side="left", padx=(6, 0))

ctk.CTkLabel(
    panel_formulario_alquiler, text="Fecha de devolución", text_color=texto,
    anchor="w", font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=20)
fecha_devolucion = ctk.StringVar()
fila_fecha2 = ctk.CTkFrame(panel_formulario_alquiler, fg_color=blanco)
fila_fecha2.pack(fill="x", padx=20, pady=(5, 10))
caja_fecha2 = CampoTexto(
    fila_fecha2, textvariable=fecha_devolucion, state="readonly", height=44
)
caja_fecha2.pack(side="left", fill="x", expand=True)
Boton(
    fila_fecha2, text="📅", width=44, height=44,
    font=ctk.CTkFont(size=17), command=lambda: abrir_calendario(fecha_devolucion)
).pack(side="left", padx=(6, 0))

ctk.CTkLabel(
    panel_formulario_alquiler, text="Método de pago", text_color=texto,
    anchor="w", font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=20)
selector_metodo_alquiler = Selector(
    panel_formulario_alquiler,
    values=["Efectivo al recibir", "Tarjeta de crédito", "Tarjeta débito"],
    height=40
)
selector_metodo_alquiler.set("Efectivo al recibir")
selector_metodo_alquiler.pack(fill="x", padx=20, pady=(5, 4))
formulario_tarjeta_alquiler = ctk.CTkFrame(panel_formulario_alquiler, fg_color=blanco)
campo_titular_alquiler = CampoTexto(
    formulario_tarjeta_alquiler, placeholder_text="Nombre del titular", height=36
)
campo_titular_alquiler.pack(fill="x", padx=10, pady=3)
campo_ultimos_alquiler = CampoTexto(
    formulario_tarjeta_alquiler, placeholder_text="Últimos cuatro dígitos", height=36
)
campo_ultimos_alquiler.pack(fill="x", padx=10, pady=(3, 8))

def actualizar_formulario_tarjeta_alquiler(valor):
    if valor in {"Tarjeta de crédito", "Tarjeta débito"}:
        formulario_tarjeta_alquiler.pack(fill="x", padx=20, pady=(0, 4))
    else:
        formulario_tarjeta_alquiler.pack_forget()

selector_metodo_alquiler.configure(command=actualizar_formulario_tarjeta_alquiler)
actualizar_formulario_tarjeta_alquiler(selector_metodo_alquiler.get())
ctk.CTkLabel(
    panel_formulario_alquiler,
    text="Este sistema no procesa pagos reales.",
    text_color=gris, anchor="w", justify="left", wraplength=560,
    font=fuente_texto(size=12)
).pack(fill="x", padx=20, pady=(0, 8))

mensaje_alquiler = ctk.CTkLabel(
    panel_formulario_alquiler, text="", text_color=rojo,
    wraplength=560, justify="left", anchor="w", font=fuente_texto(size=13)
)
mensaje_alquiler.pack(fill="x", padx=20, pady=(0, 4))
vincular_ajuste_de_texto(
    panel_formulario_alquiler, traje_seleccionado, ancho_minimo=220, margen=40
)
vincular_ajuste_de_texto(
    panel_formulario_alquiler, mensaje_alquiler, ancho_minimo=250, margen=42
)

codigo_elegido = ""

def abrir_formulario_alquiler(codigo, nombre, tallas, precio, fecha_inicio=None, fecha_fin=None):
    global codigo_elegido
    codigo_elegido = codigo

    precio_texto = f"${precio:,}".replace(",", ".")
    traje_seleccionado.configure(text=f"{nombre}\n{precio_texto}")

    lista_tallas = tallas.split(", ")
    selector_talla.configure(values=lista_tallas)
    selector_talla.set("Elija una talla")

    fecha_alquiler.set(
        fecha_inicio or datetime.date.today().strftime("%d/%m/%Y")
    )
    fecha_devolucion.set(
        fecha_fin or (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d/%m/%Y")
    )
    mensaje_alquiler.configure(text="")
    mostrar(pantalla_alquiler)

# Confirmar alquiler

def confirmar_alquiler_interfaz():
    talla = selector_talla.get()
    fecha1 = caja_fecha1.get().strip()
    fecha2 = caja_fecha2.get().strip()

    if talla == "Elija una talla":
        mensaje_alquiler.configure(text="Elija una talla.", text_color=rojo)
        return
    try:
        validar_perfil_completo(sesion_actual.correo)
    except ValueError as problema:
        mensaje_alquiler.configure(
            text=f"{problema} Usa «Mis datos» para completarlos.",
            text_color=rojo
        )
        return
    metodo_alquiler = selector_metodo_alquiler.get()
    if metodo_alquiler in {"Tarjeta de crédito", "Tarjeta débito"}:
        if (not campo_titular_alquiler.get().strip()
                or len(campo_ultimos_alquiler.get().strip()) != 4
                or not campo_ultimos_alquiler.get().strip().isdigit()):
            mensaje_alquiler.configure(
                text="Indica el titular y cuatro dígitos.",
                text_color=rojo
            )
            return

    try:
        datetime.datetime.strptime(fecha1, "%d/%m/%Y")
        datetime.datetime.strptime(fecha2, "%d/%m/%Y")
    except ValueError:
        mensaje_alquiler.configure(text="Formato de fecha inválido. Use dd/mm/aaaa.", text_color=rojo)
        return

    try:
        alquiler = registrar_alquiler(
            sesion_actual.correo, codigo_elegido, talla, fecha1, fecha2,
            metodo_alquiler
        )
    except ValueError as problema:
        mostrar_aviso(str(problema), rojo)
        mensaje_alquiler.configure(text=str(problema), text_color=rojo)
        return

    mensaje_alquiler.configure(
        text=f"¡Alquiler registrado exitosamente!\n{alquiler['Nombre']} · Talla {alquiler['Talla']}\nDel {alquiler['FechaAlquiler']} al {alquiler['FechaProgramada']}",
        text_color= verde)
    mostrar_aviso(f"🤵  ¡Alquiler registrado!\n{alquiler['Nombre']} · Talla {alquiler['Talla']}")

bonton_confirmar = Boton(
    panel_formulario_alquiler, text="Confirmar alquiler",
    command=confirmar_alquiler_interfaz, height=44,
    font=fuente_texto(size=15, weight="bold")
)
bonton_confirmar.pack(fill="x", padx=20, pady=(6, 14))

#Mis alquileres
pantalla_alquileres = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)

boton_volver_menu2 = Boton(pantalla_alquileres, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold"))
boton_volver_menu2.pack(fill="x", padx=16, pady=(16, 0))

titulo_alquileres = ctk.CTkLabel(pantalla_alquileres, text="Mis alquileres", text_color=texto, font=fuente_titulo(size=26, weight="bold"), anchor="w")
titulo_alquileres.pack(fill="x", padx=24, pady=(4, 10))

mensaje_devolucion = ctk.CTkLabel(pantalla_alquileres, text="", text_color=verde, wraplength=372, justify="left", anchor="w", font=fuente_texto(size=13))
mensaje_devolucion.pack(fill="x", padx=24)


lista_alquileres = ctk.CTkScrollableFrame(pantalla_alquileres, fg_color=fondo)
lista_alquileres._limitar_columnas_a_elementos = True
lista_alquileres.pack(fill="both", expand=True, padx=12, pady=(0,16))

def mostrar_alquileres():
    mensaje_devolucion.configure(text="")
    for tarjeta in lista_alquileres.winfo_children():
        tarjeta.destroy()

    try:
        alquileres = obtener_alquileres_usuario(sesion_actual.correo)
    except (OSError, UnicodeError) as problema:
        mensaje_devolucion.configure(
            text=f"No se pudieron cargar los alquileres: {problema}",
            text_color=rojo
        )
        mostrar(pantalla_alquileres)
        return

    if len (alquileres)== 0:
        vacio = ctk.CTkLabel(
            lista_alquileres, text="Todavía no tienes alquileres.",
            text_color=gris, font=fuente_texto(size=14)
        )
        vacio._ocupar_columnas_adaptables = True
        vacio.grid(row=0, column=0, sticky="ew", padx=12, pady=20)

    for alquiler in alquileres:
        tarjeta = crear_tarjeta(lista_alquileres)
        tarjeta.grid(row=len(lista_alquileres.winfo_children()), column=0, sticky="nsew", padx=8, pady=6)
        contenido = ctk.CTkFrame(tarjeta, fg_color=blanco)
        contenido.pack(fill="x", padx=12, pady=(12, 8))
        crear_miniatura_producto(
            contenido, str(alquiler["Codigo"]), size=(78, 104), icono="🤵"
        ).pack(side="left", padx=(0, 12))
        informacion = ctk.CTkFrame(contenido, fg_color=blanco)
        informacion.pack(side="left", fill="both", expand=True)
        nombre_alquiler = ctk.CTkLabel(
            informacion, text=alquiler["Nombre"], text_color=texto,
            anchor="w", justify="left", wraplength=360,
            font=fuente_texto(size=16, weight="bold")
        )
        nombre_alquiler.pack(fill="x", pady=(2, 4))
        def ajustar_nombre_alquiler(evento, objetivo=informacion, etiqueta=nombre_alquiler):
            if evento.widget is objetivo:
                etiqueta.configure(wraplength=max(150, objetivo.winfo_width() - 8))
        informacion.bind("<Configure>", ajustar_nombre_alquiler, add="+")
        ctk.CTkLabel(
            informacion, text=f"Talla: {alquiler['Talla']}", text_color=gris,
            anchor="w", font=fuente_texto(size=13)
        ).pack(fill="x", pady=(0, 3))
        ctk.CTkLabel(
            informacion,
            text=f"Del {alquiler['FechaAlquiler']} al {alquiler['FechaProgramada']}",
            text_color=champagne_texto, anchor="w", justify="left",
            wraplength=360, font=fuente_texto(size=13)
        ).pack(fill="x")

        if alquiler["Estado"] == "Activo":
            color_estado= verde
            fondo_estado = "#E8F1E9"
        else:
            color_estado = gris
            fondo_estado = fondo
        fila_estado = ctk.CTkFrame(tarjeta, fg_color=blanco)
        fila_estado.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(
            fila_estado, text=alquiler["Estado"], text_color=color_estado,
            fg_color=fondo_estado, corner_radius=8,
            font=fuente_texto(size=12, weight="bold")
        ).pack(side="left")
        if alquiler["Estado"] == "Activo":
            Boton(
                fila_estado, text="Devolver traje", height=36,
                variant="principal", font=fuente_texto(size=13, weight="bold"),
                command=lambda indice_i=alquiler["IndiceArchivo"]: devolver(indice_i)
            ).pack(side="right")
        ctk.CTkLabel(
            tarjeta,
            text=f"Método de pago: {alquiler.get('MetodoPago', 'Método no registrado')}\n"
                 f"Estado del pago: {texto_estado_pago(alquiler.get('EstadoPago', 'Pago anterior no registrado'))}",
            text_color=champagne_texto, anchor="w", justify="left",
            font=fuente_texto(size=12, weight="bold")
        ).pack(fill="x", padx=14, pady=(2, 10))

    _organizar_tarjetas_adaptables(
        lista_alquileres, ancho_minimo=520, columnas_maximas=2, separacion=14
    )
    mostrar(pantalla_alquileres)

#Devolver traje
def devolver(indice):
    if not preguntar_confirmacion_cliente(
        "Confirmar devolución", "¿Seguro que quieres devolver este traje?"
    ):
        return
    try:
        traje= devolver_alquiler(sesion_actual.correo, indice)
    except ValueError as problema:
        mensaje_devolucion.configure(text=str(problema), text_color=rojo)
        mostrar_aviso(str(problema), rojo)
        return

    mostrar_alquileres()
    mensaje_devolucion.configure(text=f"¡{traje['Nombre']} devuelto exitosamente el {traje['FechaReal']}!", text_color=verde)
    mostrar_aviso(f"↩️  ¡Traje devuelto!\n{traje['Nombre']}")
# Crear cuenta
pantalla_registro = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)
contenedor_registro = ctk.CTkFrame(pantalla_registro, fg_color=fondo, corner_radius=0)
if imagen_logo_marca is not None:
    espacio_logo_registro = agregar_espacio_logo_acceso(contenedor_registro)
    espacio_logo_registro.pack_configure(pady=(0, 4))
panel_registro = crear_tarjeta(contenedor_registro)
panel_registro.pack(fill="x")
ctk.CTkLabel(
    panel_registro, text="Crear cuenta", text_color=texto,
    font=fuente_titulo(size=25, weight="bold"), anchor="w"
).pack(fill="x", padx=20, pady=(10, 7))
ctk.CTkLabel(
    panel_registro, text="Correo electrónico", text_color=texto,
    font=fuente_texto(size=13, weight="bold"), anchor="w"
).pack(fill="x", padx=20)
registro_correo = CampoTexto(
    panel_registro, placeholder_text="tunombre@gmail.com", height=44
)
registro_correo.pack(fill="x", padx=20, pady=(3, 6))
ctk.CTkLabel(
    panel_registro, text="Contraseña", text_color=texto,
    font=fuente_texto(size=13, weight="bold"), anchor="w"
).pack(fill="x", padx=20)
contenedor_clave_registro, registro_clave = crear_campo_clave(
    panel_registro,
    placeholder_text="Mínimo 8, con mayúscula, minúscula y número",
    height=44,
)
contenedor_clave_registro.pack(fill="x", padx=20, pady=(3, 6))
ctk.CTkLabel(
    panel_registro, text="Repite la contraseña", text_color=texto,
    font=fuente_texto(size=13, weight="bold"), anchor="w"
).pack(fill="x", padx=20)
contenedor_clave_registro2, registro_clave2 = crear_campo_clave(
    panel_registro, placeholder_text="********", height=44
)
contenedor_clave_registro2.pack(fill="x", padx=20, pady=(3, 5))
mensaje_registro = ctk.CTkLabel(
    panel_registro, text="", text_color=rojo, font=fuente_texto(size=13),
    wraplength=400, justify="left", anchor="w"
)
mensaje_registro.pack(fill="x", padx=20, pady=(0, 4))
vincular_ajuste_de_texto(panel_registro, mensaje_registro, ancho_minimo=240, margen=40)

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

Boton(
    panel_registro, text="Crear cuenta", command=crear_cuenta_interfaz,
    height=44, font=fuente_texto(size=15, weight="bold")
).pack(fill="x", padx=20, pady=(2, 2))
Boton(
    panel_registro, text="¿Ya tienes cuenta? Inicia sesión",
    command=lambda: mostrar(pantalla_login), variant="secundario",
    font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=20, pady=(2, 6))

for columna in range(3):
    pantalla_registro.grid_columnconfigure(
        columna, weight=1 if columna != 1 else 0
    )
pantalla_registro.grid_rowconfigure(0, weight=1)
contenedor_registro.grid_columnconfigure(0, weight=1)
contenedor_registro.grid(row=0, column=1, sticky="ew")

def _ajustar_ancho_registro(evento=None):
    if evento is not None and evento.widget not in (pantalla_registro, ventana):
        return
    ancho_area = pantalla_registro.winfo_width()
    if ancho_area <= 1:
        ancho_area = ventana.winfo_width()
    ancho = max(300, min(480, ancho_area - 32))
    pantalla_registro.grid_columnconfigure(1, minsize=ancho)
    contenedor_registro.configure(width=ancho)

pantalla_registro.bind("<Configure>", _ajustar_ancho_registro, add="+")
ventana.bind("<Configure>", _ajustar_ancho_registro, add="+")
pantalla_registro.after_idle(_ajustar_ancho_registro)

def ir_a_registro():
    registro_correo.delete(0, "end")
    registro_clave.delete(0, "end")
    registro_clave2.delete(0, "end")
    mensaje_registro.configure(text="")
    mostrar(pantalla_registro)

Boton(
    panel_login, text="¿Primera vez aquí? Crea una cuenta",
    command=ir_a_registro, variant="secundario",
    font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=20, pady=(3, 12))

#MIS DATOS

pantalla_datos = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)

Boton(pantalla_datos, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_datos, text="Mis datos", text_color=texto, anchor="w", font=fuente_titulo(size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

formulario = ctk.CTkScrollableFrame(pantalla_datos, fg_color=fondo)
formulario.pack(fill="both", expand=True, padx=8, pady=(0, 16))
campos_datos = ctk.CTkFrame(formulario, fg_color=fondo)
campos_datos.pack(fill="x", padx=8, pady=(6, 0))

def crear_campo(etiqueta, ejemplo):
    tarjeta_campo = crear_tarjeta(campos_datos)
    tarjeta_campo.grid(
        row=len(campos_datos.winfo_children()), column=0,
        sticky="nsew", padx=6, pady=6
    )
    ctk.CTkLabel(
        tarjeta_campo, text=etiqueta, text_color=texto, anchor="w",
        font=fuente_texto(size=13, weight="bold")
    ).pack(fill="x", padx=12, pady=(10, 2))
    caja = CampoTexto(
        tarjeta_campo, placeholder_text=ejemplo, height=42,
        corner_radius=10, fg_color=blanco, border_color=borde,
        text_color=texto
    )
    caja.pack(fill="x", padx=12, pady=(4, 12))
    return caja

caja_nombre = crear_campo("Nombre", "Ej: Isabella")
caja_apellidos = crear_campo("Apellidos", "Ej: Caro López")
caja_telefono = crear_campo("Teléfono", "10 dígitos")

tarjeta_tipo_documento = crear_tarjeta(campos_datos)
tarjeta_tipo_documento.grid(
    row=len(campos_datos.winfo_children()), column=0,
    sticky="nsew", padx=6, pady=6
)
ctk.CTkLabel(
    tarjeta_tipo_documento, text="Tipo de documento", text_color=texto,
    anchor="w", font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=12, pady=(10, 2))
selector_documento = Selector(
    tarjeta_tipo_documento, values=["CC", "CE", "NIT"], height=42,
    corner_radius=10, fg_color=blanco, button_color=champagne,
    button_hover_color=champagne_oscuro, text_color=texto,
    dropdown_fg_color=blanco, dropdown_text_color=texto
)
selector_documento.pack(fill="x", padx=12, pady=(4, 12))

caja_documento = crear_campo("Número de documento", "Solo números")
caja_direccion = crear_campo("Dirección", "Ej: Calle 5 # 10-20")
caja_postal = crear_campo("Código postal", "6 dígitos")
caja_direccion.master._ocupar_columnas_adaptables = True
_organizar_tarjetas_adaptables(
    campos_datos, ancho_minimo=360, columnas_maximas=2, separacion=12
)

mensaje_datos = ctk.CTkLabel(formulario, text="", text_color=rojo, wraplength=340, justify="left", anchor="w", font=fuente_texto(size=13))
mensaje_datos.pack(fill="x", padx=16)


def llenar_campo(caja, valor):
    caja.delete(0, "end")
    if valor:
        caja.insert(0, valor)

def mostrar_datos_personales():
    try:
        datos = leer_datos_personales(sesion_actual.correo)
    except (OSError, UnicodeError) as problema:
        mensaje_datos.configure(
            text=f"No se pudieron cargar tus datos: {problema}",
            text_color=rojo
        )
        mostrar(pantalla_datos)
        return
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

Boton(formulario, text="Guardar datos", command=guardar_datos_interfaz, height=46, corner_radius=10, fg_color=texto, hover_color="#333333", text_color=blanco, font=fuente_texto(size=15, weight="bold")).pack(fill="x", padx=16, pady=(8, 12))

#BUSCAR ROPA
pantalla_buscar = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)

Boton(pantalla_buscar, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_buscar, text="Buscar ropa", text_color=texto, anchor="w", font=fuente_titulo(size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

filtros = ctk.CTkFrame(pantalla_buscar, fg_color=fondo)
filtros.pack(fill="x", padx=16, pady=(0, 8))
selector_seccion = Selector(
    filtros, values=["Todas", "Mujer", "Hombre", "Unisex"],
    command=lambda valor: mostrar_productos_ropa(), width=170, height=38
)
selector_tipo = Selector(
    filtros, values=["Todos"], command=lambda valor: mostrar_productos_ropa(),
    width=170, height=38
)
caja_busqueda = CampoTexto(
    filtros, placeholder_text="Buscar nombre o código", width=170, height=38
)
caja_busqueda.bind("<KeyRelease>", lambda evento: mostrar_productos_ropa())
selector_disponibilidad = Selector(
    filtros, values=["Todas", "Disponible", "Agotado"],
    command=lambda valor: mostrar_productos_ropa(), width=130, height=38
)
_distribuir_controles_adaptable(
    filtros, (selector_seccion, selector_tipo, caja_busqueda, selector_disponibilidad)
)

mensaje_buscar = ctk.CTkLabel(
    pantalla_buscar, text="", text_color=rojo, wraplength=372,
    justify="left", anchor="w", font=fuente_texto(size=13)
)
mensaje_buscar.pack(fill="x", padx=24)

lista_ropa = ctk.CTkScrollableFrame(pantalla_buscar, fg_color=fondo)
lista_ropa.pack(fill="both", expand=True, padx=12, pady=(0, 12))

catalogo = []

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
    caja_busqueda.configure(placeholder_text="Buscar nombre o código")
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
    busqueda = caja_busqueda.get().strip().lower()
    disponibilidad = selector_disponibilidad.get()
    productos = [
        producto for producto in productos
        if (busqueda in producto["Nombre"].lower() or busqueda in producto["Codigo"].lower())
        and (disponibilidad == "Todas" or producto["Disponibilidad"] == disponibilidad)
    ]

    if not productos:
        vacio = ctk.CTkLabel(
            lista_ropa, text="No hay prendas con esos filtros.",
            text_color=gris, font=fuente_texto(size=14)
        )
        vacio._ocupar_columnas_adaptables = True
        vacio.grid(row=0, column=0, sticky="ew", padx=12, pady=12)

    for producto in productos:
        tarjeta = crear_tarjeta(lista_ropa)
        tarjeta.grid(row=len(lista_ropa.winfo_children()), column=0, sticky="nsew", padx=8, pady=8)
        mostrar_foto_producto(
            tarjeta, producto["Codigo"],
            iconos_ropa.get(producto["Tipo"], "🛍️"), alto_maximo=340
        )

        nombre_producto = ctk.CTkLabel(
            tarjeta, text=producto["Nombre"], text_color=texto, anchor="w",
            justify="left", wraplength=280,
            font=fuente_titulo(size=18, weight="bold")
        )
        nombre_producto.pack(fill="x", padx=16, pady=(8, 1))
        def ajustar_nombre(evento, objetivo=tarjeta, etiqueta=nombre_producto):
            if evento.widget is objetivo:
                etiqueta.configure(wraplength=max(180, objetivo.winfo_width() - 36))
        tarjeta.bind("<Configure>", ajustar_nombre, add="+")
        ctk.CTkLabel(
            tarjeta, text=f"${producto['Precio']:,.0f}".replace(",", "."),
            text_color=champagne_texto, anchor="w",
            font=fuente_titulo(size=19, weight="bold")
        ).pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(
            tarjeta,
            text=f"{producto['Seccion']} · {producto['Tipo']} · {producto['Codigo']}",
            text_color=gris, anchor="w", font=fuente_texto(size=12)
        ).pack(fill="x", padx=16)
        descripcion = ctk.CTkLabel(
            tarjeta, text=producto["Descripcion"], text_color=texto,
            anchor="w", justify="left", wraplength=280,
            font=fuente_texto(size=13)
        )
        descripcion.pack(fill="x", padx=16, pady=(5, 5))
        vincular_ajuste_de_texto(
            tarjeta, descripcion, ancho_minimo=180, margen=36
        )

        texto_tallas = "   ".join(
            talla["Talla"] for talla in producto["Tallas"] if talla["Cantidad"] > 0
        )
        ctk.CTkLabel(
            tarjeta, text=f"Tallas  {texto_tallas or 'Sin tallas disponibles'}",
            text_color=texto, anchor="w", font=fuente_texto(size=14, weight="bold")
        ).pack(fill="x", padx=16, pady=(0, 7))
        disponible = producto["Disponibilidad"] == "Disponible"
        ctk.CTkLabel(
            tarjeta, text=producto["Disponibilidad"],
            text_color=verde if disponible else rojo,
            fg_color="#E8F1E9" if disponible else "#F5E8E5",
            corner_radius=8, font=fuente_texto(size=12, weight="bold")
        ).pack(anchor="w", padx=16, pady=(0, 10))

        tallas_disponibles = [
            talla["Talla"] for talla in producto["Tallas"] if talla["Cantidad"] > 0
        ]
        pie_acciones = ctk.CTkFrame(tarjeta, fg_color=blanco)
        pie_acciones.pack(side="bottom", fill="x", padx=12, pady=(4, 10))
        if tallas_disponibles:
            fila_acciones = ctk.CTkFrame(pie_acciones, fg_color=blanco)
            fila_acciones.pack(fill="x", pady=(0, 2))
            selector = Selector(
                fila_acciones, values=tallas_disponibles,
                width=86, height=36, fg_color=fondo
            )
            selector.pack(side="left", padx=(0, 8))
            Boton(
                fila_acciones, text="Agregar al carrito", height=36,
                fg_color=texto, hover_color="#333333", text_color=blanco,
                font=fuente_texto(size=13, weight="bold"),
                command=lambda caracter_c=producto["Codigo"], elemento_s=selector:
                    agregar_producto_carrito(caracter_c, elemento_s.get())
            ).pack(side="left", fill="x", expand=True)
        Boton(
            pie_acciones, text="♡  Agregar a favoritos", variant="secundario", height=32,
            fg_color="transparent", hover_color=borde,
            text_color=champagne_texto, font=fuente_texto(size=13, weight="bold"),
            command=lambda caracter_c=producto["Codigo"]:
                agregar_producto_favorito(caracter_c)
        ).pack(anchor="w", pady=(2, 0))

    _organizar_tarjetas_adaptables(lista_ropa, ancho_minimo=270, columnas_maximas=4)

# AVISO GRANDE QUE APARECE Y SE VA SOLO
aviso_flotante = None


def mostrar_aviso(mensaje, color=verde):
    global aviso_flotante
    if aviso_flotante is not None and aviso_flotante.winfo_exists():
        aviso_flotante.destroy()

    aviso_flotante = ctk.CTkFrame(ventana, fg_color=color, corner_radius=14)
    ctk.CTkLabel(aviso_flotante, text=mensaje, text_color=blanco, justify="center", wraplength=340, font=fuente_texto(size=17, weight="bold")).pack(padx=26, pady=16)
    aviso_flotante.place(relx=0.5, rely=0.88, anchor="center")   # centrado, abajo
    aviso_flotante.lift()                                         # encima de todo

    aviso = aviso_flotante
    ventana.after(2500, lambda: aviso.destroy() if aviso.winfo_exists() else None)


#AGREGAR AL CARRITO

def agregar_producto_carrito(codigo, talla):
    try:
        cantidad = agregar_al_carrito(sesion_actual.correo, codigo, talla, 1, catalogo)
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema), text_color=rojo)
        mostrar_aviso(str(problema), rojo)
        return

    mensaje_buscar.configure(text=f"¡Agregado al carrito! (talla {talla}, llevas {cantidad})", text_color=verde)
    mostrar_aviso(f"🛒  ¡Agregado al carrito!\nTalla {talla} · llevas {cantidad}")

def texto_estado_pago(estado):
    if estado == "No procesado; demostración académica":
        return "No procesado"
    return estado


def texto_indicador(nombre):
    if nombre == "Ventas simuladas":
        return "Valor de pedidos registrados"
    return nombre


def formatear_pesos(valor):
    return f"${valor:,.0f}".replace(",", ".")

#VER MI CARRITO

pantalla_carrito = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)

Boton(pantalla_carrito, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_carrito, text="Mi carrito", text_color=texto, anchor="w", font=fuente_titulo(size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

mensaje_carrito = ctk.CTkLabel(pantalla_carrito, text="", text_color=rojo, wraplength=372, justify="left", anchor="w", font=fuente_texto(size=13))
mensaje_carrito.pack(fill="x", padx=24)

lista_carrito = ctk.CTkScrollableFrame(pantalla_carrito, fg_color=fondo)
lista_carrito._limitar_columnas_a_elementos = True
lista_carrito.pack(fill="both", expand=True, padx=16, pady=(0, 8))

resumen_carrito = crear_tarjeta(pantalla_carrito)
resumen_carrito.pack(fill="x", padx=16, pady=(0, 10))
total_carrito = ctk.CTkLabel(
    resumen_carrito, text="", text_color=champagne_texto, anchor="e",
    font=fuente_titulo(size=20, weight="bold")
)
total_carrito.pack(fill="x", padx=16, pady=(12, 8))

ctk.CTkLabel(
    resumen_carrito,
    text="Método de pago",
    text_color=texto,
    anchor="w",
    font=fuente_texto(size=13, weight="bold"),
).pack(fill="x", padx=14, pady=(0, 4))
selector_metodo_pago = Selector(
    resumen_carrito,
    values=["Efectivo al recibir", "Tarjeta de crédito", "Tarjeta débito"],
    height=40,
)
selector_metodo_pago.set("Efectivo al recibir")
selector_metodo_pago.pack(fill="x", padx=14, pady=(0, 6))
aviso_metodo_pago = ctk.CTkLabel(
    resumen_carrito,
    text="Efectivo al recibir: Pendiente. Este sistema no procesa pagos reales.",
    text_color=gris,
    anchor="w",
    justify="left",
    wraplength=500,
    font=fuente_texto(size=12),
)
aviso_metodo_pago.pack(fill="x", padx=14, pady=(0, 8))

def actualizar_aviso_metodo_pago(valor):
    if valor in {"Tarjeta de crédito", "Tarjeta débito"}:
        aviso_metodo_pago.configure(
            text="Este sistema no procesa pagos reales.",
            text_color=champagne_texto,
        )
    else:
        aviso_metodo_pago.configure(
            text="Efectivo al recibir: Pendiente. Este sistema no procesa pagos reales.",
            text_color=gris,
        )

selector_metodo_pago.configure(command=actualizar_aviso_metodo_pago)

formulario_tarjeta = ctk.CTkFrame(resumen_carrito, fg_color=blanco)
ctk.CTkLabel(
    formulario_tarjeta, text="Datos de tarjeta (no se guardan)",
    text_color=gris, anchor="w", font=fuente_texto(size=12, weight="bold")
).pack(fill="x", padx=10, pady=(4, 2))
campo_titular_tarjeta = CampoTexto(
    formulario_tarjeta, placeholder_text="Nombre del titular", height=36
)
campo_titular_tarjeta.pack(fill="x", padx=10, pady=3)
campo_ultimos_tarjeta = CampoTexto(
    formulario_tarjeta, placeholder_text="Últimos cuatro dígitos", height=36
)
campo_ultimos_tarjeta.pack(fill="x", padx=10, pady=(3, 8))

def actualizar_formulario_tarjeta(valor):
    if valor in {"Tarjeta de crédito", "Tarjeta débito"}:
        formulario_tarjeta.pack(fill="x", padx=4, pady=(0, 4))
    else:
        formulario_tarjeta.pack_forget()

selector_metodo_pago.configure(command=lambda valor: (
    actualizar_aviso_metodo_pago(valor), actualizar_formulario_tarjeta(valor)
))
actualizar_formulario_tarjeta(selector_metodo_pago.get())


def mostrar_carrito():
    mensaje_carrito.configure(text="")
    for tarjeta in lista_carrito.winfo_children():
        tarjeta.destroy()

    try:
        detalles = obtener_detalles_carrito(sesion_actual.correo)
    except (OSError, ValueError, ImportError, UnicodeError) as problema:
        mensaje_carrito.configure(
            text=f"No se pudo cargar el carrito: {problema}",
            text_color=rojo
        )
        mostrar(pantalla_carrito)
        return
    total=0

    if len(detalles) == 0:
        vacio = ctk.CTkLabel(
            lista_carrito, text="Tu carrito está vacío.", text_color=gris,
            font=fuente_texto(size=14)
        )
        vacio._ocupar_columnas_adaptables = True
        vacio.grid(row=0, column=0, sticky="ew", padx=12, pady=20)

    for detalle in detalles:
        tarjeta = crear_tarjeta(lista_carrito)
        tarjeta.grid(row=len(lista_carrito.winfo_children()), column=0, sticky="nsew", padx=8, pady=6)
        contenido = ctk.CTkFrame(tarjeta, fg_color=blanco)
        contenido.pack(fill="x", padx=12, pady=(12, 4))
        crear_miniatura_producto(
            contenido, str(detalle["Codigo"]), size=(78, 104)
        ).pack(side="left", padx=(0, 12))
        informacion = ctk.CTkFrame(contenido, fg_color=blanco)
        informacion.pack(side="left", fill="both", expand=True)

        nombre_item = ctk.CTkLabel(
            informacion, text=detalle["Nombre"], text_color=texto,
            anchor="w", justify="left", wraplength=280,
            font=fuente_texto(size=16, weight="bold")
        )
        nombre_item.pack(fill="x", pady=(2, 3))
        def ajustar_nombre_item(evento, objetivo=informacion, etiqueta=nombre_item):
            if evento.widget is objetivo:
                etiqueta.configure(wraplength=max(150, objetivo.winfo_width() - 8))
        informacion.bind("<Configure>", ajustar_nombre_item, add="+")
        ctk.CTkLabel(
            informacion, text=f"Talla: {detalle['Talla']} · Código {detalle['Codigo']}",
            text_color=gris, anchor="w", font=fuente_texto(size=12)
        ).pack(fill="x")

        if detalle ["Subtotal"] is None:
            subtotal_texto = "Precio no disponible"
        else:
            subtotal_texto = f"{formatear_pesos(detalle['Precio'])} c/u · Subtotal {formatear_pesos(detalle['Subtotal'])}"
            total = total + detalle["Subtotal"]
        ctk.CTkLabel(
            informacion, text=subtotal_texto, text_color=champagne_texto,
            anchor="w", justify="left", wraplength=280,
            font=fuente_texto(size=13, weight="bold")
        ).pack(fill="x", pady=(5, 0))

        if detalle["Aviso"]!= "":
            ctk.CTkLabel(
                informacion, text=detalle["Aviso"], text_color=rojo,
                wraplength=280, justify="left", anchor="w",
                font=fuente_texto(size=12)
            ).pack(fill="x", pady=(4, 0))

        fila = ctk.CTkFrame(tarjeta, fg_color=blanco)
        fila.pack(fill="x", padx=12, pady=(4, 12))

        Boton(fila, text="−", width=36, height=32, corner_radius=8, fg_color=fondo, hover_color=borde, text_color=champagne_texto, font=fuente_texto(size=16, weight="bold"), command=lambda caracter_c=detalle["Codigo"], talla_t=detalle["Talla"], numero_n=detalle["Cantidad"] - 1: cambiar_cantidad_carrito(caracter_c, talla_t, numero_n)).pack(side="left")
        ctk.CTkLabel(fila, text=str(detalle["Cantidad"]), width=36, text_color=texto, font=fuente_texto(size=15, weight="bold")).pack(side="left")
        Boton(fila, text="+", width=36, height=32, corner_radius=8, fg_color=fondo, hover_color=borde, text_color=champagne_texto, font=fuente_texto(size=16, weight="bold"), command=lambda caracter_c=detalle["Codigo"], talla_t=detalle["Talla"], numero_n=detalle["Cantidad"] + 1: cambiar_cantidad_carrito(caracter_c, talla_t, numero_n)).pack(side="left")

        Boton(fila, text="Quitar", variant="destructivo", width=70, height=32, font=fuente_texto(size=13, weight="bold"), command=lambda caracter_c=detalle["Codigo"], talla_t=detalle["Talla"]: quitar(caracter_c, talla_t)).pack(side="right")

    total_carrito.configure(text=f"Total: {formatear_pesos(total)}")
    _organizar_tarjetas_adaptables(
        lista_carrito, ancho_minimo=520, columnas_maximas=2, separacion=14
    )
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

    try:
        validar_perfil_completo(sesion_actual.correo)
    except ValueError as problema:
        mensaje_carrito.configure(
            text=f"{problema} Usa «Mis datos» para completarlos.",
            text_color=rojo
        )
        mostrar_aviso("Completa «Mis datos» antes de comprar.", rojo)
        return
    metodo_pago = selector_metodo_pago.get()
    if metodo_pago in {"Tarjeta de crédito", "Tarjeta débito"}:
        titular = campo_titular_tarjeta.get().strip()
        ultimos = campo_ultimos_tarjeta.get().strip()
        if not titular or len(ultimos) != 4 or not ultimos.isdigit():
            mensaje_carrito.configure(
                text="Indica el titular y cuatro dígitos.",
                text_color=rojo
            )
            return
    descripcion_pago = (
        "Pago pendiente al recibir."
        if metodo_pago == "Efectivo al recibir"
        else "Estado del pago: No procesado. Este sistema no procesa pagos reales."
    )
    respuesta = preguntar_confirmacion_cliente(
        "Confirmar compra",
        f"¿Desea confirmar la compra por {formatear_pesos(total)}?\n"
        f"Método: {metodo_pago}\n{descripcion_pago}"
    )

    resultado = confirmar_compra(
        sesion_actual.correo,
        respuesta,
        metodo_pago=metodo_pago,
    )

    if resultado["ok"]:
        mostrar_carrito()
        mensaje_carrito.configure(text=f"¡Compra confirmada! Pedido {resultado['pedido']}", text_color=verde)
        mostrar_aviso(f"🛍️  ¡Compra confirmada!\nPedido {resultado['pedido']}")
    else:
        mensaje_carrito.configure(text=resultado["message"], text_color=rojo)
        mostrar_aviso(resultado["message"], rojo)

Boton(
    resumen_carrito, text="Confirmar compra", command=comprar, height=44,
    variant="principal", font=fuente_texto(size=15, weight="bold")
).pack(fill="x", padx=14, pady=(0, 14))


#MIS COMPRAS
pantalla_compras = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)

Boton(pantalla_compras, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_compras, text="Mis compras", text_color=texto, anchor="w", font=fuente_titulo(size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

lista_compras = ctk.CTkScrollableFrame(pantalla_compras, fg_color=fondo)
lista_compras._limitar_columnas_a_elementos = True
lista_compras.pack(fill="both", expand=True, padx=16, pady=(0, 16))

def mostrar_compras():
    for tarjeta in lista_compras.winfo_children():
        tarjeta.destroy()

    try:
        pedidos = listar_compras(sesion_actual.correo)
    except (OSError, UnicodeError) as problema:
        mensaje = ctk.CTkLabel(
            lista_compras,
            text=f"No se pudieron cargar las compras: {problema}",
            text_color=rojo, wraplength=500, justify="left"
        )
        mensaje.grid(row=0, column=0, sticky="ew", padx=12, pady=20)
        mostrar(pantalla_compras)
        return

    if len(pedidos) == 0:
        vacio = ctk.CTkLabel(
            lista_compras, text="Aún no tienes compras registradas.",
            text_color=gris, font=fuente_texto(size=14)
        )
        vacio._ocupar_columnas_adaptables = True
        vacio.grid(row=0, column=0, sticky="ew", padx=12, pady=20)

    for pedido in pedidos:
        tarjeta = crear_tarjeta(lista_compras)
        tarjeta.grid(row=len(lista_compras.winfo_children()), column=0, sticky="nsew", padx=8, pady=6)

        encabezado_pedido = ctk.CTkFrame(tarjeta, fg_color=blanco)
        encabezado_pedido.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(
            encabezado_pedido, text=pedido["Fecha"], text_color=texto,
            anchor="w", font=fuente_titulo(size=16, weight="bold")
        ).pack(fill="x")
        ctk.CTkLabel(
            encabezado_pedido, text=pedido["Pedido"],
            text_color=gris, anchor="e", justify="right",
            font=fuente_texto(size=11)
        ).pack(fill="x")

        ctk.CTkLabel(
            tarjeta,
            text=f"Estado del pedido: {pedido.get('Estado', 'Confirmada')}",
            text_color=verde,
            anchor="w",
            font=fuente_texto(size=12, weight="bold"),
        ).pack(fill="x", padx=14, pady=(4, 1))
        ctk.CTkLabel(
            tarjeta,
            text=f"Método de pago: {pedido.get('MetodoPago', 'Método no registrado')}",
            text_color=texto,
            anchor="w",
            font=fuente_texto(size=12),
        ).pack(fill="x", padx=14, pady=1)
        ctk.CTkLabel(
            tarjeta,
            text=f"Estado del pago: {texto_estado_pago(pedido.get('EstadoPago', 'Pago anterior no registrado'))}",
            text_color=champagne_texto,
            anchor="w",
            font=fuente_texto(size=12, weight="bold"),
        ).pack(fill="x", padx=14, pady=(1, 4))

        for articulo in pedido["Articulos"]:
            linea_articulo = ctk.CTkLabel(
                tarjeta,
                text=f"{articulo['Nombre']} · Talla {articulo['Talla']} · x{articulo['Cantidad']}  —  {formatear_pesos(articulo['Subtotal'])}",
                text_color=texto, anchor="w", justify="left", wraplength=500,
                font=fuente_texto(size=13)
            )
            linea_articulo.pack(fill="x", padx=14, pady=3)
            vincular_ajuste_de_texto(tarjeta, linea_articulo, ancho_minimo=220, margen=28)

        ctk.CTkLabel(
            tarjeta, text=f"Total: {formatear_pesos(pedido['Total'])}",
            text_color=champagne_texto, anchor="e",
            font=fuente_titulo(size=17, weight="bold")
        ).pack(fill="x", padx=14, pady=(8, 14))

    _organizar_tarjetas_adaptables(
        lista_compras, ancho_minimo=520, columnas_maximas=2, separacion=14
    )
    mostrar(pantalla_compras)

#FAVORITOS

def agregar_producto_favorito(codigo):
    try:
        agregar_favorito(sesion_actual.correo, codigo)
    except ValueError as problema:
        mensaje_buscar.configure(text=str(problema), text_color=rojo)
        mostrar_aviso(str(problema), rojo)
        return
    mensaje_buscar.configure(text="¡Agregado a favoritos! ♡", text_color=verde)
    mostrar_aviso("♡  ¡Agregado a favoritos!")

pantalla_favoritos = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)

Boton(pantalla_favoritos, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold")).pack(fill="x", padx=16, pady=(16, 0))
ctk.CTkLabel(pantalla_favoritos, text="Mis favoritos", text_color=texto, anchor="w", font=fuente_titulo(size=26, weight="bold")).pack(fill="x", padx=24, pady=(4, 10))

lista_favoritos = ctk.CTkScrollableFrame(pantalla_favoritos, fg_color=fondo)
lista_favoritos._limitar_columnas_a_elementos = True
lista_favoritos.pack(fill="both", expand=True, padx=16, pady=(0, 16))


def mostrar_favoritos():
    for tarjeta in lista_favoritos.winfo_children():
        tarjeta.destroy()

    try:
        favoritos = listar_favoritos(sesion_actual.correo)
    except (OSError, ValueError, ImportError, UnicodeError) as problema:
        mensaje = ctk.CTkLabel(
            lista_favoritos,
            text=f"No se pudieron cargar los favoritos: {problema}",
            text_color=rojo, wraplength=500, justify="left"
        )
        mensaje.grid(row=0, column=0, sticky="ew", padx=12, pady=20)
        mostrar(pantalla_favoritos)
        return

    if len(favoritos) == 0:
        vacio = ctk.CTkLabel(
            lista_favoritos, text="No tienes productos favoritos.",
            text_color=gris, font=fuente_texto(size=14)
        )
        vacio._ocupar_columnas_adaptables = True
        vacio.grid(row=0, column=0, sticky="ew", padx=12, pady=20)

    for favorito in favoritos:
        tarjeta = crear_tarjeta(lista_favoritos)
        tarjeta.grid(row=len(lista_favoritos.winfo_children()), column=0, sticky="nsew", padx=8, pady=6)
        contenido = ctk.CTkFrame(tarjeta, fg_color=blanco)
        contenido.pack(fill="x", padx=12, pady=(12, 6))
        crear_miniatura_producto(
            contenido, str(favorito["Codigo"]), size=(78, 104)
        ).pack(side="left", padx=(0, 12))
        informacion = ctk.CTkFrame(contenido, fg_color=blanco)
        informacion.pack(side="left", fill="both", expand=True)

        if favorito["EstadoFavorito"] == "Activo":
            nombre_favorito = ctk.CTkLabel(
                informacion, text=favorito["Nombre"], text_color=texto,
                anchor="w", justify="left", wraplength=360,
                font=fuente_texto(size=16, weight="bold")
            )
            nombre_favorito.pack(fill="x", pady=(2, 2))
            vincular_ajuste_de_texto(informacion, nombre_favorito)
            ctk.CTkLabel(
                informacion, text=f"{favorito['Seccion']} · {favorito['Tipo']}",
                text_color=gris, anchor="w", font=fuente_texto(size=12)
            ).pack(fill="x")
            ctk.CTkLabel(
                informacion, text=formatear_pesos(favorito["Precio"]),
                text_color=champagne_texto, anchor="w",
                font=fuente_titulo(size=17, weight="bold")
            ).pack(fill="x", pady=(4, 3))
            if favorito["Disponibilidad"] == "Disponible":
                color_estado = verde
                fondo_estado = "#E8F1E9"
            else:
                color_estado = rojo
                fondo_estado = "#F5E8E5"
            ctk.CTkLabel(
                informacion, text=favorito["Disponibilidad"],
                text_color=color_estado, fg_color=fondo_estado,
                corner_radius=8, font=fuente_texto(size=12, weight="bold")
            ).pack(anchor="w")
        else:
            # El producto ya no está en el catálogo
            nombre_favorito = ctk.CTkLabel(
                informacion, text=f"{favorito['Nombre']} ({favorito['Codigo']})",
                text_color=texto, anchor="w", justify="left", wraplength=360,
                font=fuente_texto(size=16, weight="bold")
            )
            nombre_favorito.pack(fill="x", pady=(2, 4))
            vincular_ajuste_de_texto(informacion, nombre_favorito)
            aviso_favorito = ctk.CTkLabel(
                informacion, text="Ya no está disponible en la tienda.",
                text_color=rojo, anchor="w", justify="left", wraplength=360,
                font=fuente_texto(size=13)
            )
            aviso_favorito.pack(fill="x")
            vincular_ajuste_de_texto(informacion, aviso_favorito)

        Boton(
            tarjeta, text="Quitar de favoritos", variant="destructivo", height=32,
            font=fuente_texto(size=13, weight="bold"),
            command=lambda caracter_c=favorito["Codigo"]: quitar_producto_favorito(caracter_c)
        ).pack(anchor="e", padx=12, pady=(0, 12))

    _organizar_tarjetas_adaptables(
        lista_favoritos, ancho_minimo=520, columnas_maximas=2, separacion=14
    )
    mostrar(pantalla_favoritos)


def quitar_producto_favorito(codigo):
    eliminar_favorito(sesion_actual.correo, codigo)
    mostrar_favoritos()

# PANEL ADMINISTRATIVO
# Reutiliza la identidad visual del cliente: carbón, champagne, marfil y blanco.
color_admin_negro = texto
color_admin_marfil = fondo
color_admin_navegacion = texto
color_admin_navegacion_hover = "#333333"

pantalla_admin = ctk.CTkFrame(contenedor_vistas, fg_color=color_admin_marfil, corner_radius=0)
encabezado_admin = ctk.CTkFrame(pantalla_admin, fg_color=texto, corner_radius=0)
encabezado_admin.pack(fill="x")
ctk.CTkLabel(
    encabezado_admin, text="Panel administrativo", text_color=champagne,
    font=fuente_titulo(size=22, weight="bold")
).pack(pady=(10, 10))

barra_admin = ctk.CTkFrame(pantalla_admin, fg_color=color_admin_marfil)
barra_admin.pack(fill="x", padx=8, pady=(7, 3))
for columna in range(2):
    barra_admin.grid_columnconfigure(columna, weight=1)
contenido_admin = ctk.CTkScrollableFrame(pantalla_admin, fg_color=color_admin_marfil)

mensaje_admin = ctk.CTkLabel(
    pantalla_admin, text="", text_color="#9B241B", wraplength=380,
    justify="left", font=fuente_texto(size=12)
)
mensaje_admin.pack(fill="x", padx=18, pady=(0, 4))
contenido_admin.pack(fill="both", expand=True, padx=8, pady=(0, 7))

def _limpiar_admin():
    for elemento in contenido_admin.winfo_children():
        elemento.destroy()
    contenido_admin._parent_canvas.yview_moveto(0)
    mensaje_admin.configure(text="")


def _titulo_admin(texto):
    ctk.CTkLabel(
        contenido_admin, text=texto, text_color=color_admin_negro, anchor="w",
        font=fuente_titulo(size=24, weight="bold")
    ).pack(fill="x", padx=10, pady=(8, 10))


def _rejilla_registros_admin(ancho_minimo=450, columnas_maximas=2, distribucion="registros"):
    rejilla = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    rejilla.pack(fill="x", padx=4, pady=(0, 8))
    rejilla._admin_ancho_minimo = ancho_minimo
    rejilla._admin_columnas_maximas = columnas_maximas
    rejilla._admin_separacion = 12
    rejilla._admin_distribucion = distribucion
    return rejilla


def _estado_admin(contenedor, estado):
    normalizado = str(estado).strip().casefold()
    if any(palabra in normalizado for palabra in ("activo", "confirmado", "devuelto", "finalizado", "completado")):
        color, superficie = verde, "#E8F1E9"
    elif any(palabra in normalizado for palabra in ("cancelado", "rechazado", "vencido", "inactivo")):
        color, superficie = rojo, "#F5E8E5"
    else:
        color, superficie = champagne_texto, fondo
    return ctk.CTkLabel(
        contenedor, text=str(estado), text_color=color, fg_color=superficie,
        corner_radius=8, padx=6, pady=3,
        font=fuente_texto(size=10, weight="bold")
    )


def _tarjeta_registro_admin(
    contenedor, titulo, campos, estado=None, total=None, productos=None
):
    tarjeta = crear_tarjeta(contenedor)
    encabezado = ctk.CTkFrame(tarjeta, fg_color=blanco)
    encabezado.pack(fill="x", padx=14, pady=(12, 8))
    ctk.CTkLabel(
        encabezado, text=str(titulo), text_color=color_admin_negro,
        anchor="w", justify="left", wraplength=360,
        font=fuente_titulo(size=13 if len(str(titulo)) > 24 else 16, weight="bold")
    ).pack(side="left", fill="x", expand=True)
    if estado not in (None, ""):
        _estado_admin(encabezado, estado).pack(side="right", padx=(8, 0))

    datos = ctk.CTkFrame(tarjeta, fg_color=blanco)
    datos.pack(fill="x", padx=14, pady=(0, 8))
    for columna in range(2):
        datos.grid_columnconfigure(columna, weight=1, uniform="registro_admin")
    for indice, (etiqueta, valor) in enumerate(campos):
        bloque = ctk.CTkFrame(datos, fg_color=blanco)
        bloque.grid(
            row=indice // 2, column=indice % 2, sticky="nsew",
            padx=(0, 8) if indice % 2 == 0 else (8, 0), pady=4
        )
        ctk.CTkLabel(
            bloque, text=str(etiqueta), text_color=gris, anchor="w",
            font=fuente_texto(size=11, weight="bold")
        ).pack(fill="x")
        ctk.CTkLabel(
            bloque, text=str(valor), text_color=color_admin_negro,
            anchor="w", justify="left", wraplength=250,
            font=fuente_texto(size=12)
        ).pack(fill="x")

    if productos:
        ctk.CTkLabel(
            tarjeta, text="Productos", text_color=gris, anchor="w",
            font=fuente_texto(size=11, weight="bold")
        ).pack(fill="x", padx=14, pady=(2, 2))
        for producto in productos:
            ctk.CTkLabel(
                tarjeta, text=str(producto), text_color=color_admin_negro,
                anchor="w", justify="left", wraplength=500,
                font=fuente_texto(size=12)
            ).pack(fill="x", padx=14, pady=1)

    if total is not None:
        ctk.CTkLabel(
            tarjeta, text=f"Total: {total}", text_color=champagne_texto,
            anchor="e", font=fuente_titulo(size=16, weight="bold")
        ).pack(fill="x", padx=14, pady=(6, 12))
    else:
        tarjeta.grid_configure(pady=6)
    return tarjeta


def _tarjeta_estadistica(contenedor, texto, valor, principal=False):
    tarjeta = crear_tarjeta(
        contenedor,
        fg_color=fondo if principal else blanco,
        border_color=champagne if principal else borde,
        border_width=2 if principal else 1,
    )
    ctk.CTkLabel(
        tarjeta, text=texto, text_color=gris, anchor="w",
        justify="left", wraplength=200,
        font=fuente_texto(size=12 if principal else 11, weight="bold")
    ).pack(fill="x", padx=12, pady=(10, 2))
    ctk.CTkLabel(
        tarjeta, text=str(valor), text_color=champagne_texto, anchor="w",
        font=fuente_titulo(size=22 if principal else 18, weight="bold")
    ).pack(fill="x", padx=12, pady=(0, 10))
    return tarjeta


def _organizar_tarjetas_admin(contenedor, ancho_minimo=520, columnas_maximas=2, separacion=12, distribucion='ancho'):
    contenedor._admin_ancho_minimo = ancho_minimo
    contenedor._admin_columnas_maximas = columnas_maximas
    contenedor._admin_separacion = separacion
    contenedor._admin_distribucion = distribucion
    contenido_admin._rejilla_admin_actual = contenedor
    ancho = contenedor.winfo_width()
    if ancho <= 1:
        ancho = max(1, contenedor.winfo_reqwidth())
    _aplicar_rejilla_admin(contenedor, ancho)
    _programar_actualizacion_rejilla_admin()


def _aplicar_rejilla_admin(contenedor, ancho):
    ancho_minimo = getattr(contenedor, "_admin_ancho_minimo", 520)
    columnas_maximas = getattr(contenedor, "_admin_columnas_maximas", 2)
    separacion = getattr(contenedor, "_admin_separacion", 12)
    distribucion = getattr(contenedor, "_admin_distribucion", "ancho")
    if distribucion in {"dashboard", "inventario", "estadisticas", "registros", "clientes"}:
        ancho_ventana = ventana.winfo_width()
        if distribucion in {"dashboard", "estadisticas"}:
            columnas = 1 if ancho_ventana < 380 else (2 if ancho_ventana < 800 else 3)
        elif distribucion == "clientes":
            columnas = 1 if ancho_ventana < 800 else (2 if ancho_ventana < 1120 else 3)
        elif distribucion == "registros":
            columnas = 1 if ancho_ventana < 800 else 2
        else:
            columnas = 1 if ancho_ventana < 800 else 2
    else:
        columnas = max(1, min(
            columnas_maximas,
            (ancho + separacion) // (ancho_minimo + separacion)
        ))
    columnas = min(columnas, columnas_maximas)
    layout_actual = (
        columnas,
        tuple(str(widget) for widget in contenedor.winfo_children()),
    )
    if getattr(contenedor, "_layout_admin_actual", None) == layout_actual:
        return
    contenedor._layout_admin_actual = layout_actual
    for columna in range(columnas_maximas):
        contenedor.grid_columnconfigure(columna, weight=1 if columna < columnas else 0)
    for indice, widget in enumerate(contenedor.winfo_children()):
        widget.grid(
            row=indice // columnas, column=indice % columnas,
            sticky="nsew", padx=separacion // 2, pady=separacion // 2
        )


def _actualizar_rejilla_admin_actual():
    if globals().get("pantalla_actual") is not pantalla_admin:
        return
    rejilla = getattr(contenido_admin, "_rejilla_admin_actual", None)
    if rejilla is None:
        return
    try:
        if not rejilla.winfo_exists():
            return
        ancho = rejilla.winfo_width()
        if ancho <= 1:
            ancho = max(
                1, min(ventana.winfo_width(), ANCHO_CONTENIDO_MAXIMO) - 32
            )
        _aplicar_rejilla_admin(rejilla, ancho)
    except (RuntimeError, TclError):
        return


def _programar_actualizacion_rejilla_admin(evento=None):
    if evento is not None and evento.widget is not ventana:
        return
    if globals().get("pantalla_actual") is not pantalla_admin:
        return
    if getattr(ventana, "_rejilla_admin_pendiente", False):
        return
    ventana._rejilla_admin_pendiente = True

    def aplicar():
        ventana._rejilla_admin_pendiente = False
        _actualizar_navegacion_admin()
        _actualizar_rejilla_admin_actual()

    ventana.after_idle(aplicar)


ventana.bind("<Configure>", _programar_actualizacion_rejilla_admin, add="+")

def _tarjeta_indicador_dashboard(contenedor, nombre, valor, principal=False):
    tarjeta = crear_tarjeta(
        contenedor,
        fg_color=fondo if principal else blanco,
        border_color=champagne if principal else borde,
        border_width=2 if principal else 1,
    )
    etiqueta = ctk.CTkLabel(
        tarjeta, text=nombre, text_color=gris, anchor="w",
        justify="left", wraplength=180,
        font=fuente_texto(size=13 if principal else 12, weight="bold")
    )
    etiqueta.pack(fill="x", padx=14, pady=(12, 2))
    vincular_ajuste_de_texto(tarjeta, etiqueta, ancho_minimo=130, margen=28)
    ctk.CTkLabel(
        tarjeta, text=str(valor),
        text_color=champagne_texto if principal else texto,
        anchor="w", justify="left",
        font=fuente_titulo(size=25 if principal else 21, weight="bold")
    ).pack(fill="x", padx=14, pady=(0, 12))
    return tarjeta


def _tarjeta_producto_admin(
    contenedor, codigo, nombre, precio, estado, detalle,
    descripcion=None, comando_editar=None, comando_desactivar=None
):
    tarjeta = crear_tarjeta(contenedor, corner_radius=RADIO_TARJETA)
    tarjeta.grid_columnconfigure(1, weight=1)

    area_foto = ctk.CTkFrame(
        tarjeta, fg_color=fondo, corner_radius=10,
        width=144, height=178
    )
    area_foto.grid(
        row=0, column=0, rowspan=2, sticky="nw",
        padx=(12, 10), pady=12
    )
    area_foto.grid_propagate(False)
    mostrar_foto_admin(area_foto, str(codigo), size=(132, 166))

    informacion = ctk.CTkFrame(tarjeta, fg_color=blanco)
    informacion.grid(
        row=0, column=1, sticky="nsew",
        padx=(0, 12), pady=(12, 6)
    )
    informacion.grid_columnconfigure(0, weight=1)

    etiqueta_nombre = ctk.CTkLabel(
        informacion, text=str(nombre), text_color=texto, anchor="w",
        justify="left", wraplength=360,
        font=fuente_titulo(size=17, weight="bold")
    )
    etiqueta_nombre.pack(fill="x")
    vincular_ajuste_de_texto(informacion, etiqueta_nombre, 160, 8)

    ctk.CTkLabel(
        informacion, text=f"Código · {codigo}", text_color=gris,
        anchor="w", font=fuente_texto(size=12)
    ).pack(fill="x", pady=(2, 2))

    ctk.CTkLabel(
        informacion, text=formatear_pesos(precio),
        text_color=champagne_texto, anchor="w",
        font=fuente_titulo(size=20, weight="bold")
    ).pack(fill="x", pady=(1, 5))

    etiqueta_detalle = ctk.CTkLabel(
        informacion, text=detalle, text_color=texto,
        anchor="w", justify="left", wraplength=360,
        font=fuente_texto(size=13, weight="bold")
    )
    etiqueta_detalle.pack(fill="x", pady=(0, 5))
    vincular_ajuste_de_texto(informacion, etiqueta_detalle, 160, 8)

    activo = str(estado).strip().casefold() == "activo"
    etiqueta_estado = ctk.CTkLabel(
        informacion, text=f"Estado · {estado}",
        text_color=verde if activo else rojo,
        fg_color="#E8F1E9" if activo else "#F5E8E5",
        corner_radius=8, anchor="w",
        font=fuente_texto(size=12, weight="bold")
    )
    etiqueta_estado.pack(anchor="w", pady=(1, 5))

    if descripcion:
        etiqueta_descripcion = ctk.CTkLabel(
            informacion, text=str(descripcion), text_color=gris,
            anchor="w", justify="left", wraplength=360,
            font=fuente_texto(size=13)
        )
        etiqueta_descripcion.pack(fill="x", pady=(0, 5))
        vincular_ajuste_de_texto(
            informacion, etiqueta_descripcion, ancho_minimo=160, margen=8
        )

    acciones = ctk.CTkFrame(tarjeta, fg_color=blanco)
    acciones.grid(
        row=1, column=1, sticky="ew",
        padx=(0, 12), pady=(2, 12)
    )
    acciones.grid_columnconfigure(0, weight=1)
    if comando_desactivar is None:
        Boton(
            acciones, text="Editar", variant="principal", height=34,
            command=comando_editar
        ).grid(row=0, column=0, sticky="ew")
    else:
        acciones.grid_columnconfigure(1, weight=1)
        Boton(
            acciones, text="Editar", variant="principal", height=34,
            command=comando_editar
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        Boton(
            acciones, text="Desactivar", variant="destructivo", height=34,
            state="disabled" if not activo else "normal",
            command=comando_desactivar
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))
    return tarjeta


def _mostrar_dashboard():
    _limpiar_admin()
    _titulo_admin("Dashboard")
    try:
        estadisticas = obtener_estadisticas_administracion()
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return

    rejilla_indicadores = ctk.CTkFrame(
        contenido_admin, fg_color=color_admin_marfil
    )
    rejilla_indicadores.pack(fill="x", padx=4, pady=(0, 8))
    indicadores_principales = {
        "Ventas simuladas", "Compras confirmadas", "Alquileres activos"
    }
    indicadores = [
        (nombre, valor, True)
        for nombre, valor in estadisticas.items()
        if nombre in indicadores_principales
    ]
    indicadores.extend(
        (nombre, valor, False)
        for nombre, valor in estadisticas.items()
        if nombre not in indicadores_principales
    )
    for nombre, valor, principal in indicadores:
        if nombre == "Ventas simuladas":
            valor = formatear_pesos(valor)
        _tarjeta_indicador_dashboard(
            rejilla_indicadores, texto_indicador(nombre), valor, principal
        )
    _organizar_tarjetas_admin(
        rejilla_indicadores, ancho_minimo=181,
        columnas_maximas=3, separacion=10, distribucion="dashboard"
    )

def _mostrar_inventario(vista="prendas"):
    _limpiar_admin()
    _titulo_admin("Inventario")
    barra_inventario = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    barra_inventario.pack(fill="x", padx=4, pady=(0, 6))
    Boton(
        barra_inventario, text="Prendas",
        fg_color=texto if vista == "prendas" else blanco,
        hover_color="#333333" if vista == "prendas" else borde,
        text_color=blanco if vista == "prendas" else champagne_texto,
        height=34, border_width=1, border_color=champagne if vista == "prendas" else borde,
        command=lambda: _mostrar_inventario("prendas")
    ).pack(side="left", padx=(0, 6))
    Boton(
        barra_inventario, text="Trajes",
        fg_color=texto if vista == "trajes" else blanco,
        hover_color="#333333" if vista == "trajes" else borde,
        text_color=blanco if vista == "trajes" else champagne_texto,
        height=34, border_width=1, border_color=champagne if vista == "trajes" else borde,
        command=lambda: _mostrar_inventario("trajes")
    ).pack(side="left")

    if vista == "trajes":
        _mostrar_trajes_admin_contenido()
        return

    controles = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    controles.pack(fill="x", padx=4, pady=(0, 8))
    busqueda = CampoTexto(
        controles, placeholder_text="Buscar por nombre o código",
        height=38, fg_color=blanco, border_color=borde, text_color=texto
    )
    busqueda.pack(side="left", fill="x", expand=True, padx=(0, 6))
    Boton(
        controles, text="+ Agregar prenda", height=38, fg_color=texto,
        hover_color="#333333", text_color=blanco,
        command=lambda: _abrir_formulario_prenda(
            actualizar_lista=cargar_prendas
        )
    ).pack(side="right")

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
            ctk.CTkLabel(
                lista_prendas, text="No hay prendas que coincidan con la búsqueda.",
                text_color=gris, anchor="w",
                font=fuente_texto(size=14)
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=20)
            return
        for _, producto in encontrados.iterrows():
            variantes = existencias[
                existencias["Codigo"].astype(str).str.casefold()
                == str(producto["Codigo"]).casefold()
            ]
            detalle_tallas = "\n".join(
                f"Talla {fila['Talla']}  ·  Existencias: {int(fila['Cantidad'])}"
                for _, fila in variantes.iterrows()
            ) or "Sin tallas registradas"
            _tarjeta_producto_admin(
                lista_prendas,
                codigo=producto["Codigo"],
                nombre=producto["Nombre"],
                precio=producto["Precio"],
                estado=producto["Estado"],
                detalle=f"Inventario\n{detalle_tallas}",
                comando_editar=lambda producto_p=producto, variantes_v=variantes:
                    _abrir_formulario_prenda(
                        producto_p, variantes_v, cargar_prendas
                    ),
                comando_desactivar=lambda codigo_c=producto["Codigo"]:
                    _desactivar_prenda(codigo_c, cargar_prendas),
            )
        _organizar_tarjetas_admin(
            lista_prendas, ancho_minimo=440,
            columnas_maximas=2, separacion=12, distribucion="inventario"
        )

    busqueda.bind("<KeyRelease>", lambda evento: cargar_prendas())
    cargar_prendas()

def _mostrar_trajes_admin_contenido():
    controles = ctk.CTkFrame(contenido_admin, fg_color=color_admin_marfil)
    controles.pack(fill="x", padx=4, pady=(0, 8))
    busqueda = CampoTexto(
        controles, placeholder_text="Buscar por nombre o código",
        height=38, fg_color=blanco, border_color=borde, text_color=texto
    )
    busqueda.pack(side="left", fill="x", expand=True, padx=(0, 6))
    Boton(
        controles, text="+ Agregar traje", height=38, fg_color=texto,
        hover_color="#333333", text_color=blanco,
        command=lambda: _abrir_formulario_traje(
            actualizar_lista=cargar_trajes_admin
        )
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
                font=fuente_texto(size=14)
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=20)
            return

        for _, traje in encontrados.iterrows():
            codigo = traje["Codigo"]
            _tarjeta_producto_admin(
                lista_trajes_admin,
                codigo=codigo,
                nombre=traje["Nombre"],
                precio=traje["Precio"],
                estado=traje["Estado"],
                detalle=f"Tallas disponibles · {traje['Tallas']}",
                descripcion=traje["Descripcion"],
                comando_editar=lambda traje_p=traje:
                    _abrir_formulario_traje(traje_p, cargar_trajes_admin),
            )
        _organizar_tarjetas_admin(
            lista_trajes_admin, ancho_minimo=440,
            columnas_maximas=2, separacion=12, distribucion="inventario"
        )

    busqueda.bind("<KeyRelease>", lambda evento: cargar_trajes_admin())
    cargar_trajes_admin()

def _mostrar_trajes_admin_pendiente():
    _mostrar_inventario("trajes")


def mostrar_foto_admin(contenedor, codigo, size=(132, 166)):
    ruta = next(
        (carpeta_imagenes / f"{codigo}{extension}"
         for extension in (".jpg", ".jpeg", ".png")
         if (carpeta_imagenes / f"{codigo}{extension}").exists()),
        None
    )
    if ruta is None:
        ctk.CTkLabel(
            contenedor, text=iconos_ropa.get("Prenda", "🛍️"),
            text_color=gris, font=ctk.CTkFont(size=32)
        ).pack(expand=True)
        return
    with Image.open(ruta) as original:
        imagen = ImageOps.exif_transpose(original).convert("RGB")
    ancho, alto = size
    imagen = ImageOps.contain(
        imagen, (ancho - 6, alto - 6), method=Image.Resampling.LANCZOS
    )
    clave_cache = (str(ruta), imagen.size)
    foto = cache_ctk_imagenes.get(clave_cache)
    if foto is None:
        foto = ctk.CTkImage(light_image=imagen, size=imagen.size)
        cache_ctk_imagenes[clave_cache] = foto
    etiqueta = ctk.CTkLabel(contenedor, image=foto, text="")
    etiqueta.image = foto
    etiqueta.bind("<Button-1>", lambda evento: ampliar_fotografia(codigo))
    etiqueta.configure(cursor="hand2")
    etiqueta.pack(expand=True)

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
            font=fuente_texto(size=12, weight="bold")
        ).pack(fill="x", pady=(5, 2))
        entrada = CampoTexto(
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
        font=fuente_texto(size=12, weight="bold")
    ).pack(fill="x", pady=(5, 2))
    estado = Selector(
        formulario, values=["Activo", "Inactivo"], fg_color=blanco,
        button_color=champagne, button_hover_color="#333333", text_color=texto
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

    Boton(
        formulario, text="Seleccionar fotografía", height=34, fg_color=texto,
        hover_color="#333333", text_color=blanco, command=seleccionar_foto
    ).pack(fill="x", pady=(2, 8))

    def guardar():
        codigo_valor = str(codigo.get()).strip().upper()
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
                    return
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
        except (OSError, ValueError, PermissionError, ImportError) as problema:
            messagebox.showerror("No se pudo guardar el traje", str(problema))
            return
        foto_error = None
        if foto is not None:
            try:
                _copiar_fotografia_producto(codigo_valor, foto)
            except (OSError, ValueError) as problema:
                foto_error = (
                    f"Los datos del traje se guardaron, pero la fotografía "
                    f"no pudo actualizarse: {problema}"
                )
                messagebox.showerror("Traje guardado", foto_error)
        ventana_formulario.destroy()
        if actualizar_lista:
            actualizar_lista()
        else:
            _mostrar_inventario("trajes")
        if foto_error:
            mensaje_admin.configure(text=foto_error, text_color=rojo)
        else:
            mensaje_admin.configure(text="¡Traje guardado exitosamente!", text_color=verde)

    Boton(
        formulario, text="Guardar traje", height=40, fg_color=texto,
        hover_color="#333333", text_color=blanco, command=guardar
    ).pack(fill="x", pady=(8, 3))
    Boton(
        formulario, text="Cancelar", height=34, fg_color="transparent",
        hover_color=borde, text_color=champagne_texto, command=ventana_formulario.destroy
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
            font=fuente_texto(size=12, weight="bold")
        ).pack(fill="x", pady=(5, 2))
        entrada = CampoTexto(
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
        font=fuente_texto(size=12, weight="bold")
    ).pack(fill="x", pady=(5, 2))
    seccion = Selector(
        formulario, values=["Mujer", "Hombre", "Unisex"], fg_color=blanco,
        button_color=champagne, button_hover_color="#333333", text_color=texto
    )
    seccion.pack(fill="x", pady=(5, 3))
    seccion.set(producto["Seccion"] if editar else "Mujer")
    tipo = campo("Tipo", producto["Tipo"] if editar else "")
    ctk.CTkLabel(
        formulario, text="Estado", text_color=texto, anchor="w",
        font=fuente_texto(size=12, weight="bold")
    ).pack(fill="x", pady=(5, 2))
    estado = Selector(
        formulario, values=["Activo", "Inactivo"], fg_color=blanco,
        button_color=champagne, button_hover_color="#333333", text_color=texto
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

    Boton(
        formulario, text="Seleccionar fotografía", height=34, fg_color=texto,
        hover_color="#333333", text_color=blanco, command=seleccionar_foto
    ).pack(fill="x", pady=(2, 8))

    ctk.CTkLabel(
        formulario, text="Tallas y existencias", text_color=texto, anchor="w",
        font=fuente_titulo(size=18, weight="bold")
    ).pack(fill="x", pady=(4, 4))
    filas_tallas = ctk.CTkFrame(formulario, fg_color=fondo)
    filas_tallas.pack(fill="x")
    entradas_tallas = []

    def agregar_fila_talla(talla="", cantidad=""):
        fila = ctk.CTkFrame(filas_tallas, fg_color=fondo)
        fila.pack(fill="x", pady=2)
        talla_entrada = CampoTexto(
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
        cantidad_entrada = CampoTexto(
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
    Boton(
        formulario, text="+ Agregar talla", height=30, fg_color="transparent",
        hover_color=borde, text_color=champagne_texto, command=agregar_fila_talla
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
        foto = foto_seleccionada["ruta"]
        if foto is not None:
            destinos = [
                carpeta_imagenes / f"{codigo_valor}{extension}"
                for extension in (".jpg", ".jpeg", ".png")
            ]
            if any(destino.exists() for destino in destinos) and not messagebox.askyesno(
                "Reemplazar fotografía",
                f"Ya existe una fotografía para {codigo_valor}. ¿Deseas reemplazarla?",
                parent=ventana_formulario
            ):
                return
        try:
            if editar:
                guardar_producto_completo(
                    codigo_valor, nombre.get(), seccion.get(), tipo.get(),
                    precio.get(), descripcion.get(), estado.get(), datos_tallas,
                    codigo_original=producto["Codigo"]
                )
            else:
                guardar_producto_completo(
                    codigo_valor, nombre.get(), seccion.get(), tipo.get(),
                    precio.get(), descripcion.get(), estado.get(), datos_tallas
                )
        except (OSError, ValueError, PermissionError) as problema:
            messagebox.showerror("No se pudo guardar", str(problema))
            return
        foto_error = None
        if foto is not None:
            try:
                _copiar_fotografia_producto(codigo_valor, foto)
            except (OSError, ValueError) as problema:
                foto_error = (
                    f"Los datos de la prenda se guardaron, pero la fotografía "
                    f"no pudo actualizarse: {problema}"
                )
                messagebox.showerror("Prenda guardada", foto_error)
        ventana_formulario.destroy()
        if actualizar_lista:
            actualizar_lista()
        else:
            _mostrar_inventario()
        if foto_error:
            mensaje_admin.configure(text=foto_error, text_color=rojo)
        else:
            mensaje_admin.configure(text="¡Prenda guardada exitosamente!", text_color=verde)

    Boton(
        formulario, text="Guardar prenda", height=40, fg_color=texto,
        hover_color="#333333", text_color=blanco, command=guardar
    ).pack(fill="x", pady=(8, 3))
    Boton(
        formulario, text="Cancelar", height=34, fg_color="transparent",
        hover_color=borde, text_color=champagne_texto, command=ventana_formulario.destroy
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
    rejilla = _rejilla_registros_admin(ancho_minimo=500, columnas_maximas=2)
    if not compras:
        ctk.CTkLabel(
            rejilla, text="No hay compras registradas.", text_color=gris,
            font=fuente_texto(size=13)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=12)
    for compra in reversed(compras):
        articulos = [
            f"{articulo['Nombre']} · x{articulo['Cantidad']}"
            for articulo in compra["Articulos"]
        ]
        campos = [
            ("Cliente", compra["Correo"]),
            ("Fecha", compra["Fecha"]),
            ("Método de pago", compra.get("MetodoPago", "Método no registrado")),
            ("Estado del pago", texto_estado_pago(compra.get("EstadoPago", "Pago anterior no registrado"))),
        ]
        _tarjeta_registro_admin(
            rejilla, compra["Pedido"], campos,
            estado=compra.get("Estado"),
            total=formatear_pesos(compra["Total"]),
            productos=articulos,
        ).grid(row=len(rejilla.winfo_children()), column=0, sticky="nsew", padx=6, pady=6)
    _organizar_tarjetas_admin(
        rejilla, ancho_minimo=500, columnas_maximas=2,
        separacion=12, distribucion="registros"
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
    rejilla = _rejilla_registros_admin(ancho_minimo=520, columnas_maximas=2)
    if not alquileres:
        ctk.CTkLabel(
            rejilla, text="No hay registros para mostrar.", text_color=gris,
            font=fuente_texto(size=13)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=12)
    for alquiler in reversed(alquileres):
        campos = [
            ("Cliente", alquiler.get("NombreCliente", "Dato no registrado")),
            ("Correo", alquiler["Correo"]),
            ("Teléfono", alquiler.get("TelefonoCliente", "Dato no registrado")),
            ("Dirección", alquiler.get("DireccionCliente", "Dato no registrado")),
            ("Traje", alquiler["Nombre"]),
            ("Código", alquiler["Codigo"]),
            ("Talla", alquiler["Talla"]),
            ("Fecha de alquiler", alquiler["FechaAlquiler"]),
            ("Devolución prevista", alquiler["FechaProgramada"]),
        ]
        if alquiler["FechaReal"]:
            campos.append(("Devolución real", alquiler["FechaReal"]))
        campos.extend([
            ("Método de pago", alquiler.get("MetodoPago", "Método no registrado")),
            ("Estado del pago", texto_estado_pago(alquiler.get("EstadoPago", "Pago anterior no registrado"))),
        ])
        campos.append(("Precio", formatear_pesos(float(alquiler["Precio"]))))
        _tarjeta_registro_admin(
            rejilla, alquiler["Nombre"], campos, estado=alquiler["Estado"]
        ).grid(row=len(rejilla.winfo_children()), column=0, sticky="nsew", padx=6, pady=6)
    _organizar_tarjetas_admin(
        rejilla, ancho_minimo=520, columnas_maximas=2,
        separacion=12, distribucion="registros"
    )


def _mostrar_clientes_admin():
    _limpiar_admin()
    _titulo_admin("Clientes")
    try:
        clientes = listar_clientes_administracion()
    except (OSError, ValueError, PermissionError) as problema:
        mensaje_admin.configure(text=str(problema), text_color=rojo)
        return
    rejilla = _rejilla_registros_admin(ancho_minimo=320, columnas_maximas=3, distribucion="clientes")
    if not clientes:
        ctk.CTkLabel(
            rejilla, text="No hay clientes registrados.", text_color=gris,
            font=fuente_texto(size=13)
        ).grid(row=0, column=0, sticky="w", padx=8, pady=12)
    for cliente in clientes:
        nombre = cliente["Nombre"] if cliente["Nombre"] != "Sin datos" else "Perfil sin datos personales"
        _tarjeta_registro_admin(
            rejilla, nombre, [("Correo", cliente["Correo"])]
        ).grid(row=len(rejilla.winfo_children()), column=0, sticky="nsew", padx=6, pady=6)
    _organizar_tarjetas_admin(
        rejilla, ancho_minimo=320, columnas_maximas=3,
        separacion=12, distribucion="clientes"
    )


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
    principales = {"Compras confirmadas", "Ventas simuladas", "Alquileres activos"}
    for indice, nombre in enumerate(nombres):
        valor = estadisticas[nombre]
        tarjeta = _tarjeta_estadistica(
            tarjetas_estadisticas, texto_indicador(nombre),
            formatear_pesos(valor) if nombre == "Ventas simuladas" else valor,
            principal=nombre in principales,
        )
        tarjeta.grid(row=indice, column=0, sticky="nsew", padx=6, pady=6)
    _organizar_tarjetas_admin(
        tarjetas_estadisticas, ancho_minimo=190,
        columnas_maximas=3, separacion=12, distribucion="estadisticas"
    )


def mostrar_panel_admin(seccion="Dashboard"):
    global seccion_admin_activa
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
    seccion_admin_activa = seccion
    _actualizar_navegacion_admin()
    mostrar(pantalla_admin)
    _programar_actualizacion_rejilla_admin()


secciones_admin = [
    "Dashboard", "Inventario", "Compras", "Alquileres",
    "Devoluciones", "Clientes", "Estadísticas"
]
botones_navegacion_admin = {}


def _actualizar_navegacion_admin(evento=None):
    if evento is not None and evento.widget not in (barra_admin, ventana):
        return
    if not botones_navegacion_admin:
        return
    ancho = max(1, ventana.winfo_width())
    columnas = 2 if ancho < 390 else (3 if ancho < 800 else (4 if ancho < 1120 else 7))
    columnas_anteriores = getattr(barra_admin, "_columnas_nav_admin", None)
    for columna in range(7):
        barra_admin.grid_columnconfigure(columna, weight=1 if columna < columnas else 0)
    if columnas != columnas_anteriores:
        for indice, nombre in enumerate(secciones_admin):
            boton = botones_navegacion_admin[nombre]
            boton.grid_forget()
            boton.grid(
                row=indice // columnas, column=indice % columnas,
                sticky="ew", padx=3, pady=3
            )
        barra_admin._columnas_nav_admin = columnas
    for nombre in secciones_admin:
        boton = botones_navegacion_admin[nombre]
        activo = nombre == seccion_admin_activa
        boton.configure(
            height=34,
            fg_color=texto if activo else blanco,
            hover_color="#333333" if activo else borde,
            text_color=blanco if activo else champagne_texto,
            border_width=1,
            border_color=champagne if activo else borde,
            font=fuente_texto(size=13, weight="bold" if activo else "normal"),
        )


seccion_admin_activa = "Dashboard"
for nombre_seccion in secciones_admin:
    boton_seccion = Boton(
        barra_admin, text=nombre_seccion,
        command=lambda seccion=nombre_seccion: mostrar_panel_admin(seccion),
        height=34, fg_color=blanco, hover_color=borde,
        text_color=champagne_texto, border_width=1, border_color=borde,
        font=fuente_texto(size=13)
    )
    botones_navegacion_admin[nombre_seccion] = boton_seccion
barra_admin.bind("<Configure>", _actualizar_navegacion_admin, add="+")

Boton(
    pantalla_admin, text="← Volver al menú cliente", command=lambda: mostrar(pantalla_menu),
    fg_color=texto, hover_color="#333333", text_color=blanco,
    font=fuente_texto(size=13, weight="bold")
).pack(fill="x", padx=18, pady=(0, 14))
Boton(
    pantalla_admin, text="Cerrar sesión", command=cerrar_sesion_interfaz,
    fg_color="transparent", hover_color=borde, text_color=champagne_texto,
    font=fuente_texto(size=13, weight="bold")
).pack(pady=(0, 40))

#INICIO
# PANTALLA: INICIO
pantalla_inicio = ctk.CTkFrame(contenedor_vistas, fg_color=fondo, corner_radius=0)
inicio_scroll = ctk.CTkScrollableFrame(pantalla_inicio, fg_color=fondo)
inicio_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 10))

Boton(inicio_scroll, text="← Volver al menú", command=lambda: mostrar(pantalla_menu), fg_color="transparent", hover_color=borde, text_color=champagne_texto, anchor="w", font=fuente_texto(size=14, weight="bold")).pack(fill="x", padx=8, pady=(12, 8))

bienvenida_inicio = ctk.CTkFrame(
    inicio_scroll, fg_color=blanco, corner_radius=16,
    border_width=1, border_color=champagne
)
bienvenida_inicio.pack(fill="x", padx=8, pady=(0, 18))
bienvenida_copy = ctk.CTkFrame(bienvenida_inicio, fg_color=blanco)
bienvenida_copy.pack(fill="x", padx=20, pady=(22, 20))
titulo_bienvenida_inicio = ctk.CTkLabel(
    bienvenida_copy, text="¡Bienvenidos a EFRATA Mini-Mall!",
    text_color=texto, justify="center", anchor="center", wraplength=1000,
    font=fuente_titulo(size=22, weight="bold")
)
titulo_bienvenida_inicio.pack(fill="x", padx=18, pady=(0, 10))
vincular_ajuste_de_texto(
    bienvenida_copy, titulo_bienvenida_inicio, ancho_minimo=240, margen=40
)
frase_bienvenida_inicio = ctk.CTkLabel(
    bienvenida_copy,
    text="Moda, alquiler de trajes y arreglos en un solo lugar",
    text_color=gris, justify="center", anchor="center", wraplength=1000,
    font=fuente_texto(size=14)
)
frase_bienvenida_inicio.pack(fill="x", padx=18, pady=(0, 18))
vincular_ajuste_de_texto(
    bienvenida_copy, frase_bienvenida_inicio, ancho_minimo=240, margen=40
)
accesos_inicio = ctk.CTkFrame(bienvenida_copy, fg_color=blanco)
accesos_inicio.pack(anchor="center")
Boton(
    accesos_inicio, text="Ver ropa", command=mostrar_catalogo_ropa,
    width=140, height=42, corner_radius=10, fg_color=texto,
    hover_color="#333333", text_color=blanco,
    font=fuente_texto(size=14, weight="bold")
).pack(side="left", padx=6)
Boton(
    accesos_inicio, text="Alquilar trajes", command=mostrar_trajes,
    width=140, height=42, corner_radius=10, fg_color=blanco,
    border_width=1, border_color=champagne, hover_color=borde,
    text_color=texto, font=fuente_texto(size=14, weight="bold")
).pack(side="left", padx=6)

ctk.CTkLabel(
    inicio_scroll, text="Lo que ofrecemos", text_color=texto, anchor="w",
    font=fuente_titulo(size=20, weight="bold")
).pack(fill="x", padx=16, pady=(0, 8))
fila_servicios = ctk.CTkFrame(inicio_scroll, fg_color=fondo)
fila_servicios.pack(fill="x", padx=8, pady=(0, 16))
for icono, servicio in [
    ("✦", "Moda nacional\ne importada"),
    ("◇", "Trajes para\ntoda ocasión"),
    ("✂", "Arreglo\nde ropa"),
]:
    tarjeta_servicio = crear_tarjeta(fila_servicios)
    ctk.CTkLabel(
        tarjeta_servicio, text=icono, text_color=champagne_texto,
        font=fuente_titulo(size=26, weight="bold")
    ).pack(pady=(12, 2))
    ctk.CTkLabel(
        tarjeta_servicio, text=servicio, text_color=texto, justify="center",
        font=fuente_texto(size=12, weight="bold")
    ).pack(padx=6, pady=(0, 12))
_organizar_tarjetas_adaptables(
    fila_servicios, ancho_minimo=180, columnas_maximas=3, separacion=12
)

contacto = crear_tarjeta(inicio_scroll)
contacto.pack(fill="x", padx=8, pady=(0, 12))
ctk.CTkLabel(
    contacto, text="📍  Cali, Colombia", text_color=texto, anchor="w",
    font=fuente_texto(size=14)
).pack(fill="x", padx=16, pady=(10, 3))
ctk.CTkLabel(
    contacto, text="📞  323 965 5863", text_color=texto, anchor="w",
    font=fuente_texto(size=14)
).pack(fill="x", padx=16, pady=(3, 10))
ctk.CTkLabel(
    inicio_scroll, text="¡Será un placer atenderte!", text_color=champagne_texto,
    font=fuente_texto(size=15, weight="bold")
).pack(pady=(0, 12))

#Ventana calendario GRANDE

ventana_calendario = None

def abrir_calendario(variable):
    global ventana_calendario

    if ventana_calendario is not None and ventana_calendario.winfo_exists():
        ventana_calendario.lift()
        return

    ventana_calendario = ctk.CTkToplevel(ventana)
    ventana_calendario.title("Seleccionar fecha")
    ventana_calendario.resizable(False, False)
    ventana_calendario.configure(fg_color=fondo)
    ventana_calendario.transient(ventana)
    ventana.update_idletasks()
    pantalla_ancho = ventana_calendario.winfo_screenwidth()
    pantalla_alto = ventana_calendario.winfo_screenheight()
    ancho = min(390, max(320, pantalla_ancho - 32))
    alto = min(400, max(360, pantalla_alto - 80))
    x = ventana.winfo_rootx() + (ventana.winfo_width() - ancho) // 2
    y = ventana.winfo_rooty() + (ventana.winfo_height() - alto) // 2
    x = min(max(x, 0), max(pantalla_ancho - ancho, 0))
    y = min(max(y, 0), max(pantalla_alto - alto, 0))
    ventana_calendario.geometry(f"{ancho}x{alto}+{x}+{y}")

    calendario = Calendar(
        ventana_calendario, selectmode="day", date_pattern="dd/mm/yyyy",
        locale="es_ES", mindate=datetime.date.today(),
        font=(letra_texto, 12), background=texto, foreground=blanco,
        headersbackground=texto, headersforeground=blanco,
        selectbackground=champagne_texto, selectforeground=blanco,
        normalbackground=blanco, normalforeground=texto,
        weekendbackground=borde, weekendforeground=texto
    )
    calendario.pack(padx=16, pady=(16, 12), fill="both", expand=True)

    def confirmar_fecha():
        fecha = calendario.selection_get()
        if fecha is not None:
            variable.set(fecha.strftime("%d/%m/%Y"))
        ventana_calendario.destroy()

    Boton(
        ventana_calendario, text="Confirmar fecha", command=confirmar_fecha,
        height=40, font=fuente_texto(size=14, weight="bold")
    ).pack(padx=16, pady=(0, 16), fill="x")
    ventana_calendario.bind("<Escape>", lambda evento: ventana_calendario.destroy())
    ventana_calendario.after(200, ventana_calendario.lift)



def ejecutar_interfaz():
    ventana.mainloop()


if __name__ == "__main__":
    ejecutar_interfaz()
