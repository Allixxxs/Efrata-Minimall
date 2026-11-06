"""Rutas centralizadas para el código y los datos del proyecto."""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
USERS_FILE = DATA_DIR / "usuarios.txt"
LOGIN_LOG_FILE = DATA_DIR / "iniciossesion.txt"
ADMIN_FILE = DATA_DIR / "administradores.txt"
PERSONAL_DATA_FILE = DATA_DIR / "datos_personales.txt"
SUITS_FILE = DATA_DIR / "inventario.xlsx"
RENTALS_FILE = DATA_DIR / "registraralquiler.txt"
AVAILABILITY_FILE = DATA_DIR / "consultardisponibilidad.txt"
AVAILABLE_SUITS_FILE = DATA_DIR / "trajesdisponibles.txt"
CLOTHING_FILE = DATA_DIR / "ropa.xlsx"
CART_FILE = DATA_DIR / "carrito.txt"
PURCHASES_FILE = DATA_DIR / "compras.txt"
FAVORITES_FILE = DATA_DIR / "favoritos.txt"
RECEIPTS_DIR = PROJECT_DIR / "comprobantes"