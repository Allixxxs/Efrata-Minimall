"""Preparación, confirmación e historial de compras."""

import datetime
import os
import tempfile
import uuid
from pathlib import Path
from openpyxl import load_workbook
from .rutas import (
    CLOTHING_FILE, PURCHASES_FILE, CART_FILE, RECEIPTS_DIR, DATA_DIR,
)
from .sesion import require_user
from .carrito import read_cart, validate_quantity
from .catalogo import load_clothing_catalog


def prepare_purchase(email):
    email = require_user(email)
    cart = read_cart(email)
    if not cart:
        return [], 0.0, "Tu carrito está vacío."
    catalog = load_clothing_catalog()
    details, total, errors = [], 0.0, []
    for item in cart:
        product = next((p for p in catalog if p["Codigo"].casefold() == item["Codigo"].casefold()), None)
        if product is None:
            errors.append(f"{item['Codigo']}: producto inexistente o inactivo.")
            continue
        variant = next((v for v in product["Tallas"] if v["Talla"].casefold() == item["Talla"].casefold()), None)
        if variant is None:
            errors.append(f"{item['Codigo']} talla {item['Talla']}: talla inexistente.")
            continue
        amount = validate_quantity(item["Cantidad"])
        if amount > variant["Cantidad"]:
            errors.append(f"{product['Nombre']} talla {variant['Talla']}: solicitas {amount}, hay {variant['Cantidad']}.")
            continue
        price = float(product["Precio"])
        subtotal = price * amount
        details.append({"Codigo": product["Codigo"].upper(), "Nombre": str(product["Nombre"]),
                        "Talla": variant["Talla"].upper(), "Cantidad": amount,
                        "Precio": price, "Subtotal": subtotal})
        total += subtotal
    if errors:
        return [], 0.0, "Compra cancelada; no se modificó ningún archivo. " + " ".join(errors)
    return details, total, ""


def _prepare_inventory(reductions):
    workbook = load_workbook(CLOTHING_FILE)
    try:
        if "Existencias" not in workbook.sheetnames:
            raise ValueError("No existe la hoja Existencias.")
        sheet = workbook["Existencias"]
        headers = {str(sheet.cell(1, col).value).strip(): col
                   for col in range(1, sheet.max_column + 1)
                   if sheet.cell(1, col).value is not None}
        if not {"Codigo", "Talla", "Cantidad"}.issubset(headers):
            raise ValueError("Columnas inválidas en Existencias.")
        for (code, size), amount in reductions.items():
            rows = [r for r in range(2, sheet.max_row + 1)
                    if str(sheet.cell(r, headers["Codigo"]).value).strip().upper() == code
                    and str(sheet.cell(r, headers["Talla"]).value).strip().upper() == size]
            if len(rows) != 1:
                raise ValueError(f"Variante duplicada o inexistente: {code} talla {size}.")
            row = rows[0]
            raw = sheet.cell(row, headers["Cantidad"]).value
            try:
                quantity = int(raw)
                if float(raw) != quantity or quantity < amount:
                    raise ValueError
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError(f"Existencias insuficientes o inválidas: {code} talla {size}.") from error
            sheet.cell(row, headers["Cantidad"]).value = quantity - amount
        descriptor, temp_name = tempfile.mkstemp(prefix=".ropa_pedido_", suffix=".xlsx", dir=DATA_DIR)
        os.close(descriptor)
        try:
            workbook.save(temp_name)
            return temp_name
        except Exception:
            if os.path.exists(temp_name):
                os.remove(temp_name)
            raise
    finally:
        workbook.close()


def _order_lines(order_id, email, date, details, total):
    lines = []
    for item in details:
        name = str(item["Nombre"]).replace("|", "/").replace("\r", " ").replace("\n", " ")
        lines.append("|".join((order_id, email, date, item["Codigo"], name,
                               item["Talla"], str(item["Cantidad"]),
                               f"{item['Precio']:.2f}", f"{item['Subtotal']:.2f}",
                               f"{total:.2f}", "Confirmada")) + "\n")
    return lines


def _receipt(order_id, email, date, details, total):
    lines = ["COMPROBANTE DE COMPRA - EFRATA MINI-MALL", f"Pedido: {order_id}",
             f"Fecha: {date}", f"Correo: {email}", "", "ARTÍCULOS:"]
    for item in details:
        lines.append(f"{item['Nombre']} | Código: {item['Codigo']} | Talla: {item['Talla']} | "
                     f"Cantidad: {item['Cantidad']} | Precio unitario: ${item['Precio']:,.2f} | "
                     f"Subtotal: ${item['Subtotal']:,.2f}")
    lines.extend(["", f"TOTAL: ${total:,.2f}", "Compra simulada; no se procesó ningún pago."])
    return "\n".join(lines) + "\n"


def _temp_bytes(content, prefix):
    descriptor, temp_name = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=DATA_DIR)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(content)
        return temp_name
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def _cart_without_owner(email):
    if not CART_FILE.exists():
        return b""
    lines = []
    with CART_FILE.open("r", encoding="utf-8", newline="") as file:
        for line in file:
            fields = line.rstrip("\r\n").split("|")
            own = False
            if len(fields) == 4 and fields[0].strip().casefold() == email:
                try:
                    own = int(fields[3]) > 0
                except ValueError:
                    pass
            if not own:
                lines.append(line if line.endswith(("\n", "\r")) else line + "\n")
    return "".join(lines).encode("utf-8")


def _restore(path, existed, content):
    if not existed:
        if path.exists():
            path.unlink()
        return
    descriptor, temp_name = tempfile.mkstemp(prefix=".compra_restaurar_", suffix=".tmp", dir=DATA_DIR)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(content)
        os.replace(temp_name, path)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def _new_order_id():
    while True:
        order_id = datetime.datetime.now().strftime("PED-%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8].upper()
        receipt = RECEIPTS_DIR / f"{order_id}.txt"
        used = False
        if PURCHASES_FILE.exists():
            with PURCHASES_FILE.open("r", encoding="utf-8") as file:
                used = any(line.split("|", 1)[0] == order_id for line in file)
        if not used and not receipt.exists():
            return order_id, receipt


def confirm_purchase(email, confirmed, date_time=None):
    email = require_user(email)
    details, total, error = prepare_purchase(email)
    if error:
        return {"ok": False, "message": error, "details": [], "total": 0.0}
    if not confirmed:
        return {"ok": False, "message": "Compra cancelada. El carrito y las existencias no cambiaron.",
                "details": details, "total": total}
    current_details, current_total, error = prepare_purchase(email)
    if error:
        return {"ok": False, "message": error, "details": [], "total": 0.0}
    if current_details != details or current_total != total:
        return {"ok": False, "message": "El carrito, el precio o las existencias cambiaron durante la confirmación.",
                "details": current_details, "total": current_total}
    details, total = current_details, current_total
    timestamp = date_time or datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    order_id, receipt_path = _new_order_id()
    paths = {"inventario": CLOTHING_FILE, "compras": PURCHASES_FILE, "carrito": CART_FILE}
    snapshots = {}
    try:
        for name, path in paths.items():
            snapshots[name] = (path.exists(), path.read_bytes() if path.exists() else b"")
    except OSError as error:
        return {"ok": False, "message": f"No se pudieron respaldar los archivos: {error}", "details": details, "total": total}

    temps, receipt_created = [], False
    try:
        reductions = {}
        for item in details:
            key = (item["Codigo"], item["Talla"])
            reductions[key] = reductions.get(key, 0) + item["Cantidad"]
        temp_excel = _prepare_inventory(reductions)
        temps.append(temp_excel)
        previous_orders = snapshots["compras"][1]
        if previous_orders and not previous_orders.endswith((b"\n", b"\r")):
            previous_orders += b"\n"
        temp_orders = _temp_bytes(previous_orders + "".join(
            _order_lines(order_id, email, timestamp, details, total)
        ).encode("utf-8"), ".compras_pedido_")
        temps.append(temp_orders)
        temp_cart = _temp_bytes(_cart_without_owner(email), ".carrito_pedido_")
        temps.append(temp_cart)
        RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        with receipt_path.open("x", encoding="utf-8") as file:
            receipt_created = True
            file.write(_receipt(order_id, email, timestamp, details, total))
        for key, temp_name in (("compras", temp_orders), ("inventario", temp_excel), ("carrito", temp_cart)):
            os.replace(temp_name, paths[key])
            temps.remove(temp_name)
    except Exception as error:
        restore_errors = []
        for name, path in paths.items():
            existed, content = snapshots[name]
            try:
                _restore(path, existed, content)
            except Exception as restore_error:
                restore_errors.append(f"{path.name}: {restore_error}")
        if receipt_created:
            try:
                receipt_path.unlink(missing_ok=True)
            except OSError as receipt_error:
                restore_errors.append(f"{receipt_path.name}: {receipt_error}")
        for temp_name in temps:
            try:
                Path(temp_name).unlink(missing_ok=True)
            except OSError:
                pass
        suffix = " No se pudo restaurar: " + "; ".join(restore_errors) if restore_errors else " Se restauraron los archivos anteriores."
        return {"ok": False, "message": f"No se completó la compra: {error}.{suffix}",
                "details": details, "total": total}
    return {"ok": True, "message": "Compra confirmada.", "pedido": order_id,
            "comprobante": str(receipt_path), "details": details, "total": total}


def list_purchases(email):
    email = require_user(email)
    if not PURCHASES_FILE.exists():
        return []
    orders = {}
    with PURCHASES_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            fields = line.rstrip("\r\n").split("|")
            if len(fields) != 11 or fields[1].strip().casefold() != email:
                continue
            try:
                item = {"Codigo": fields[3], "Nombre": fields[4], "Talla": fields[5],
                        "Cantidad": int(fields[6]), "Precio": float(fields[7]),
                        "Subtotal": float(fields[8]), "Estado": fields[10]}
                total = float(fields[9])
            except (ValueError, TypeError):
                continue
            order = orders.setdefault(fields[0], {"Pedido": fields[0], "Fecha": fields[2],
                                                  "Total": total, "Articulos": []})
            order["Articulos"].append(item)
    return list(orders.values())


def get_purchase_detail(email, order_id):
    email = require_user(email)
    return next((order for order in list_purchases(email)
                 if order["Pedido"].casefold() == str(order_id).strip().casefold()), None)
