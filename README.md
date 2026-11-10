# Efrata Minimall
<img width="500" height="500" alt="526696872_1297498519053003_1711582319059823326_n" src="https://github.com/user-attachments/assets/bee38036-1c73-4e82-bc53-e4d0b1e7719f" />

**Sistema de gestión de catálogo, ventas y alquiler de trajes para Efrata Minimall.**

Efrata Minimall es un negocio ubicado en Cali, Colombia, dedicado a la comercialización de prendas de vestir, alquiler de trajes para ocasiones especiales y arreglos de ropa.

Este proyecto consiste en el desarrollo de una aplicación de escritorio que busca facilitar la consulta de productos, el control de existencias, las compras y la gestión de alquileres.

## Problemática

La consulta de disponibilidad de trajes y la organización de los alquileres representan dificultades para el negocio, especialmente al momento de verificar si una prenda está disponible para determinadas fechas, registrar un alquiler y controlar su devolución.

Por esta razón, se propone una solución informática que permita centralizar estas operaciones y facilitar la consulta de la información.

## Funcionalidades principales

### Catálogo de productos
- Consulta de prendas disponibles.
- Búsqueda por nombre y código.
- Filtros de productos.
- Visualización de imágenes y descripciones.
- Consulta de existencias por talla.

### Compras
- Registro e inicio de sesión de usuarios.
- Carrito de compras independiente por usuario.
- Gestión de favoritos.
- Validación de existencias al confirmar una compra.
- Actualización del inventario.
- Generación de comprobantes.
- Consulta del historial de compras.

### Alquiler de trajes
- Consulta del catálogo de trajes.
- Verificación de disponibilidad.
- Registro de alquileres.
- Control de devoluciones.
- Confirmación de devolución.
- Actualización del estado de los trajes.

### Administración
- Consulta y modificación de inventario desde las funciones administrativas del backend y la consola.

## Tecnologías utilizadas

- **Python:** lenguaje principal de desarrollo.
- **CustomTkinter:** construcción de la interfaz gráfica.
- **Pandas:** procesamiento y manipulación de datos.
- **OpenPyXL:** lectura y escritura de archivos Excel.
- **Tkcalendar:** selección de fechas para los alquileres.
- **Pillow:** gestión y visualización de imágenes.
- **TXT y Excel:** almacenamiento local de información.

## Arquitectura del proyecto

El proyecto está organizado en módulos para separar la lógica de funcionamiento de la interfaz gráfica.

- **backend/**: contiene la lógica de negocio, gestión de usuarios, catálogo, inventario, compras y alquileres.
- **frontend/**: contiene la interfaz gráfica y los recursos visuales.
- **data/**: almacena los archivos de datos utilizados por la aplicación.
- **comprobantes/**: contiene los comprobantes generados por las operaciones.
- **main.py**: punto de entrada para ejecutar la aplicación.
- **consola.py**: permite acceder a funciones administrativas mediante la consola.

## Instalación y ejecución

### Requisitos
- Python 3.12.
- Visual Studio Code (recomendado).

### Instalar dependencias

Desde la terminal, ejecutar:

```bash
python -m pip install customtkinter pandas openpyxl pillow tkcalendar
```

### Ejecutar la aplicación

Desde la carpeta principal del proyecto:

```bash
python main.py
```

## Pruebas y validación

El proyecto fue sometido a pruebas funcionales y de integración con datos de prueba, incluyendo:

- Consulta y filtrado del catálogo.
- Gestión de existencias.
- Funcionamiento del carrito.
- Confirmación de compras y generación de comprobantes.
- Registro y devolución de alquileres.
- Validaciones de disponibilidad.

También se realizaron sesiones de validación con cuatro participantes, incluyendo personal relacionado con el negocio, para evaluar la comprensión y utilidad de la solución y recoger observaciones sobre la interfaz y los procesos.


**Integrantes:**
- Allison Castrillón Núñez
- Isabella Caro Giraldo

**Docente:** Juan Manuel Núñez Velasco.

