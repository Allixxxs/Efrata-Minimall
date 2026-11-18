"""Crear los TXT locales ausentes a partir de plantillas públicas vacías."""
from pathlib import Path


def inicializar_datos(raiz=None):
    raiz = Path(raiz) if raiz is not None else Path(__file__).resolve().parent
    datos = raiz / "data"
    plantillas = datos / "plantillas"
    datos.mkdir(parents=True, exist_ok=True)
    for plantilla in sorted(plantillas.glob("*.txt")):
        try:
            with (datos / plantilla.name).open("xb") as destino:
                destino.write(plantilla.read_bytes())
        except FileExistsError:
            # Nunca sobrescribir cuentas u operaciones que ya existan.
            continue
    (raiz / "comprobantes").mkdir(exist_ok=True)


if __name__ == "__main__":
    inicializar_datos()
