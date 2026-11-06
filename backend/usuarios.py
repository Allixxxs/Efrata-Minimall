"""Registro, autenticación y cierre de sesión."""

from datetime import datetime
from .rutas import USERS_FILE, LOGIN_LOG_FILE
from .sesion import current_session


def normalize_email(email):
    value = str(email or "").strip().casefold()
    if (
        not value or "|" in value or "\n" in value or "\r" in value
        or " " in value or value.count("@") != 1
    ):
        raise ValueError("El correo electrónico no tiene un formato válido.")
    local, domain = value.rsplit("@", 1)
    if not local or domain not in {"gmail.com", "hotmail.com"}:
        raise ValueError("El correo debe ser de Gmail o Hotmail.")
    return value


def validate_password(password):
    value = str(password or "")
    if (
        len(value) < 8 or not any(c.isupper() for c in value)
        or not any(c.islower() for c in value) or not any(c.isdigit() for c in value)
        or "|" in value or "\n" in value or "\r" in value
    ):
        raise ValueError("La contraseña requiere 8 caracteres, mayúscula, minúscula y número.")
    return value


def _read_users():
    if not USERS_FILE.exists():
        return {}
    users = {}
    with USERS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            fields = line.rstrip("\r\n").split("|")
            if len(fields) == 2 and fields[0].strip():
                users[fields[0].strip().casefold()] = fields[1]
    return users


def user_exists(email):
    return normalize_email(email) in _read_users()


def register_user(email, password):
    email = normalize_email(email)
    password = validate_password(password)
    if email in _read_users():
        raise ValueError("Ya existe una cuenta con ese correo.")
    with USERS_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{email}|{password}\n")
    _start_session(email, password)
    _record_login(email)
    return True


def authenticate_user(email, password):
    email = normalize_email(email)
    if _read_users().get(email) != str(password):
        return False
    _start_session(email, str(password))
    _record_login(email)
    return True


def _start_session(email, password):
    current_session.email = email
    current_session.password = password
    current_session.active = True


def _record_login(email):
    with LOGIN_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{email}|{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")


def close_session():
    current_session.email = ""
    current_session.password = ""
    current_session.active = False
