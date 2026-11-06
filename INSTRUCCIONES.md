## Ejecutar en Windows

Desde esta carpeta, abre una terminal y ejecuta:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install pandas openpyxl
python main.py
```

Para usar el menú de terminal directamente: `python consola.py`.

## Cuentas de demostración

- Cliente: `cliente.demo01@gmail.com` — contraseña: `DemoCliente1A`
- Administrador: `admin.prueba@gmail.com` — contraseña: `AdminDemo5A`

Los otros tres usuarios de prueba aparecen en `data/usuarios.txt`. La cuenta administrativa está autorizada en `data/administradores.txt`.

## Importar servicios desde la futura GUI

La GUI puede importar el API público del backend sin que se inicie el menú:

```python
from backend import current_session, authenticate_user, load_clothing_catalog
from backend import add_to_cart, get_cart_details, prepare_purchase, confirm_purchase
from backend import get_user_rentals, check_rental_conflict
```

Los nombres públicos de las operaciones se conservan. Los módulos internos están organizados en español, por ejemplo `backend.catalogo`, `backend.carrito` y `backend.alquileres`. Las funciones de consola usan `input()` y `print()`; la GUI debe llamar a los servicios de `backend` y presentar sus resultados en sus propios formularios y vistas.

Las rutas de Excel y TXT se resuelven desde esta carpeta, dentro de `data/`, aunque se ejecute Python desde otra carpeta. Los comprobantes se guardan en `comprobantes/`.
