"""Lectura, validación y filtrado de los dos inventarios Excel."""

import math
import os
import tempfile
import pandas as pd
from .rutas import (
    CLOTHING_FILE, SUITS_FILE, AVAILABILITY_FILE, DATA_DIR,
)

PRODUCT_COLUMNS = ["Codigo", "Nombre", "Seccion", "Tipo", "Precio", "Estado"]
STOCK_COLUMNS = ["Codigo", "Talla", "Cantidad"]


def create_empty_clothing_workbook():
    """Crea solo la plantilla vacía, y únicamente cuando el catálogo la necesita."""
    if CLOTHING_FILE.exists():
        return False
    with pd.ExcelWriter(CLOTHING_FILE, engine="openpyxl") as writer:
        pd.DataFrame(columns=PRODUCT_COLUMNS).to_excel(
            writer, sheet_name="Productos", index=False
        )
        pd.DataFrame(columns=STOCK_COLUMNS).to_excel(
            writer, sheet_name="Existencias", index=False
        )
    return True


def validate_inventory(products, stock):
    missing_products = [c for c in PRODUCT_COLUMNS if c not in products.columns]
    missing_stock = [c for c in STOCK_COLUMNS if c not in stock.columns]
    if missing_products or missing_stock:
        raise ValueError("ropa.xlsx no tiene los encabezados requeridos en ambas hojas.")
    products = products[PRODUCT_COLUMNS].dropna(how="all").copy()
    stock = stock[STOCK_COLUMNS].dropna(how="all").copy()
    for col in ("Codigo", "Nombre", "Seccion", "Tipo", "Estado"):
        products[col] = products[col].fillna("").astype(str).str.strip()
    products["_key"] = products["Codigo"].str.casefold()
    if (products["_key"] == "").any() or products["_key"].duplicated().any():
        raise ValueError("Cada producto debe tener un código único.")
    for col in ("Codigo", "Nombre", "Seccion", "Tipo"):
        if products[col].str.contains(r"[|\r\n]", regex=True).any():
            raise ValueError(f"{col} no puede contener | ni saltos de línea.")
    if (products["Nombre"] == "").any() or (products["Tipo"] == "").any():
        raise ValueError("Cada producto debe tener nombre y categoría.")
    sections = {"mujer": "Mujer", "hombre": "Hombre", "unisex": "Unisex"}
    products["Seccion"] = products["Seccion"].str.casefold().map(sections)
    states = {"activo": "Activo", "inactivo": "Inactivo"}
    products["Estado"] = products["Estado"].str.casefold().map(states)
    if products["Seccion"].isna().any() or products["Estado"].isna().any():
        raise ValueError("La sección o el estado de un producto no son válidos.")
    products["Precio"] = pd.to_numeric(products["Precio"], errors="coerce")
    invalid_price = products["Precio"].map(
        lambda x: pd.isna(x) or not math.isfinite(float(x)) or x < 0
    )
    if invalid_price.any():
        raise ValueError("El precio debe ser un número igual o mayor que cero.")

    for col in ("Codigo", "Talla"):
        stock[col] = stock[col].fillna("").astype(str).str.strip()
    for col in ("Codigo", "Talla"):
        if stock[col].str.contains(r"[|\r\n]", regex=True).any():
            raise ValueError(f"{col} no puede contener | ni saltos de línea.")
    stock["_code_key"] = stock["Codigo"].str.casefold()
    stock["_size_key"] = stock["Talla"].str.casefold()
    if (stock["_code_key"] == "").any() or (stock["_size_key"] == "").any():
        raise ValueError("Cada existencia debe tener código y talla.")
    if stock.duplicated(["_code_key", "_size_key"]).any():
        raise ValueError("La combinación de código y talla debe ser única.")
    unknown = set(stock["_code_key"]) - set(products["_key"])
    if unknown:
        raise ValueError("Hay existencias asociadas a productos inexistentes.")
    stock["Cantidad"] = pd.to_numeric(stock["Cantidad"], errors="coerce")
    invalid_qty = stock["Cantidad"].map(
        lambda x: pd.isna(x) or not math.isfinite(float(x)) or x < 0 or x % 1 != 0
    )
    if invalid_qty.any():
        raise ValueError("Las cantidades deben ser enteros iguales o mayores que cero.")
    stock["Cantidad"] = stock["Cantidad"].astype(int)
    return products[PRODUCT_COLUMNS].reset_index(drop=True), stock[STOCK_COLUMNS].reset_index(drop=True)


def validate_clothing_catalog(products, stock):
    products, stock = validate_inventory(products, stock)
    stock_by_code = {}
    for _, row in stock.iterrows():
        stock_by_code.setdefault(str(row["Codigo"]).casefold(), []).append({
            "Talla": row["Talla"], "Cantidad": int(row["Cantidad"]),
        })
    result = []
    for _, row in products[products["Estado"] == "Activo"].iterrows():
        sizes = stock_by_code.get(str(row["Codigo"]).casefold(), [])
        result.append({
            "Codigo": row["Codigo"], "Nombre": row["Nombre"],
            "Seccion": row["Seccion"], "Tipo": row["Tipo"],
            "Precio": float(row["Precio"]), "Tallas": sizes,
            "Disponibilidad": "Disponible" if any(s["Cantidad"] > 0 for s in sizes) else "Agotado",
        })
    return result


def load_clothing_catalog():
    if not CLOTHING_FILE.exists():
        create_empty_clothing_workbook()
    try:
        products = pd.read_excel(CLOTHING_FILE, sheet_name="Productos")
        stock = pd.read_excel(CLOTHING_FILE, sheet_name="Existencias")
    except (ValueError, OSError, ImportError) as error:
        raise ValueError("No se pudo leer ropa.xlsx o faltan sus hojas.") from error
    return validate_clothing_catalog(products, stock)


def filter_clothing_catalog(catalog, section=None, category=None):
    return [
        product for product in catalog
        if (not section or product["Seccion"].casefold() == section.casefold())
        and (not category or product["Tipo"].casefold() == category.casefold())
    ]


def load_suits():
    if not SUITS_FILE.exists():
        raise FileNotFoundError(f"No se encontró el inventario de trajes: {SUITS_FILE.name}")
    frame = pd.read_excel(SUITS_FILE)
    required = ["Codigo", "Nombre", "Tallas", "Precio", "Estado"]
    if any(col not in frame.columns for col in required):
        raise ValueError("inventario.xlsx no tiene los encabezados de trajes requeridos.")
    return [[str(row[0]), row[1], row[2], int(row[3]), row[4]] for row in frame[required].values]


def save_suits(suits):
    frame = pd.DataFrame(suits, columns=["Codigo", "Nombre", "Tallas", "Precio", "Estado"])
    descriptor, temp_name = tempfile.mkstemp(prefix=".inventario_", suffix=".xlsx", dir=DATA_DIR)
    os.close(descriptor)
    try:
        frame.to_excel(temp_name, index=False)
        os.replace(temp_name, SUITS_FILE)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def update_suit_availability():
    rows = load_suits()
    with AVAILABILITY_FILE.open("w", encoding="utf-8") as file:
        for suit in rows:
            file.write(f"{suit[0]}|{suit[1]}|{suit[4]}\n")
    return True
