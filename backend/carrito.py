"""Servicios del carrito; no gestionan prompts ni presentación."""

import os
import tempfile
from .rutas import CART_FILE, DATA_DIR
from .sesion import require_user
from .catalogo import load_clothing_catalog


def normalize_email(email):
    return require_user(email)


def read_cart(email):
    email = require_user(email)
    quantities = {}
    if not CART_FILE.exists():
        return []
    with CART_FILE.open("r", encoding="utf-8", newline="") as file:
        for line in file:
            fields = line.rstrip("\r\n").split("|")
            if len(fields) != 4 or fields[0].strip().casefold() != email:
                continue
            try:
                amount = int(fields[3])
            except ValueError:
                continue
            if amount <= 0:
                continue
            key = (fields[1].strip().upper(), fields[2].strip().upper())
            quantities[key] = quantities.get(key, 0) + amount
    return [{"Codigo": code, "Talla": size, "Cantidad": amount}
            for (code, size), amount in quantities.items()]


def validate_quantity(amount):
    try:
        value = float(amount)
        integer = int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("La cantidad debe ser un número entero positivo.") from error
    if value != integer or integer <= 0:
        raise ValueError("La cantidad debe ser un número entero positivo.")
    return integer


def save_cart(email, items):
    email = require_user(email)
    preserved = []
    if CART_FILE.exists():
        with CART_FILE.open("r", encoding="utf-8", newline="") as file:
            for line in file:
                fields = line.rstrip("\r\n").split("|")
                own_valid_line = False
                if len(fields) == 4:
                    try:
                        own_valid_line = fields[0].strip().casefold() == email and int(fields[3]) > 0
                    except ValueError:
                        pass
                if not own_valid_line:
                    preserved.append(line if line.endswith(("\n", "\r")) else line + "\n")
    for item in items:
        amount = int(item["Cantidad"])
        if amount > 0:
            code, size = item["Codigo"].strip().upper(), item["Talla"].strip().upper()
            if any(char in value for value in (code, size) for char in "|\r\n"):
                raise ValueError("El código y la talla no pueden contener separadores.")
            preserved.append(f"{email}|{code}|{size}|{amount}\n")
    descriptor, temp_name = tempfile.mkstemp(prefix=".carrito_", suffix=".tmp", dir=DATA_DIR)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as file:
            file.writelines(preserved)
        os.replace(temp_name, CART_FILE)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def get_variant(catalog, code, size):
    code, size = str(code).strip().upper(), str(size).strip().upper()
    for product in catalog:
        if product["Codigo"].strip().upper() == code:
            for variant in product["Tallas"]:
                if variant["Talla"].strip().upper() == size:
                    return product, variant
            return product, None
    return None, None


def add_to_cart(email, code, size, amount, catalog=None):
    email, amount = require_user(email), validate_quantity(amount)
    catalog = load_clothing_catalog() if catalog is None else catalog
    product, variant = get_variant(catalog, code, size)
    if product is None:
        raise ValueError("El producto no existe o está inactivo.")
    if variant is None:
        raise ValueError("La talla no está disponible para este producto.")
    items = read_cart(email)
    code, size = product["Codigo"].strip().upper(), variant["Talla"].strip().upper()
    current = next((x for x in items if x["Codigo"] == code and x["Talla"] == size), None)
    new_amount = (current["Cantidad"] if current else 0) + amount
    if new_amount > variant["Cantidad"]:
        raise ValueError(f"Solo hay {variant['Cantidad']} unidades disponibles de {product['Nombre']} talla {size}.")
    if current:
        current["Cantidad"] = new_amount
    else:
        items.append({"Codigo": code, "Talla": size, "Cantidad": new_amount})
    save_cart(email, items)
    return new_amount


def update_cart_quantity(email, code, size, amount, catalog=None):
    email, amount = require_user(email), validate_quantity(amount)
    catalog = load_clothing_catalog() if catalog is None else catalog
    product, variant = get_variant(catalog, code, size)
    if product is None:
        raise ValueError("El producto no existe o está inactivo.")
    if variant is None:
        raise ValueError("La talla no está disponible para este producto.")
    if amount > variant["Cantidad"]:
        raise ValueError(f"Solo hay {variant['Cantidad']} unidades disponibles de {product['Nombre']} talla {variant['Talla']}.")
    items = read_cart(email)
    item = next((x for x in items if x["Codigo"] == product["Codigo"].upper()
                 and x["Talla"] == variant["Talla"].upper()), None)
    if item is None:
        raise ValueError("Esa variante no está en tu carrito.")
    item["Cantidad"] = amount
    save_cart(email, items)
    return amount


def remove_from_cart(email, code, size):
    email = require_user(email)
    key = (str(code).strip().upper(), str(size).strip().upper())
    items = read_cart(email)
    remaining = [x for x in items if (x["Codigo"], x["Talla"]) != key]
    if len(remaining) == len(items):
        return False
    save_cart(email, remaining)
    return True


def get_cart_details(email, catalog=None):
    email = require_user(email)
    catalog = load_clothing_catalog() if catalog is None else catalog
    details = []
    for item in read_cart(email):
        product, variant = get_variant(catalog, item["Codigo"], item["Talla"])
        if product is None:
            details.append({**item, "Nombre": "Producto no disponible", "Precio": None,
                            "Subtotal": None, "StockActual": None,
                            "Aviso": "El producto ya no está activo o no existe en el catálogo."})
        elif variant is None:
            details.append({**item, "Nombre": product["Nombre"], "Precio": product["Precio"],
                            "Subtotal": product["Precio"] * item["Cantidad"], "StockActual": 0,
                            "Aviso": "La talla ya no está registrada en el inventario."})
        else:
            stock = variant["Cantidad"]
            notice = (f"La existencia cambió: quedan {stock} unidades. El artículo se conserva en el carrito."
                      if item["Cantidad"] > stock else "")
            details.append({**item, "Nombre": product["Nombre"], "Precio": product["Precio"],
                            "Subtotal": product["Precio"] * item["Cantidad"], "StockActual": stock,
                            "Aviso": notice})
    return details
