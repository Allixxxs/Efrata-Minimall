"""Operaciones protegidas de administración del inventario de ropa."""

import os
import tempfile
import pandas as pd
from .rutas import ADMIN_FILE, CLOTHING_FILE, DATA_DIR
from .sesion import current_session
from .catalogo import validate_inventory


def is_administrator(email):
    if not current_session.active or not current_session.email or email is None:
        return False
    normalized = str(email).strip().casefold()
    if normalized != current_session.email.casefold() or not ADMIN_FILE.exists():
        return False
    with ADMIN_FILE.open("r", encoding="utf-8") as file:
        authorized = {line.strip().casefold() for line in file
                      if line.strip() and not line.lstrip().startswith("#")}
    return normalized in authorized


def _require_admin():
    if not is_administrator(current_session.email):
        raise PermissionError("Esta operación requiere una sesión administrativa autorizada.")


def load_admin_inventory():
    _require_admin()
    if not CLOTHING_FILE.exists():
        raise FileNotFoundError("No se encontró ropa.xlsx.")
    try:
        products = pd.read_excel(CLOTHING_FILE, sheet_name="Productos")
        stock = pd.read_excel(CLOTHING_FILE, sheet_name="Existencias")
    except (ValueError, OSError, ImportError) as error:
        raise ValueError("No se pudo leer ropa.xlsx o faltan sus hojas.") from error
    return validate_inventory(products, stock)


def save_admin_inventory(products, stock):
    _require_admin()
    products, stock = validate_inventory(products, stock)
    if not CLOTHING_FILE.exists():
        raise FileNotFoundError("No se encontró ropa.xlsx.")
    descriptor, temp_name = tempfile.mkstemp(prefix=".ropa_admin_", suffix=".xlsx", dir=DATA_DIR)
    os.close(descriptor)
    try:
        with pd.ExcelWriter(temp_name, engine="openpyxl") as writer:
            products.to_excel(writer, sheet_name="Productos", index=False)
            stock.to_excel(writer, sheet_name="Existencias", index=False)
        os.replace(temp_name, CLOTHING_FILE)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def register_product(code, name, section, category, price):
    _require_admin()
    products, stock = load_admin_inventory()
    code, name, category = str(code).strip(), str(name).strip(), str(category).strip()
    if not code or not name or not category:
        raise ValueError("Código, nombre y categoría son obligatorios.")
    if products["Codigo"].str.casefold().eq(code.casefold()).any():
        raise ValueError("El código del producto ya está registrado.")
    row = pd.DataFrame([{"Codigo": code, "Nombre": name, "Seccion": str(section).strip(),
                         "Tipo": category, "Precio": _validate_price(price), "Estado": "Activo"}])
    save_admin_inventory(pd.concat([products, row], ignore_index=True), stock)
    return True


def _validate_price(price):
    try:
        result = float(price)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("El precio debe ser numérico.") from error
    if not pd.notna(result) or result < 0 or result in (float("inf"), float("-inf")):
        raise ValueError("El precio debe ser un número igual o mayor que cero.")
    return result


def _validate_quantity(quantity):
    try:
        value = float(quantity)
        integer = int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("La cantidad debe ser un entero igual o mayor que cero.") from error
    if value != integer or integer < 0:
        raise ValueError("La cantidad debe ser un entero igual o mayor que cero.")
    return integer


def update_product(code, name=None, section=None, category=None, price=None):
    _require_admin()
    products, stock = load_admin_inventory()
    key = str(code).strip().casefold()
    rows = products.index[products["Codigo"].str.casefold() == key]
    if len(rows) != 1:
        raise ValueError("No se encontró el código del producto.")
    index = rows[0]
    for field, value in (("Nombre", name), ("Seccion", section), ("Tipo", category)):
        if value is not None:
            products.loc[index, field] = str(value).strip()
    if price is not None:
        products.loc[index, "Precio"] = _validate_price(price)
    save_admin_inventory(products, stock)
    return True


def add_stock_variant(code, size, quantity):
    _require_admin()
    products, stock = load_admin_inventory()
    code, size = str(code).strip(), str(size).strip()
    if not products["Codigo"].str.casefold().eq(code.casefold()).any():
        raise ValueError("No existe un producto con ese código.")
    duplicate = (
        stock["Codigo"].str.casefold().eq(code.casefold())
        & stock["Talla"].str.casefold().eq(size.casefold())
    )
    if duplicate.any():
        raise ValueError("Esa talla ya está registrada.")
    addition = pd.DataFrame([{"Codigo": code, "Talla": size,
                              "Cantidad": _validate_quantity(quantity)}])
    save_admin_inventory(products, pd.concat([stock, addition], ignore_index=True))
    return True


def update_stock(code, size, quantity):
    _require_admin()
    products, stock = load_admin_inventory()
    mask = stock["Codigo"].str.casefold().eq(str(code).strip().casefold()) & stock["Talla"].str.casefold().eq(str(size).strip().casefold())
    indices = stock.index[mask]
    if len(indices) != 1:
        raise ValueError("No existe esa combinación de producto y talla.")
    stock.loc[indices[0], "Cantidad"] = _validate_quantity(quantity)
    save_admin_inventory(products, stock)
    return True


def deactivate_product(code):
    _require_admin()
    products, stock = load_admin_inventory()
    indices = products.index[products["Codigo"].str.casefold() == str(code).strip().casefold()]
    if len(indices) != 1:
        raise ValueError("No se encontró el código del producto.")
    products.loc[indices[0], "Estado"] = "Inactivo"
    save_admin_inventory(products, stock)
    return True
