"""Inicializar los TXT locales ausentes y abrir la aplicación."""
from pathlib import Path


CONTRASENA_ADMIN_DEMO = "EfrataDemo2026!"
ARCHIVOS_OPERATIVOS = (
    "usuarios.txt", "administradores.txt", "iniciossesion.txt",
    "datos_personales.txt", "carrito.txt", "favoritos.txt",
    "compras.txt", "registraralquiler.txt",
)


def inicializar_datos(raiz=None):
    raiz = Path(raiz) if raiz is not None else Path(__file__).resolve().parent
    datos = raiz / "data"
    datos.mkdir(parents=True, exist_ok=True)
    instalacion_nueva = not any((datos / nombre).exists() for nombre in ARCHIVOS_OPERATIVOS)
    contenidos = {}
    if instalacion_nueva:
        from backend.usuarios import CORREO_ADMIN_DEMO, cifrar_contrasena
        contenidos["usuarios.txt"] = f"{CORREO_ADMIN_DEMO}|{cifrar_contrasena(CONTRASENA_ADMIN_DEMO)}\n"
        contenidos["administradores.txt"] = f"{CORREO_ADMIN_DEMO}\n"
    for nombre in ARCHIVOS_OPERATIVOS:
        try:
            with (datos / nombre).open("x", encoding="utf-8") as destino:
                destino.write(contenidos.get(nombre, ""))
        except FileExistsError:
            # Nunca sobrescribir cuentas u operaciones que ya existan.
            continue
    (raiz / "comprobantes").mkdir(exist_ok=True)


def main():
    inicializar_datos()
    from frontend.app import ejecutar_interfaz
    ejecutar_interfaz()


if __name__ == "__main__":
    main()
