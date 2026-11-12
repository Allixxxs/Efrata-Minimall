

import os
import tempfile
from .rutas import ARCHIVO_DATOS_PERSONALES, DIRECTORIO_DATOS
from .sesion import requerir_usuario


def validar_datos_personales(datos):
    def nombre(valor, etiqueta):
        valor = str(valor).strip()
        if (not valor or "|" in valor or "\n" in valor or "\r" in valor
                or not any(ch.isalpha() for ch in valor)
                or any(not (ch.isalpha() or ch in " -'’") for ch in valor)):
            raise ValueError(f"{etiqueta} debe contener letras y puede incluir espacios o guiones.")
        return " ".join(valor.split())

    resultado = {
        "Nombre": nombre(datos.get("Nombre", ""), "El nombre"),
        "Apellidos": nombre(datos.get("Apellidos", ""), "Los apellidos"),
        "Telefono": str(datos.get("Telefono", "")).strip(),
        "TipoDocumento": str(datos.get("TipoDocumento", "")).strip().upper(),
        "NumeroDocumento": str(datos.get("NumeroDocumento", "")).strip(),
        "Direccion": str(datos.get("Direccion", "")).strip(),
        "CodigoPostal": str(datos.get("CodigoPostal", "")).strip(),
    }
    if not resultado["Telefono"].isdigit() or len(resultado["Telefono"]) != 10:
        raise ValueError("El teléfono debe contener 10 dígitos.")
    if resultado["TipoDocumento"] not in {"CC", "CE", "NIT"}:
        raise ValueError("El tipo de documento debe ser CC, CE o NIT.")
    if not resultado["NumeroDocumento"].isdigit():
        raise ValueError("El número de documento debe contener solo dígitos.")
    if not resultado["Direccion"] or any(caracter_c in resultado["Direccion"] for caracter_c in "|\r\n"):
        raise ValueError("La dirección no puede estar vacía ni contener separadores o saltos de línea.")
    if not resultado["CodigoPostal"].isdigit() or len(resultado["CodigoPostal"]) != 6:
        raise ValueError("El código postal debe contener seis dígitos.")
    return resultado


def leer_datos_personales(correo):
    correo = requerir_usuario(correo)
    if not ARCHIVO_DATOS_PERSONALES.exists():
        return None
    encontrado = []
    with ARCHIVO_DATOS_PERSONALES.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = linea.rstrip("\r\n").split("|")
            if len(campos) == 8 and campos[0].strip().casefold() == correo:
                encontrado.append(dict(zip(
                    ("Correo", "Nombre", "Apellidos", "Telefono", "TipoDocumento",
                     "NumeroDocumento", "Direccion", "CodigoPostal"), campos
                )))
    return encontrado[-1] if encontrado else None


def _reemplazar_lineas_personales(lineas):
    descripcion, nombre_temporal = tempfile.mkstemp(
        prefix=".datos_personales_", suffix=".tmp", dir=DIRECTORIO_DATOS
    )
    try:
        with os.fdopen(descripcion, "w", encoding="utf-8", newline="") as archivo:
            archivo.writelines(lineas)
        os.replace(nombre_temporal, ARCHIVO_DATOS_PERSONALES)
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise


def guardar_datos_personales(correo, datos):
    correo = requerir_usuario(correo)
    datos = validar_datos_personales(datos)
    lineas = []
    if ARCHIVO_DATOS_PERSONALES.exists():
        with ARCHIVO_DATOS_PERSONALES.open("r", encoding="utf-8", newline="") as archivo:
            for linea in archivo:
                propietario = linea.rstrip("\r\n").split("|", 1)[0].strip().casefold()
                if propietario != correo:
                    lineas.append(linea if linea.endswith(("\n", "\r")) else linea + "\n")
    lineas.append("|".join((correo, *(datos[clave] for clave in (
        "Nombre", "Apellidos", "Telefono", "TipoDocumento", "NumeroDocumento",
        "Direccion", "CodigoPostal"
    )))) + "\n")
    _reemplazar_lineas_personales(lineas)
    return leer_datos_personales(correo)


def eliminar_datos_personales(correo):
    correo = requerir_usuario(correo)
    if not ARCHIVO_DATOS_PERSONALES.exists():
        return False
    lineas, eliminado = [], False
    with ARCHIVO_DATOS_PERSONALES.open("r", encoding="utf-8", newline="") as archivo:
        for linea in archivo:
            propietario = linea.rstrip("\r\n").split("|", 1)[0].strip().casefold()
            if propietario == correo:
                eliminado = True
            else:
                lineas.append(linea if linea.endswith(("\n", "\r")) else linea + "\n")
    if eliminado:
        _reemplazar_lineas_personales(lineas)
    return eliminado
