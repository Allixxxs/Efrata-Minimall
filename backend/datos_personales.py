"""Servicios de datos personales; no solicitan entrada ni imprimen."""

import os
import tempfile
from .rutas import PERSONAL_DATA_FILE, DATA_DIR
from .sesion import require_user


def validate_personal_data(data):
    def name(value, label):
        value = str(value).strip()
        if (not value or "|" in value or "\n" in value or "\r" in value
                or not any(ch.isalpha() for ch in value)
                or any(not (ch.isalpha() or ch in " -'’") for ch in value)):
            raise ValueError(f"{label} debe contener letras y puede incluir espacios o guiones.")
        return " ".join(value.split())

    result = {
        "Nombre": name(data.get("Nombre", ""), "El nombre"),
        "Apellidos": name(data.get("Apellidos", ""), "Los apellidos"),
        "Telefono": str(data.get("Telefono", "")).strip(),
        "TipoDocumento": str(data.get("TipoDocumento", "")).strip().upper(),
        "NumeroDocumento": str(data.get("NumeroDocumento", "")).strip(),
        "Direccion": str(data.get("Direccion", "")).strip(),
        "CodigoPostal": str(data.get("CodigoPostal", "")).strip(),
    }
    if not result["Telefono"].isdigit() or len(result["Telefono"]) != 10:
        raise ValueError("El teléfono debe contener 10 dígitos.")
    if result["TipoDocumento"] not in {"CC", "CE", "NIT"}:
        raise ValueError("El tipo de documento debe ser CC, CE o NIT.")
    if not result["NumeroDocumento"].isdigit():
        raise ValueError("El número de documento debe contener solo dígitos.")
    if not result["Direccion"] or any(c in result["Direccion"] for c in "|\r\n"):
        raise ValueError("La dirección no puede estar vacía ni contener separadores o saltos de línea.")
    if not result["CodigoPostal"].isdigit() or len(result["CodigoPostal"]) != 6:
        raise ValueError("El código postal debe contener seis dígitos.")
    return result


def read_personal_data(email):
    email = require_user(email)
    if not PERSONAL_DATA_FILE.exists():
        return None
    found = []
    with PERSONAL_DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            fields = line.rstrip("\r\n").split("|")
            if len(fields) == 8 and fields[0].strip().casefold() == email:
                found.append(dict(zip(
                    ("Correo", "Nombre", "Apellidos", "Telefono", "TipoDocumento",
                     "NumeroDocumento", "Direccion", "CodigoPostal"), fields
                )))
    return found[-1] if found else None


def _replace_personal_lines(lines):
    descriptor, temp_name = tempfile.mkstemp(
        prefix=".datos_personales_", suffix=".tmp", dir=DATA_DIR
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as file:
            file.writelines(lines)
        os.replace(temp_name, PERSONAL_DATA_FILE)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def save_personal_data(email, data):
    email = require_user(email)
    data = validate_personal_data(data)
    lines = []
    if PERSONAL_DATA_FILE.exists():
        with PERSONAL_DATA_FILE.open("r", encoding="utf-8", newline="") as file:
            for line in file:
                owner = line.rstrip("\r\n").split("|", 1)[0].strip().casefold()
                if owner != email:
                    lines.append(line if line.endswith(("\n", "\r")) else line + "\n")
    lines.append("|".join((email, *(data[key] for key in (
        "Nombre", "Apellidos", "Telefono", "TipoDocumento", "NumeroDocumento",
        "Direccion", "CodigoPostal"
    )))) + "\n")
    _replace_personal_lines(lines)
    return read_personal_data(email)


def delete_personal_data(email):
    email = require_user(email)
    if not PERSONAL_DATA_FILE.exists():
        return False
    lines, removed = [], False
    with PERSONAL_DATA_FILE.open("r", encoding="utf-8", newline="") as file:
        for line in file:
            owner = line.rstrip("\r\n").split("|", 1)[0].strip().casefold()
            if owner == email:
                removed = True
            else:
                lines.append(line if line.endswith(("\n", "\r")) else line + "\n")
    if removed:
        _replace_personal_lines(lines)
    return removed
