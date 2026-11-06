"""Persistencia y consulta de Favoritos por usuario."""

import os
import tempfile
import pandas as pd
from .rutas import FAVORITES_FILE, DATA_DIR, CLOTHING_FILE
from .sesion import require_user
from .catalogo import load_clothing_catalog


def _records():
    if not FAVORITES_FILE.exists():
        return []
    records = []
    with FAVORITES_FILE.open("r", encoding="utf-8", newline="") as file:
        for line in file:
            fields = line.rstrip("\r\n").split("|")
            if len(fields) == 2 and all(field.strip() for field in fields):
                records.append((fields[0].strip().casefold(), fields[1].strip()))
    return records


def list_favorites(email):
    email = require_user(email)
    codes, seen = [], set()
    for owner, code in _records():
        if owner == email and code.casefold() not in seen:
            seen.add(code.casefold())
            codes.append(code)
    catalog = {item["Codigo"].casefold(): item for item in load_clothing_catalog()}
    inactive = {}
    if CLOTHING_FILE.exists():
        products = pd.read_excel(CLOTHING_FILE, sheet_name="Productos")
        if "Codigo" in products and "Estado" in products:
            for _, row in products.iterrows():
                code = str(row.get("Codigo", "")).strip()
                state = str(row.get("Estado", "")).strip().casefold()
                if code and state == "inactivo":
                    inactive[code.casefold()] = str(row.get("Nombre", ""))
    result = []
    for code in codes:
        product = catalog.get(code.casefold())
        if product:
            result.append({**product, "EstadoFavorito": "Activo"})
        elif code.casefold() in inactive:
            result.append({"Codigo": code, "Nombre": inactive[code.casefold()], "EstadoFavorito": "Inactivo"})
        else:
            result.append({"Codigo": code, "Nombre": "", "EstadoFavorito": "No encontrado"})
    return result


def _write_owner_change(lines):
    descriptor, temp_name = tempfile.mkstemp(prefix=".favoritos_", suffix=".tmp", dir=DATA_DIR)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as file:
            file.writelines(lines)
        os.replace(temp_name, FAVORITES_FILE)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def add_favorite(email, code):
    email = require_user(email)
    code = str(code).strip()
    catalog = load_clothing_catalog()
    product = next((p for p in catalog if p["Codigo"].casefold() == code.casefold()), None)
    if product is None:
        raise ValueError("El producto no existe o está inactivo.")
    lines = FAVORITES_FILE.read_text(encoding="utf-8").splitlines(keepends=True) if FAVORITES_FILE.exists() else []
    for line in lines:
        fields = line.rstrip("\r\n").split("|")
        if len(fields) == 2 and fields[0].strip().casefold() == email and fields[1].strip().casefold() == code.casefold():
            raise ValueError("Ese producto ya está en tus favoritos.")
    if lines and not lines[-1].endswith(("\n", "\r")):
        lines[-1] += "\n"
    lines.append(f"{email}|{product['Codigo']}\n")
    _write_owner_change(lines)
    return True


def remove_favorite(email, code):
    email = require_user(email)
    code = str(code).strip().casefold()
    if not FAVORITES_FILE.exists():
        return False
    lines, removed = [], False
    with FAVORITES_FILE.open("r", encoding="utf-8", newline="") as file:
        for line in file:
            fields = line.rstrip("\r\n").split("|")
            if len(fields) == 2 and fields[0].strip().casefold() == email and fields[1].strip().casefold() == code:
                removed = True
            else:
                lines.append(line)
    if removed:
        _write_owner_change(lines)
    return removed
