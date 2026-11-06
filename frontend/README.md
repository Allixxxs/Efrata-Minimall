# Interfaz gráfica

Esta carpeta queda preparada para la futura interfaz de Isabella. Importar
`frontend` no abre ventanas ni ejecuta la consola.

La GUI debe importar operaciones de negocio desde `backend`, por ejemplo:

```python
from backend import current_session, load_clothing_catalog, add_to_cart
```

Después del inicio de sesión, la GUI usa `current_session.email` y llama a los
servicios del backend. El backend devuelve datos o resultados; la GUI presenta
formularios, tablas y mensajes. No debe volver a implementar validaciones,
precios, existencias o permisos.

Mientras se desarrolla la GUI, `main.py` inicia `consola.run_console()`. Cuando
exista `frontend.app.run`, el punto de entrada se cambia en `main.py` para
importar y llamar a esa función. La consola seguirá disponible ejecutando
`python consola.py` o mediante el modo actual de `main.py`.
