

from datetime import datetime
from .rutas import ARCHIVO_USUARIOS, ARCHIVO_REGISTRO_SESIONES
from .sesion import sesion_actual


def normalizar_correo(correo):
    valor = str(correo or "").strip().casefold()
    if (
        not valor or "|" in valor or "\n" in valor or "\r" in valor
        or " " in valor or valor.count("@") != 1
    ):
        raise ValueError("El correo electrónico no tiene un formato válido.")
    parte_local, dominio = valor.rsplit("@", 1)
    if not parte_local or dominio not in {"gmail.com", "hotmail.com"}:
        raise ValueError("El correo debe ser de Gmail o Hotmail.")
    return valor


def validar_contrasena(contrasena):
    valor = str(contrasena or "")
    if (
        len(valor) < 8 or not any(caracter_c.isupper() for caracter_c in valor)
        or not any(caracter_c.islower() for caracter_c in valor) or not any(caracter_c.isdigit() for caracter_c in valor)
        or "|" in valor or "\n" in valor or "\r" in valor
    ):
        raise ValueError("La contraseña requiere 8 caracteres, mayúscula, minúscula y número.")
    return valor


def _leer_usuarios():
    if not ARCHIVO_USUARIOS.exists():
        return {}
    usuarios = {}
    with ARCHIVO_USUARIOS.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) == 2 and campos[0].strip():
                usuarios[campos[0].strip().casefold()] = campos[1]
    return usuarios


def existe_usuario(correo):
    return normalizar_correo(correo) in _leer_usuarios()


def registrar_usuario(correo, contrasena):
    correo = normalizar_correo(correo)
    contrasena = validar_contrasena(contrasena)
    if correo in _leer_usuarios():
        raise ValueError("Ya existe una cuenta con ese correo.")
    with ARCHIVO_USUARIOS.open("a", encoding="utf-8") as archivo:
        archivo.write(f"{correo}|{contrasena}\n")
    _iniciar_sesion(correo, contrasena)
    _registrar_inicio_sesion(correo)
    return True


def autenticar_usuario(correo, contrasena):
    correo = normalizar_correo(correo)
    if _leer_usuarios().get(correo) != str(contrasena):
        return False
    _iniciar_sesion(correo, str(contrasena))
    _registrar_inicio_sesion(correo)
    return True


def _iniciar_sesion(correo, contrasena):
    sesion_actual.correo = correo
    sesion_actual.contrasena = contrasena
    sesion_actual.activa = True


def _registrar_inicio_sesion(correo):
    with ARCHIVO_REGISTRO_SESIONES.open("a", encoding="utf-8") as archivo:
        archivo.write(f"{correo}|{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")


def cerrar_sesion():
    sesion_actual.correo = ""
    sesion_actual.contrasena = ""
    sesion_actual.activa = False
