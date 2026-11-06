"""Servicios de registro, consulta, disponibilidad y devolución de trajes."""

import datetime
import os
import tempfile
import uuid
from .rutas import RENTALS_FILE, DATA_DIR
from .catalogo import load_suits
from .sesion import require_user


def _parse_line(line):
    fields = line.rstrip("\r\n").split("|")
    return fields if len(fields) in {8, 10} else None


def _date(value):
    return datetime.datetime.strptime(str(value), "%d/%m/%Y").date()


def check_rental_conflict(code, size, start, end):
    if not RENTALS_FILE.exists():
        return False
    start = _date(start) if isinstance(start, str) else start
    end = _date(end) if isinstance(end, str) else end
    if isinstance(start, datetime.datetime):
        start = start.date()
    if isinstance(end, datetime.datetime):
        end = end.date()
    with RENTALS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            fields = _parse_line(line)
            if fields is None or fields[1] != str(code).strip():
                continue
            if fields[3].strip().casefold() != str(size).strip().casefold():
                continue
            try:
                existing_start, programmed_return = _date(fields[4]), _date(fields[5])
            except ValueError:
                continue
            occupied_through = programmed_return + datetime.timedelta(days=2)
            if start <= occupied_through and end >= existing_start:
                return True
    return False


def get_user_rentals(email):
    email = require_user(email)
    if not RENTALS_FILE.exists():
        return []
    rentals = []
    with RENTALS_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file):
            fields = _parse_line(line)
            if fields and fields[0].strip().casefold() == email:
                rentals.append({
                    "Correo": email, "Codigo": fields[1], "Nombre": fields[2],
                    "Talla": fields[3], "FechaAlquiler": fields[4],
                    "FechaProgramada": fields[5], "Estado": fields[6],
                    "Precio": fields[7],
                    "Id": fields[8] if len(fields) == 10 else "",
                    "FechaReal": fields[9] if len(fields) == 10 else "",
                    "IndiceArchivo": line_number,
                })
    return rentals


def register_rental(email, code, size, start, programmed_return):
    email = require_user(email)
    code, size = str(code).strip(), str(size).strip().upper()
    start_date, return_date = _date(start), _date(programmed_return)
    if start_date < datetime.date.today():
        raise ValueError("La fecha de alquiler no puede ser anterior a hoy.")
    if return_date <= start_date:
        raise ValueError("La devolución debe ser posterior al alquiler.")
    suit = next((item for item in load_suits() if item[0] == code), None)
    if suit is None:
        raise ValueError("No se encontró el traje solicitado.")
    sizes = {value.strip().upper() for value in str(suit[2]).split(",")}
    if size not in sizes:
        raise ValueError("La talla no está disponible para este traje.")
    if check_rental_conflict(code, size, start_date, return_date):
        raise ValueError("Esta talla ya tiene un alquiler o revisión que se cruza con esas fechas.")
    rental_id = str(uuid.uuid4())
    if RENTALS_FILE.exists() and RENTALS_FILE.stat().st_size:
        with RENTALS_FILE.open("rb") as existing:
            existing.seek(-1, os.SEEK_END)
            if existing.read(1) not in {b"\n", b"\r"}:
                with RENTALS_FILE.open("a", encoding="utf-8") as file:
                    file.write("\n")
    with RENTALS_FILE.open("a", encoding="utf-8") as file:
        file.write(
            f"{email}|{code}|{suit[1]}|{size}|{start_date.strftime('%d/%m/%Y')}|"
            f"{return_date.strftime('%d/%m/%Y')}|Activo|{suit[3]}|{rental_id}|\n"
        )
    return {
        "Correo": email, "Codigo": code, "Nombre": suit[1], "Talla": size,
        "FechaAlquiler": start_date.strftime("%d/%m/%Y"),
        "FechaProgramada": return_date.strftime("%d/%m/%Y"),
        "Estado": "Activo", "Precio": suit[3], "Id": rental_id, "FechaReal": "",
    }


def return_rental(email, rental_token):
    email = require_user(email)
    if not RENTALS_FILE.exists():
        raise ValueError("No hay alquileres registrados.")
    with RENTALS_FILE.open("r", encoding="utf-8", newline="") as file:
        lines = file.readlines()
    rentals = get_user_rentals(email)
    active = [r for r in rentals if r["Estado"].strip().casefold() == "activo"]
    selected = next((r for r in active if str(r["IndiceArchivo"]) == str(rental_token)
                     or (r["Id"] and r["Id"].casefold() == str(rental_token).casefold())), None)
    if selected is None:
        raise ValueError("No se encontró un alquiler activo de esta cuenta.")
    fields = _parse_line(lines[selected["IndiceArchivo"]])
    today = datetime.date.today().strftime("%d/%m/%Y")
    fields[6] = "Devuelto"
    if len(fields) == 8:
        fields.extend([str(uuid.uuid4()), today])
    else:
        if not fields[8].strip():
            fields[8] = str(uuid.uuid4())
        fields[9] = today
    lines[selected["IndiceArchivo"]] = "|".join(fields) + "\n"
    descriptor, temp_name = tempfile.mkstemp(
        prefix=".alquiler_devolucion_", suffix=".tmp", dir=DATA_DIR
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as file:
            file.writelines(lines)
        os.replace(temp_name, RENTALS_FILE)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise
    selected.update({"Estado": "Devuelto", "FechaReal": today, "Id": fields[8]})
    return selected
