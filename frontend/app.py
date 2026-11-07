import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from backend import authenticate_user, close_session, load_suits


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


def abrir_opcion(nombre):
    if nombre == "Alquilar trajes":
        ver_trajes()
    else:
        aviso.configure(text=f"\"{nombre}\" lo hacemos pronto.")

for opcion in ["Inicio", "Buscar trajes", "Alquilar trajes", "Consultar alquileres", "Devolver traje", "Ver carrito", "Ver favoritos", "Mis datos", "Mis compras"]:
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
        ctk.CTkLabel(tarjeta, text=texto_estado, text_color=color_estado, anchor="w", font=ctk.CTkFont(family=letra_texto, size=12, weight="bold")).pack(fill="x", padx=14, pady=(0, 12))

    mostrar(pantalla_trajes)


ventana.mainloop()



