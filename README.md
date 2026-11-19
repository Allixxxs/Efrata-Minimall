# Efrata Minimall

**Aplicación de escritorio para consultar ropa, realizar compras y gestionar alquileres de trajes.**

Proyecto académico de la **Universidad Autónoma de Occidente**, desarrollado para la asignatura **Algoritmia y Programación**. Está construido en Python, con una interfaz gráfica para clientes y administradores y almacenamiento local en archivos TXT y Excel.


## Contenido

- [Catálogo y fotografías](#catálogo-de-demostración-y-fotografías).
- [Instalación y ejecución](#instalación-y-ejecución-en-windows).
- [Acceso de administrador](#acceso-de-administrador).
- [Validación con usuarios y mejoras](#validación-con-usuarios-y-mejoras).
- [Pruebas técnicas y correcciones](#pruebas-técnicas-y-correcciones).
- [Ampliación del catálogo](#ampliacion-catalogo).
- [Sustitución de fotografías y logotipo](#sustitucion-fotografias).
- [Registro completo de las 24 fotografías](#registro-fotografias).
- [Detalle de los 31 casos originales](#informe-tecnico-31).
- [Registro de ejecución de 31 pruebas](#registro-31-pruebas).
- [Registro final de 32 pruebas](#registro-32-pruebas).

## Contexto y problema

Efrata Minimall es un negocio de Cali, Colombia, dedicado a la venta de ropa, el alquiler de trajes y los arreglos de prendas. Para atender una compra o un alquiler es necesario consultar productos, tallas, existencias, información de contacto y, en el caso de los trajes, fechas de entrega y devolución.

Cuando esa información se consulta por separado, resulta más difícil conocer la disponibilidad y hacer seguimiento a cada operación. Por eso, este proyecto reúne las funciones principales en una aplicación: los **clientes** pueden explorar el catálogo y registrar compras o alquileres, mientras que los **administradores** pueden gestionar el inventario y consultar los movimientos del negocio.

La aplicación se centra en las ventas y los alquileres. Aunque el negocio también ofrece arreglos de ropa, ese servicio no está automatizado en esta versión.

## Objetivos y alcance

### Objetivo general

Desarrollar una aplicación de escritorio en Python que facilite la consulta de productos y la gestión de compras, alquileres e inventario de Efrata Minimall mediante una interfaz gráfica, validaciones y registros locales.

### Objetivos específicos

- Organizar la solución en módulos de usuarios, catálogo, carrito, compras, alquileres y administración.
- Permitir la consulta de prendas, tallas, precios y existencias antes de comprar.
- Verificar los datos personales necesarios para registrar compras y alquileres.
- Controlar la disponibilidad de los trajes según su talla y las fechas solicitadas.
- Conservar los registros de operaciones y los métodos de pago elegidos para su consulta posterior.
- Comprobar las funciones principales mediante pruebas con información ficticia.

### Funcionalidades priorizadas

El producto mínimo viable (MVP) se concentra en cuatro procesos: **acceso de usuarios, consulta del catálogo, compras con control de inventario y alquiler de trajes con verificación de fechas**. El carrito persistente, el historial, los comprobantes y el panel administrativo complementan esos procesos para permitir su seguimiento.

Esta versión funciona de forma **local en Windows**; no requiere servidor ni conexión con una plataforma de pagos. No está diseñada para operar simultáneamente desde varios computadores.

## Requisitos y criterios de aceptación

Cada requisito se relaciona con una condición observable y con los módulos donde se implementa. Estos criterios también sirven como guía para las pruebas y la sustentación.

| Requisito | ¿Cómo se comprueba? | Módulos principales |
| --- | --- | --- |
| Acceso de usuarios | Se registra una cuenta válida, se inicia sesión y las operaciones quedan asociadas al usuario correspondiente. | `backend/usuarios.py`, `backend/sesion.py` |
| Perfil obligatorio | No se confirma una compra ni un alquiler si falta alguno de los siete datos personales exigidos. | `backend/datos_personales.py`, `backend/compras.py`, `backend/alquileres.py` |
| Catálogo de ropa | Se pueden consultar productos y buscar o filtrar por las opciones disponibles en la interfaz. | `backend/catalogo.py`, `frontend/app.py` |
| Carrito persistente | Los artículos se conservan al cerrar sesión y desaparecen al comprarlos o eliminarlos manualmente. | `backend/carrito.py`, `backend/usuarios.py` |
| Compra e inventario | Se rechazan cantidades sin existencias; una compra confirmada registra el pedido, descuenta unidades, genera comprobante y actualiza el carrito. | `backend/compras.py` |
| Cancelación de compra | Cancelar antes de confirmar no altera el carrito ni el inventario. | `backend/compras.py` |
| Disponibilidad de trajes | Se validan estado, talla, fecha de inicio no anterior a hoy y fecha de devolución posterior; se rechazan cruces con otros alquileres y el margen de revisión de dos días. | `backend/alquileres.py` |
| Devoluciones | El cliente registra una devolución válida y el alquiler conserva su historial. | `backend/alquileres.py` |
| Métodos de pago | Se guarda el método y el estado del pago; los formularios de tarjeta rechazan datos incompletos o inválidos. | `backend/compras.py`, `backend/alquileres.py`, `frontend/app.py` |
| Administración | Solo las cuentas autorizadas pueden acceder a las funciones administrativas. | `backend/administracion.py` |

## Funcionalidades

### Clientes

- **Cuentas:** registro, inicio y cierre de sesión. El registro admite correos de Gmail o Hotmail (con la excepción reservada de la cuenta de demostración) y contraseñas de al menos ocho caracteres, con mayúscula, minúscula y número.
- **Datos personales:** consulta y actualización del perfil. Para comprar o alquilar se requieren nombre, apellidos, teléfono, tipo y número de documento, dirección y código postal.
- **Catálogo:** fotografías, descripciones, precios, tallas, búsquedas y filtros. La colección de demostración contiene **14 prendas registradas (13 activas)** y **10 trajes de alquiler**.
- **Favoritos y carrito:** artículos asociados a cada cuenta, con posibilidad de cambiar cantidades o eliminarlos. El carrito se conserva entre sesiones.
- **Compras:** validación de existencias, registro de pedidos, comprobantes TXT e historial de compras.
- **Alquileres:** consulta de trajes disponibles, selección de talla y fechas, registro de alquileres e historial de devoluciones.

### Administradores

- Panel principal con indicadores generales.
- Registro, edición y desactivación de prendas y trajes, con precios, descripciones, fotografías, tallas y existencias.
- Consulta de compras, artículos, totales y métodos de pago.
- Seguimiento de alquileres y consulta de las devoluciones realizadas.
- Consulta de información de clientes y estadísticas del negocio.

La devolución se registra desde la cuenta del cliente; la sección administrativa permite consultar los registros correspondientes.

## Capturas de la aplicación

Las capturas reales incorporadas fueron tomadas el **17 de noviembre de 2026** y muestran la interfaz con datos de demostración. Se revisaron antes de incluirlas y no se observaron datos personales sensibles. Las fotografías de productos son referencias, no imágenes tomadas del inventario físico de Efrata Minimall.

### Catálogo de ropa

![Catálogo de ropa con buscador, filtros y productos](frontend/imagenes/catalogo-ropa.png)

### Catálogo de trajes

![Catálogo de trajes y consulta de disponibilidad por fechas](frontend/imagenes/catalogo-trajes.png)

### Formulario de alquiler

![Formulario de alquiler con selección de talla, fechas y método de pago](frontend/imagenes/formulario-alquiler.png)

### Panel administrativo

![Panel administrativo con navegación e indicadores del catálogo](frontend/imagenes/panel-administrativo.png)

### Validaciones y manejo de información

La aplicación comprueba campos obligatorios, formatos, cantidades, tallas y fechas antes de registrar operaciones. También muestra mensajes cuando una acción no puede completarse y restringe las herramientas administrativas a cuentas autorizadas. Para la demostración se utilizan datos ficticios y no se recopilan números completos de tarjetas ni códigos de seguridad bancarios.

### Métodos y estados de pago

| Método | Información solicitada | Estado registrado |
| --- | --- | --- |
| Efectivo al recibir | No requiere datos de tarjeta. | Pendiente |
| Tarjeta de crédito | Nombre del titular y últimos cuatro dígitos. | No procesado |
| Tarjeta débito | Nombre del titular y últimos cuatro dígitos. | No procesado |

Los formularios de tarjeta sirven para comprobar la interacción y las validaciones. **No solicitan información bancaria real, no guardan los datos introducidos y no realizan cargos.** El estado del pedido o del alquiler se muestra por separado del estado del pago.

## Catálogo de demostración y fotografías

La versión preparada para la presentación incluye **14 prendas registradas, 13 activas, y 10 trajes de alquiler**. En ropa hay **44 variantes de talla: 39 disponibles y 5 agotadas**. Estas cifras se comprobaron en el inventario el **17 de noviembre de 2026** y pueden cambiar al registrar operaciones.

Los productos añadidos, así como sus precios, tallas y existencias, son **datos ficticios de uso académico**; no representan cantidades ni precios confirmados por el establecimiento. Las **24 fotografías del catálogo** son referencias de Pexels, cuya procedencia y condiciones de uso se documentaron en el [registro completo de fotografías](#registro-fotografias) y en los antecedentes de [ampliación](#ampliacion-catalogo) y [sustitución](#sustitucion-fotografias) de este README. No deben interpretarse como fotografías de productos reales de la tienda.

El logotipo fue facilitado por la propietaria para el proyecto académico, según la información aportada. Sin embargo, no se dispone de documentación que confirme la autoría del diseño y las licencias de todos sus componentes ni una autorización documentada para su publicación. Sus derechos de uso siguen pendientes de confirmación; no se le atribuye la licencia de Pexels. La [revisión del logotipo](#sustitucion-fotografias) conserva los detalles de esta limitación.

## Arquitectura y almacenamiento

El proyecto está dividido en tres partes:

1. **`frontend/`:** contiene la interfaz, las imágenes y los formularios con los que interactúan los usuarios.
2. **`backend/`:** organiza las reglas de negocio, las validaciones y el acceso a los datos.
3. **`data/`:** conserva la información local para que las operaciones puedan consultarse después de cerrar la aplicación.

El recorrido general de una operación es:

```text
Cliente o administrador
        ↓
Interfaz gráfica (frontend/app.py)
        ↓
Funciones y validaciones del backend
        ↓
Archivos locales TXT / Excel
        ↓
Resultado mostrado en la interfaz
```

**Ejemplo de integración:** al confirmar una compra, el sistema verifica el perfil y las existencias, registra el pedido, actualiza el inventario, genera un comprobante y retira del carrito los artículos comprados. Si el usuario cancela antes de confirmar, el carrito y las existencias se mantienen. En los alquileres, la disponibilidad se calcula a partir del traje, la talla y los intervalos de fechas registrados.

### Estructura principal del repositorio

```text
Efrata-Minimall/
├── .gitignore
├── main.py
├── README.md
├── frontend/
│   ├── __init__.py
│   ├── app.py
│   └── imagenes/
│       ├── CL-*.jpg (14 fotografías de ropa)
│       ├── T001.jpg … T010.jpg (10 fotografías de trajes)
│       ├── efrata_logo_ui.png
│       ├── catalogo-ropa.png
│       ├── catalogo-trajes.png
│       ├── formulario-alquiler.png
│       └── panel-administrativo.png
├── backend/
│   ├── __init__.py
│   ├── rutas.py
│   ├── sesion.py
│   ├── usuarios.py
│   ├── datos_personales.py
│   ├── catalogo.py
│   ├── favoritos.py
│   ├── carrito.py
│   ├── compras.py
│   ├── alquileres.py
│   └── administracion.py
├── data/
│   ├── ropa.xlsx
│   ├── inventario.xlsx
│   ├── consultardisponibilidad.txt
│   └── trajesdisponibles.txt
└── comprobantes/
    └── .gitkeep
```

El árbol muestra los archivos públicos; el nombre de la carpeta raíz puede variar al descargar el proyecto. `ropa.xlsx` contiene las hojas **Productos** y **Existencias**; `inventario.xlsx` almacena los trajes. Al arrancar se crean, si faltan, `usuarios.txt`, `administradores.txt`, `iniciossesion.txt`, `datos_personales.txt`, `favoritos.txt`, `carrito.txt`, `compras.txt` y `registraralquiler.txt` en `data/`. Estos archivos operativos y los comprobantes son locales y están excluidos de Git. Los identificadores y correos relacionan los registros correspondientes. Toda la documentación, las atribuciones y las evidencias históricas se reúnen en este README.

## Tecnologías

| Tecnología | Uso |
| --- | --- |
| **Python 3.12** | Lenguaje principal; la revisión se realizó con Python 3.12.10. |
| **CustomTkinter y Tkinter** | Ventanas, navegación, controles y mensajes. |
| **pandas** | Consulta y organización de información tabular. |
| **openpyxl** | Lectura y actualización de libros Excel. |
| **Pillow** | Carga y adaptación de fotografías. |
| **tkcalendar** | Selección de fechas en los alquileres. |
| **TXT y Excel** | Persistencia local de usuarios, productos y operaciones. |

### Datos iniciales y privacidad de la descarga pública

Los inventarios Excel y las fotografías se incluyen completos. Los ocho TXT operativos se crean directamente al ejecutar `python main.py` si faltan, sin archivos de plantilla. En una instalación totalmente nueva se configura la cuenta administrativa pública de demostración en los TXT de usuarios y administradores; los otros seis TXT quedan vacíos. La inicialización integrada en `main.py` solo crea archivos ausentes: nunca sobrescribe datos existentes. Los nombres y formatos TXT utilizados por el backend se conservan.

Los TXT operativos y los comprobantes generados están excluidos por `.gitignore`. La descarga no contiene registros privados: la cuenta pública de demostración se genera localmente en el primer arranque. Los clientes pueden registrar su propia cuenta; ese registro no concede permisos administrativos. Los TXT de usuarios y administradores no deben publicarse. Los comprobantes se guardan en `comprobantes/` únicamente de forma local.

## Instalación y ejecución en Windows

**Requisito previo:** tener instalado Python 3.12, con Tkinter disponible. No es necesario utilizar Visual Studio Code. Git es opcional si se descarga el archivo ZIP del repositorio.

1. En GitHub, seleccionar **Code → Download ZIP** y extraer el contenido. También puede utilizarse **Code** para copiar la URL y clonar el repositorio con Git.
2. Abrir PowerShell en la carpeta donde se encuentra `main.py`.
3. Crear un entorno virtual:

   ```powershell
   python -m venv .venv
   ```

4. Instalar las librerías necesarias dentro del entorno:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install customtkinter pandas openpyxl Pillow tkcalendar
   ```

5. Ejecutar la aplicación:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

Estos comandos no requieren activar el entorno virtual ni modificar la política de ejecución de PowerShell. Si se prefiere usar la instalación de Python que ya está configurada en el equipo, también puede ejecutarse `python main.py` después de instalar las dependencias correspondientes.

**Importante:** mantener las carpetas `backend/`, `frontend/`, `data/` y las fotografías en su ubicación original. Para las pruebas o demostraciones, utilizar una copia de trabajo y datos ficticios, especialmente si ya existen operaciones registradas.

## Guía de uso

### Como cliente

1. Registrarse o iniciar sesión. En **Mis datos**, completar y guardar los siete campos obligatorios.
2. Entrar en **Buscar ropa**, utilizar los filtros, elegir un producto y seleccionar una talla disponible.
3. Agregar productos a **Favoritos** o **Ver carrito** y ajustar las cantidades.
4. Seleccionar un método de pago, confirmar la compra y consultar **Mis compras** y el comprobante generado.
5. Entrar en **Alquilar trajes**, consultar tallas y fechas disponibles y registrar el alquiler.
6. En **Consultar alquileres**, revisar el historial y registrar la devolución cuando corresponda.

En ventanas pequeñas, puede ser necesario desplazar el menú hasta abajo para acceder a **Cerrar sesión**.

## Acceso de administrador

En una descarga nueva, ejecutar `python main.py` y utilizar estos datos en el formulario de inicio de sesión:

| Dato | Credencial pública de demostración |
| --- | --- |
| Correo / identificador | `admin@efrata.invalid` |
| Contraseña | `EfrataDemo2026!` |

El dominio `.invalid` está reservado para identificadores no reales: no es un buzón de correo ni corresponde a una cuenta personal. La validación admite únicamente este identificador como excepción a Gmail y Hotmail; no se habilitan otros correos de ese dominio.

`main.py` crea esta cuenta **solo cuando no existe ninguno de los ocho TXT operativos**. Guarda la contraseña con el mismo PBKDF2-SHA256 y sal aleatoria que las demás cuentas y añade únicamente su identificador a `administradores.txt`. No depende de los registros privados del equipo original. Si ya existe cualquier TXT operativo, solo crea los que faltan vacíos, sin añadir la cuenta de demostración ni cambiar las cuentas o permisos existentes. Una instalación anterior conserva su acceso administrativo local.

No se duplica ni restablece la cuenta al reiniciar. Registrar una cuenta normal no le concede permisos de administrador. Estas credenciales son públicas **exclusivamente para probar la aplicación académica**: deben cambiarse o deshabilitarse antes de cualquier uso fuera de ese entorno. Para deshabilitar su acceso administrativo, retirar localmente su línea de `data/administradores.txt`; mientras se conserve algún TXT operativo, la inicialización no volverá a concederle permisos. Nunca reutilizar contraseñas personales.

### Comprobación del acceso de demostración

La revisión del 18 de noviembre de 2026 utilizó exclusivamente una copia temporal de los archivos públicos actuales, sin TXT operativos privados ni plantillas. No se presenta como una nueva ejecución de las 32 pruebas históricas retiradas.

| Caso | Resultado esperado | Resultado obtenido |
| --- | --- | --- |
| Primera inicialización | Ocho TXT operativos; solo usuarios y administradores contienen la cuenta pública. | Comprobado: seis TXT vacíos; contraseña PBKDF2-SHA256 con sal, sin texto plano en usuarios. |
| Inicio desde el formulario | Credenciales públicas válidas y panel administrativo accesible. | Comprobado con widgets reales y consulta del inventario de 14 prendas en la copia temporal. |
| Cuenta de cliente | Inicio normal sin acceso administrativo. | Comprobado en formulario y backend; consulta administrativa rechazada. |
| Reinicio | Conservar registros sin duplicar ni restablecer cuentas. | Comprobado con inicializaciones repetidas y otro intérprete Python; únicamente se añadió el registro del nuevo acceso. |
| Instalación parcial | Conservar cualquier TXT existente; crear los ausentes vacíos sin añadir la demo. | Comprobado con cada uno de los ocho archivos existentes por separado y con usuarios vacío. |
| Deshabilitación | No restaurar permisos retirados. | Comprobado: administradores vacío se conservó al reinicializar. |
| Identificadores no admitidos | La excepción no habilita todo el dominio reservado. | Otro identificador en `.invalid` fue rechazado. |

Se invocaron los formularios con widgets Tk reales de forma programática; no se afirma una automatización visual completa mediante ratón y teclado. La advertencia conocida de fuente de CustomTkinter no impidió estas comprobaciones.

### Como administrador

1. Iniciar sesión con la cuenta pública descrita en **Acceso de administrador** en una descarga nueva, o con una cuenta local previamente autorizada. El registro público no concede permisos administrativos.
2. Abrir el **Panel administrativo** y revisar el resumen de información.
3. Consultar y, si corresponde, actualizar el inventario de prendas y trajes.
4. Revisar las secciones de compras, alquileres, devoluciones, clientes y estadísticas.

Para presentar el proyecto, utilizar cuentas de demostración autorizadas. No se deben publicar contraseñas personales ni credenciales privadas en el repositorio o en las capturas; la única excepción documentada es la cuenta pública de demostración. **Antes de hacer públicos los cambios, debe revisarse también el historial de Git**, porque eliminar datos personales de los archivos actuales no los elimina de los commits anteriores.

## Validación con usuarios y mejoras

Para evaluar la utilidad y la facilidad de uso de Efrata Minimall, realizamos actividades de campo con personas que podían utilizar el sistema como clientes o desde el negocio. En una primera etapa presentamos dos propuestas de interfaz y una versión inicial que funcionaba en la terminal. Posteriormente, recopilamos fotografías y videos de personas utilizando la aplicación gráfica.

### Participantes y desarrollo de las pruebas

En la validación inicial participaron cuatro personas con diferentes perfiles. Se les pidió explorar las opciones, buscar un traje, consultar su información y reconocer cómo realizarían un alquiler. Durante las actividades registramos sus respuestas, dificultades y sugerencias.

| Participante | Perfil | Principales observaciones |
| --- | --- | --- |
| 1 | Persona de 19 años, maquilladora profesional | Comprendió el propósito de la aplicación y consideró claras las opciones. Indicó que podía completar la tarea sin ayuda y sugirió contar con más alternativas de trajes. |
| 2 | Persona de 46 años, abogada | Encontró comprensible la información y destacó la importancia de ofrecer más opciones para alquilar. Manifestó que utilizaría una aplicación de este tipo. |
| 3 | Mujer de 38 años, empleada del negocio | Consideró útil la búsqueda de trajes, aunque algunas opciones de la versión en terminal le resultaron confusas. Recomendó una presentación más visual y descripciones más completas de las prendas. |
| 4 | Persona de 45 años, propietaria del negocio | Resaltó la importancia de organizar los alquileres y las devoluciones, y de consultar la disponibilidad de cada traje según la talla y las fechas solicitadas. |

Estas observaciones corresponden a la evaluación de los diseños y del programa inicial. Sirvieron como orientación para el desarrollo, pero no deben interpretarse como resultados de una prueba completa de la versión final.

### Evidencias del trabajo de campo

Las pruebas posteriores se documentaron con fotografías y videos en los que se observa la interacción con la aplicación gráfica. Los registros muestran recorridos por el inicio de sesión, el catálogo de productos, los formularios y la selección de fechas para alquileres.

El material se presenta de manera general, sin asignar cada fotografía a un participante. Los comentarios y las respuestas se conservan organizados por persona en el registro de validación inicial.

**[Consultar las evidencias fotográficas y audiovisuales en Google Drive](https://drive.google.com/drive/folders/1AQ-JaSVIc6e9VyRthsJdaCWF0V2aFu36?usp=sharing)**

La carpeta contiene 16 fotografías y cinco videos. Las imágenes permiten observar la participación y el uso de distintas pantallas, aunque por sí solas no demuestran que todas las tareas se hayan completado sin ayuda. El acceso al material depende de los permisos de la carpeta. Antes de difundir fotografías identificables o pantallas con información personal, se deben verificar las autorizaciones y proteger los datos visibles.

### Comentarios recibidos y cambios realizados

| Observación de los participantes | Cambio realizado |
| --- | --- |
| Algunas opciones del programa en terminal no eran fáciles de interpretar. | Se desarrolló una interfaz gráfica con botones, formularios y navegación entre pantallas. |
| Hacían falta más alternativas y una presentación más completa de los productos. | Se amplió el catálogo de demostración y se incorporaron imágenes de referencia, descripciones, tallas y precios. |
| Era importante consultar las fechas de alquiler y evitar reservas que coincidieran. | Se incorporó la verificación de disponibilidad por traje, talla y período, junto con el registro y la consulta de devoluciones. |
| Al agregar un producto al carrito o a favoritos, algunos usuarios no se daban cuenta de que la acción se había realizado. | Se añadió un mensaje en la parte inferior de la pantalla para confirmar cuando se agrega un producto al carrito o a favoritos. |

Sobre el último punto, nuestra compañera recogió comentarios de usuarios que, en general, entendían cómo navegar por la aplicación, pero no siempre notaban si el producto se había guardado en el carrito o en favoritos. Después de incorporar los mensajes de confirmación, **ella misma comprobó que los avisos aparecían y se visualizaban correctamente**.

Esta comprobación permitió verificar el cambio en la interfaz. No se registró una segunda sesión con los mismos usuarios para conocer su opinión sobre los nuevos mensajes; por eso, no afirmamos que el problema haya quedado validado nuevamente por ellos.

### Conclusión del trabajo de campo

Las actividades nos permitieron identificar qué información necesitaban consultar los clientes y qué funciones eran importantes para organizar los alquileres desde el negocio. También nos ayudaron a reconocer aspectos de la interfaz que podían resultar confusos y a realizar cambios durante el desarrollo.

Consideramos que Efrata Minimall ofrece una respuesta al problema planteado porque reúne en un mismo programa la consulta del catálogo, el registro de compras, la verificación de disponibilidad de trajes y el seguimiento de alquileres. Esta conclusión se apoya en las funciones implementadas, las pruebas técnicas y las observaciones recogidas durante el trabajo de campo. No supone que se hayan medido resultados comerciales del negocio.

---

## Pruebas técnicas y correcciones

Antes de simplificar la estructura, el **18 de noviembre de 2026** se ejecutaron las **32 pruebas automatizadas: 32 aprobadas, 0 fallidas, 0 errores y 0 omitidas** (`Ran 32 tests in 29.888s`, `OK`). Incluían las **7 pruebas originales del catálogo y 25 de funciones críticas y presentación**. La suite fue retirada después de esta comprobación y **ya no está incluida ni puede ejecutarse desde esta entrega**. Los resultados se conservan como evidencia histórica, no como una suite actualmente disponible.

| Área evaluada | Casos comprobados | Resultado histórico |
| --- | --- | --- |
| Catálogo e interfaz | Catálogos, existencias, fotografías, filtros, tarjetas y ampliación. | Aprobado en los siete casos originales, que también incluyen compra, alquiler y consulta administrativa. |
| Acceso y perfil | Registro válido e inválido, duplicados, contraseñas, permisos y datos personales obligatorios. | Aprobado. |
| Carrito y compras | Persistencia, separación entre usuarios, cantidades límite, stock, cancelación y comprobantes. | Aprobado. |
| Pagos | Tres métodos, estados, entradas inválidas y etiquetas compatibles con registros históricos. | Aprobado. |
| Alquileres y devoluciones | Fechas, tallas, disponibilidad, margen de revisión y devoluciones. | Aprobado. |
| Administración e integración | Consultas autorizadas, restricciones, panel y formularios con almacenamiento temporal. | Aprobado. |

La [salida completa previa a la simplificación](#registro-32-pruebas) registra los 32 resultados. El [informe técnico histórico](#informe-tecnico-31) y la [salida de la revisión anterior](#registro-31-pruebas) conservan su resultado original de **31 pruebas**. La prueba adicional fue `test_25_etiquetas_y_compatibilidad_historica`, sobre etiquetas de pagos y pedidos y lectura de estados históricos sin reescribirlos.

Se utilizaron datos ficticios, archivos temporales y comprobaciones de integridad para proteger los originales. Las revisiones documentadas también verificaron compilación de Python y `git diff --check`. Las seis regresiones más antiguas son antecedentes documentados cuya suite no está disponible; no se recuperaron ni se cuentan dentro de las 32.

Estos resultados no cubren concurrencia, fallos de disco ni automatización visual completa mediante ratón y teclado. El trabajo de campo inicial y las evidencias posteriores se describen en [Validación con usuarios y mejoras](#validación-con-usuarios-y-mejoras), con sus límites y comprobaciones pendientes.


## Archivo académico integrado

Las siguientes secciones incorporan los tres informes y los tres registros TXT de la entrega anterior. Se conservan fechas, casos, resultados y límites específicos. Las menciones de archivos retirados describen la estructura de cada revisión; no son enlaces ni instrucciones de ejecución actuales. Los registros de consola se transcriben íntegramente, sin recrear las pruebas.

**Cronología:** la ampliación y la sustitución se revisaron el 17 de noviembre de 2026 con siete pruebas. La ampliación de la suite dio lugar al informe de 31 casos y su salida del mismo día. La revisión posterior añadió el caso 25 de presentación: la última ejecución de 32 casos, del 18 de noviembre, se verificó antes de retirar la suite. No se suman ejecuciones entre sí.

**Estado actual frente a los antecedentes:** las once fotografías antiguas ya fueron sustituidas; las trece incorporadas se conservaron. El historial público se sustituyó posteriormente por el commit limpio `24ed82b`; las notas de los informes que señalan riesgos del historial describen el estado de aquella tarea. No acreditan que se hayan eliminado copias o referencias históricas externas a la rama publicada. El permiso documentado del logotipo continúa pendiente. Las expresiones «sin commits ni push» y «README intacto» se refieren solo al alcance de cada intervención antigua.

<a id="ampliacion-catalogo"></a>

### Ampliación del catálogo — 17 de noviembre de 2026

Antecedente histórico: ocho prendas y cinco trajes añadidos, tallas, existencias y corrección del diálogo de fotografía.

<details>
<summary>Ver ampliación del catálogo — 17 de noviembre de 2026</summary>

Fecha: 17 de noviembre de 2026.

### Resultado

- Ropa: 6 → 14 prendas; activas: 5 → 13. La prenda inactiva se conserva.
- Existencias de ropa: 16 → 44 variantes. Las 28 variantes nuevas tienen cantidades positivas.
- Alquiler: 5 → 10 trajes activos. Los trajes se reservan por código, talla y fechas; el modelo no maneja cantidades por talla de traje.
- Precios y existencias nuevos son ficticios, en pesos colombianos; no representan inventario confirmado del negocio.

### Respaldo y conservación

Antes de editar los Excel se guardaron y verificaron copias byte a byte en la carpeta privada `Efrata_respaldo_catalogo_20261117`, situada en Descargas y fuera del repositorio. Las filas originales de todas las hojas se compararon con esas copias y no cambiaron. Los registros de operaciones, cuentas, datos personales y comprobantes se mantuvieron intactos.

### Prendas añadidas

| Código | Prenda | Categoría / sección | Precio COP | Talla: unidades |
| --- | --- | --- | ---: | --- |
| CL-MU-004 | Blusa Alba Demo | Blusa / Mujer | 59,000 | S: 3, M: 4, L: 2 |
| CL-MU-005 | Vestido Jardín Demo | Vestido / Mujer | 115,000 | S: 2, M: 3, L: 2 |
| CL-MU-006 | Falda Aurora Demo | Falda / Mujer | 79,000 | S: 3, M: 3, L: 2 |
| CL-UNI-002 | Chaqueta Índigo Demo | Chaqueta / Unisex | 139,000 | S: 2, M: 4, L: 3, XL: 2 |
| CL-HO-003 | Camisa Nácar Demo | Camisa / Hombre | 68,000 | S: 2, M: 4, L: 3, XL: 2 |
| CL-MU-007 | Pantalón Arena Demo | Pantalón / Mujer | 95,000 | 6: 2, 8: 3, 10: 4, 12: 2 |
| CL-HO-004 | Camisa Cobalto Demo | Camisa / Hombre | 74,000 | S: 2, M: 3, L: 3, XL: 1 |
| CL-MU-008 | Chaqueta Marfil Demo | Chaqueta / Mujer | 149,000 | S: 2, M: 3, L: 2 |

### Trajes añadidos

| Código | Traje | Alquiler COP | Tallas |
| --- | --- | ---: | --- |
| T006 | Traje Azul Ceremonia Demo | 160,000 | S, M, L, XL |
| T007 | Traje Beige Balcón Demo | 145,000 | S, M, L |
| T008 | Traje Negro Ejecutivo Demo | 155,000 | M, L, XL |
| T009 | Esmoquin Gala Demo | 185,000 | S, M, L |
| T010 | Traje Gris Urbano Demo | 150,000 | S, M, L, XL |

### Fotografías y licencias

Se incorporaron trece JPEG distintos. Se verificó la indicación «Free» en las fichas de Pexels y la [licencia oficial](https://www.pexels.com/license/), que permite descargarlas, usarlas y modificarlas, con restricciones como no sugerir respaldo de las personas o marcas retratadas. Se usan exclusivamente como referencias académicas, sin atribuirles relación con el negocio. Las fotografías no son prueba de características físicas, composición ni disponibilidad de productos reales.

Se conservaron las proporciones, sin recorte, con lado mayor de 1600 píxeles, calidad JPEG 88 y sin EXIF. Peso total: 3.79 MiB. El manifiesto registro de fotografías integrado en este README registra códigos, autores, fichas originales, URL de descarga, licencia, fecha, resolución y SHA-256 de cada archivo.

| Fotografía local | Autor | Ficha original |
| --- | --- | --- |
| `frontend/imagenes/CL-MU-004.jpg` | cottonbro studio | [Pexels 7716936](https://www.pexels.com/photo/a-person-wearing-white-blouse-7716936/) |
| `frontend/imagenes/CL-MU-005.jpg` | Vika Glitter | [Pexels 8305929](https://www.pexels.com/photo/a-woman-wearing-floral-dress-8305929/) |
| `frontend/imagenes/CL-MU-006.jpg` | Maksim Goncharenok | [Pexels 4663319](https://www.pexels.com/photo/a-person-wearing-a-pleated-skirt-4663319/) |
| `frontend/imagenes/CL-UNI-002.jpg` | Antoni Shkraba | [Pexels 6843224](https://www.pexels.com/photo/blue-denim-button-up-jacket-6843224/) |
| `frontend/imagenes/CL-HO-003.jpg` | Jonathan Borba | [Pexels 28576622](https://www.pexels.com/photo/minimalist-white-shirt-hanging-on-hanger-28576622/) |
| `frontend/imagenes/CL-MU-007.jpg` | José Martin Segura Benites | [Pexels 27081006](https://www.pexels.com/photo/woman-wearing-beige-trousers-on-a-pavement-27081006/) |
| `frontend/imagenes/CL-HO-004.jpg` | Dennis Ojenomoh | [Pexels 12529233](https://www.pexels.com/photo/portrait-of-a-man-in-a-blue-shirt-posing-with-his-arms-crossed-12529233/) |
| `frontend/imagenes/CL-MU-008.jpg` | Daniel Neves Cotta | [Pexels 20016578](https://www.pexels.com/photo/studio-shot-of-a-young-woman-wearing-a-jacket-20016578/) |
| `frontend/imagenes/T006.jpg` | Jonathan Borba | [Pexels 12031208](https://www.pexels.com/photo/a-man-wearing-a-blue-suit-12031208/) |
| `frontend/imagenes/T007.jpg` | Sandeep Singh | [Pexels 5856080](https://www.pexels.com/photo/bearded-man-wearing-his-beige-suit-5856080/) |
| `frontend/imagenes/T008.jpg` | Tima Miroshnichenko | [Pexels 6766361](https://www.pexels.com/photo/man-wearing-black-suit-6766361/) |
| `frontend/imagenes/T009.jpg` | Varun Ish Nanda | [Pexels 17420227](https://www.pexels.com/photo/man-in-black-suit-17420227/) |
| `frontend/imagenes/T010.jpg` | PNW Production | [Pexels 8276133](https://www.pexels.com/photo/man-wearing-a-gray-suit-8276133/) |

En esta ampliación se conservaron las once fotografías históricas, entonces sin permisos verificados. Posteriormente se sustituyeron por referencias de Pexels; véase [Sustitución de fotografías y revisión del logotipo](#sustitucion-fotografias). Las trece fotografías añadidas en la ampliación se mantienen intactas. Los derechos del logotipo siguen pendientes de confirmación.

<a id="correccion-fotografia"></a>

### Corrección mínima de interfaz

Se reprodujo un fallo en la ampliación: con la ventana principal próxima al borde inferior, el diálogo de fotografía salía de la pantalla. La prueba inicial falló porque su borde inferior superaba la altura disponible. Se ajustó únicamente `ampliar_fotografia` para considerar la escala de CustomTkinter en el tamaño de foto y ventana, y limitar las coordenadas a la pantalla. No se alteró la organización general de la interfaz.

### Pruebas

Comandos utilizados en aquella revisión, con dependencias gráficas y escritorio disponible; se conservan como registro histórico y ya no permiten ejecutar la suite retirada:

```powershell
python -B -m unittest discover -s tests -v
git diff --check
```

La suite retirada `tests/test_catalogo.py` contenía siete pruebas con múltiples casos. Redirige todas las rutas del backend hacia un directorio temporal antes de importar la interfaz. Usa los Excel ampliados como copias, un perfil ficticio y operaciones sintéticas. Compara hashes de los archivos originales de `data/` y `comprobantes/` antes y después.

| Comprobación | Resultado |
| --- | --- |
| Ampliación cerca del borde inferior y botón Cerrar dentro del diálogo | Aprobada tras la corrección |
| Catálogo, precios, filtros del backend y existencias nuevas | Aprobada |
| Integridad y apertura de fotos; ampliación de 13 prendas activas y 10 trajes | Aprobada |
| Búsqueda por código/nombre, filtros y límites horizontales de tarjetas de ropa y trajes | Aprobada a 360 × 560; ropa también a 1100 × 800 |
| Carrito, compra, comprobante, descuento de inventario y lectura del historial | Aprobada con archivos temporales |
| Registro de los cinco trajes nuevos, rechazo de cruces y conservación de un registro histórico ficticio | Aprobada |
| Inventario administrativo: 14 prendas, 44 variantes y 10 trajes | Aprobada |

Además se abrió la aplicación aislada y se revisaron visualmente tarjetas de prendas y una foto nueva ampliada. Esta observación es distinta de las mediciones automáticas; no constituye una revisión visual manual de cada tarjeta en todos los tamaños. La persistencia del carrito se comprobó al cambiar el estado de sesión dentro del mismo proceso, no mediante un reinicio completo.

### Archivos de esta tarea

- Modificados: `data/ropa.xlsx`, `data/inventario.xlsx` y la función `ampliar_fotografia` en `frontend/app.py`.
- Añadidos: trece fotos identificadas arriba, `registro de fotografías integrado en este README`, este informe y `tests/test_catalogo.py`.
- README, código restante, fotografías históricas y registros operativos: sin modificaciones durante esta tarea.
- Sin commits ni push.

### Pendientes y límites

- Sustitución de las once imágenes históricas completada posteriormente; la autorización del logotipo sigue pendiente (véase el informe de sustitución).
- La advertencia de fuente de CustomTkinter persiste en este entorno; utiliza su método alternativo de dibujo y no impidió las pruebas.
- Las licencias se comprobaron en las fuentes oficiales; la correspondencia visual es de referencia, no una certificación de productos del negocio.
- Los riesgos de privacidad del historial Git señalados en la auditoría anterior no se han corregido: esta tarea no autorizaba sanearlo.

</details>

<a id="sustitucion-fotografias"></a>

### Sustitución de fotografías y revisión del logotipo

Antecedente histórico: once reemplazos; revisión separada del logotipo, cuyos derechos no están confirmados.

<details>
<summary>Ver sustitución de fotografías y revisión del logotipo</summary>

Fecha: 17 de noviembre de 2026.

### Resultado

Se sustituyeron las once fotografías indicadas, conservando sus códigos y nombres de archivo. No quedan reemplazos fotográficos pendientes. Las trece fotografías de la ampliación anterior se conservaron sin cambios. Los catálogos siguen teniendo 14 prendas (13 activas y una inactiva) y 10 trajes.

Se consultaron `data/ropa.xlsx` y `data/inventario.xlsx` antes de seleccionar referencias. No se editaron esos archivos. Las nuevas fotografías ilustran tipos y estilos de prendas; no certifican composición, ligereza, ajuste ni existencias de productos reales del negocio.

### Reemplazos y fuentes

| Archivo en frontend/imagenes/ | Autor | Fuente oficial | Correspondencia visual |
| --- | --- | --- | --- |
| `CL-MU-001.jpg` | picko pictura | [Pexels 40867948](https://www.pexels.com/photo/young-woman-in-yellow-blouse-on-urban-street-40867948/) | Blusa ligera de tono amarillo para un conjunto casual. |
| `CL-MU-002.jpg` | Valerie Voila | [Pexels 13727333](https://www.pexels.com/photo/woman-wearing-a-long-loose-dress-13727333/) | Detalle de vestido suelto beige de caída ligera. |
| `CL-MU-003.jpg` | Polina Tankilevitch | [Pexels 7391123](https://www.pexels.com/photo/woman-in-a-black-midi-skirt-black-boots-and-red-socks-7391123/) | Detalle de falda negra de largo midi; el producto continúa inactivo. |
| `CL-HO-001.jpg` | cottonbro studio | [Pexels 7764063](https://www.pexels.com/photo/a-person-wearing-a-long-sleeve-shirt-7764063/) | Detalle de camisa formal de manga larga y puños. |
| `CL-HO-002.jpg` | Elina Volkova | [Pexels 16238583](https://www.pexels.com/photo/a-man-in-a-white-sweater-and-tan-pants-16238583/) | Pantalón beige de corte recto en un conjunto casual. |
| `CL-UNI-001.jpg` | Santiago Sauceda González | [Pexels 10024417](https://www.pexels.com/photo/selective-focus-of-a-man-wearing-his-bomber-jacket-10024417/) | Chaqueta casual tipo bomber para un conjunto de entretiempo. |
| `T001.jpg` | Gustavo Fring | [Pexels 6284888](https://www.pexels.com/photo/a-man-wearing-a-black-suit-6284888/) | Traje negro clásico de dos piezas para ocasiones formales. |
| `T002.jpg` | Puskar Rai | [Pexels 13849227](https://www.pexels.com/photo/a-bearded-man-wearing-black-suit-13849227/) | Traje oscuro con solapas de gala para ceremonias y bodas. |
| `T003.jpg` | Bruno Casttro | [Pexels 29242239](https://www.pexels.com/photo/elegant-man-in-stylish-cream-suit-fashion-portrait-29242239/) | Traje claro para una referencia de evento de día; la ligereza del tejido no puede certificarse visualmente. |
| `T004.jpg` | zaid mohammed | [Pexels 11982600](https://www.pexels.com/photo/man-in-gray-suit-jacket-11982600/) | Traje gris formal de estilo moderno para reuniones. |
| `T005.jpg` | Taiye Salawu | [Pexels 37263479](https://www.pexels.com/photo/confident-man-in-tuxedo-posing-outdoors-37263479/) | Esmoquin de gala con solapas satinadas y tejido con detalles brillantes. |

### Permisos y tratamiento

En cada ficha oficial se comprobó la indicación «Free» o «Free to use». Se consultó la [licencia oficial de Pexels](https://www.pexels.com/license/): permite descargar, utilizar y modificar fotografías, sin exigir atribución, con restricciones como no sugerir respaldo de las personas o marcas retratadas y no redistribuirlas como un banco de imágenes. Los créditos se conservan voluntariamente.

Se revisaron visualmente las once referencias y no se observaron marcas de agua. Se descartaron opciones en las que la prenda se veía demasiado pequeña o aparecía una marca destacada en el fondo. Se mantuvieron las proporciones originales sin recortar; la optimización fue JPEG, calidad 88, lado mayor 1600 píxeles y sin EXIF.

El registro completo está en `registro de fotografías integrado en este README`: código, archivo, identificador de Pexels, autor, ficha y descarga original, licencia, fecha de verificación, dimensiones, tamaño y SHA-256. Las once fichas de reemplazo se guardan como valores multilínea de la sección general, conservando las secciones originales para no cambiar el lector de pruebas.

Peso conjunto de los once reemplazos: 2.22 MiB.

### Respaldo privado

Las once imágenes originales se copiaron, antes de sustituirlas, a la carpeta `Efrata_respaldo_fotos_20261117` en Descargas, fuera del repositorio. Se verificó la igualdad byte a byte y se guardó un registro privado `SHA256.txt`. El respaldo no debe incorporarse a la entrega pública.

### Verificaciones ejecutadas

```powershell
python -B -m unittest discover -s tests -v
git diff --check
```

- Las siete pruebas existentes aprobaron, sin modificar el código de pruebas ni el código de la aplicación.
- La suite comprobó catálogo y existencias, filtros y búsquedas, límites horizontales de tarjetas en ventanas pequeñas y amplias, ampliación de imágenes, compra y carrito aislados, conflictos de alquiler y consulta administrativa.
- Adicionalmente se verificó la carga de las once miniaturas y se abrieron sus once diálogos de ampliación, incluida la fotografía de la falda inactiva. Los diálogos quedaron dentro de la altura de pantalla.
- Cada JPEG se verificó con Pillow y no contiene EXIF. La selección visual se hizo sobre las fotografías; las mediciones de distribución y límites en la interfaz fueron automatizadas con widgets Tk reales.
- Se compararon hashes de los archivos protegidos: Excel, registros históricos, cuentas, comprobantes, README, código Python, logotipo y trece fotografías nuevas permanecieron intactos.
- Se conservan las reglas existentes de tamaño y distribución de tarjetas. Las proporciones diferentes de las fuentes pueden cambiar el espacio ocupado por una imagen dentro de su tarjeta.
- CustomTkinter sigue mostrando una advertencia de fuente y utiliza su dibujo alternativo. No impidió las comprobaciones.

### Archivos de esta tarea

- Sustituidos: los once JPEG listados en la tabla.
- Actualizados: `registro de fotografías integrado en este README` y las notas de estado en `antecedente de ampliación integrado en este README`.
- Añadido: este informe.
- No se incorporaron archivos JSON, ni se modificaron Excel, README, fotografías nuevas, código Python u operaciones existentes. Sin commits ni push.

### Revisión separada del logotipo

Archivo: `frontend/imagenes/efrata_logo_ui.png`. Se conservó sin cambios.

Se inspeccionó visualmente el PNG y sus metadatos, se revisaron las referencias del proyecto y el historial Git local. El archivo mide 436 × 281 píxeles y no aporta campos de autoría ni EXIF. El historial contiene una incorporación del recurso y un checkpoint posterior; eso acredita su presencia en el proyecto, no la autoría del diseño ni una autorización.

Un README histórico enlazaba una imagen alojada como adjunto de GitHub. Ese alojamiento no constituye por sí mismo una licencia ni permite establecer con certeza el origen del PNG actual. La búsqueda pública por el nombre del negocio tampoco aportó una fuente concluyente. No se encontró documentación que identifique autor, licencia de los adornos o tipografía, archivo editable original o permiso del titular.

**Estado: derechos de uso del logotipo no confirmados.** No se afirma que infrinja derechos, pero tampoco que sea de libre uso. Queda pendiente obtener del negocio o de quien lo diseñó una confirmación de autoría y autorización para la publicación académica, junto con las licencias de los recursos utilizados cuando corresponda. No se sustituyó ni se atribuyó una licencia de Pexels al logotipo.

</details>

<a id="registro-fotografias"></a>

### Registro completo de las 24 fotografías

Transcripción íntegra del registro de fuentes: autores, fichas originales, descargas, licencia, fecha de verificación, correspondencia visual, descripciones, precios y tallas de las incorporaciones, resolución, tamaño y SHA-256. La licencia y el tratamiento generales se aplican también a las trece fichas de incorporación. Los datos corresponden a la revisión del 17 de noviembre de 2026, no a una nueva consulta de licencias.

<details>
<summary>Ver registro completo de las 24 fotografías</summary>

```text
# Fuentes del catálogo académico. Importes en COP; datos de demostración.
# Cada sección describe una fotografía y su producto asociado.

[general]
aviso = Productos, precios, tallas y existencias ficticios para demostración académica. Las fotografías son referencias externas, no productos fotografiados en Efrata Minimall ni recomendaciones de sus modelos.
licencia = Pexels License
licencia_url = https://www.pexels.com/license/
fecha_verificacion = 2026-11-17
tratamiento = JPEG optimizado, lado mayor máximo 1600 px, sin recorte y sin metadatos EXIF. No se altera la prenda.

# Reemplazos de fotografías históricas; fichas multilínea de la sección general.
# Se conservan las secciones de las trece incorporaciones anteriores sin cambios.
fecha_verificacion_reemplazos = 2026-11-17
licencia_reemplazos = Pexels License; https://www.pexels.com/license/
condiciones_reemplazos = Uso académico como referencia, sin sugerir respaldo de modelos o marcas. No vender copias sin alterar, no redistribuir como banco de imágenes ni usar las fotos como marca.
respaldo_reemplazos = Copia privada fuera del repositorio: Efrata_respaldo_fotos_20261117 (Descargas).

reemplazo_cl_mu_001 =
    codigo: CL-MU-001
    archivo: frontend/imagenes/CL-MU-001.jpg
    foto_id: 40867948
    autor: picko pictura
    fuente: https://www.pexels.com/photo/young-woman-in-yellow-blouse-on-urban-street-40867948/
    descarga: https://images.pexels.com/photos/40867948/pexels-photo-40867948.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1067 x 1600
    bytes: 230714
    sha256: 014aa88154ede4f3488f0033008455bc9314c2f0a4311c04bcc30efc60d499c7
    correspondencia: Blusa ligera de tono amarillo para un conjunto casual.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_cl_mu_002 =
    codigo: CL-MU-002
    archivo: frontend/imagenes/CL-MU-002.jpg
    foto_id: 13727333
    autor: Valerie Voila
    fuente: https://www.pexels.com/photo/woman-wearing-a-long-loose-dress-13727333/
    descarga: https://images.pexels.com/photos/13727333/pexels-photo-13727333.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1600 x 1600
    bytes: 645596
    sha256: 3f3a29efbd8883ddfeaffce09e0a4e8040fae65eefd6fd34b33717bff96e7cd4
    correspondencia: Detalle de vestido suelto beige de caída ligera.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_cl_mu_003 =
    codigo: CL-MU-003
    archivo: frontend/imagenes/CL-MU-003.jpg
    foto_id: 7391123
    autor: Polina Tankilevitch
    fuente: https://www.pexels.com/photo/woman-in-a-black-midi-skirt-black-boots-and-red-socks-7391123/
    descarga: https://images.pexels.com/photos/7391123/pexels-photo-7391123.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1600 x 1067
    bytes: 149529
    sha256: 59c8d4d65feb65b1b225342b23757817b7ede24b58bab01673019e20f790f54f
    correspondencia: Detalle de falda negra de largo midi; el producto continúa inactivo.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_cl_ho_001 =
    codigo: CL-HO-001
    archivo: frontend/imagenes/CL-HO-001.jpg
    foto_id: 7764063
    autor: cottonbro studio
    fuente: https://www.pexels.com/photo/a-person-wearing-a-long-sleeve-shirt-7764063/
    descarga: https://images.pexels.com/photos/7764063/pexels-photo-7764063.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1600 x 1067
    bytes: 188825
    sha256: 8bbcc80b341c1350f9b14ad689b3a891863ae9e07bece818018c5e6ed435cb9b
    correspondencia: Detalle de camisa formal de manga larga y puños.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_cl_ho_002 =
    codigo: CL-HO-002
    archivo: frontend/imagenes/CL-HO-002.jpg
    foto_id: 16238583
    autor: Elina Volkova
    fuente: https://www.pexels.com/photo/a-man-in-a-white-sweater-and-tan-pants-16238583/
    descarga: https://images.pexels.com/photos/16238583/pexels-photo-16238583.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1067 x 1600
    bytes: 129994
    sha256: d258abadc15d02f038ada37604210a5a3f1f5a44932a2dcbd3d857c3bcbbc773
    correspondencia: Pantalón beige de corte recto en un conjunto casual.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_cl_uni_001 =
    codigo: CL-UNI-001
    archivo: frontend/imagenes/CL-UNI-001.jpg
    foto_id: 10024417
    autor: Santiago Sauceda González
    fuente: https://www.pexels.com/photo/selective-focus-of-a-man-wearing-his-bomber-jacket-10024417/
    descarga: https://images.pexels.com/photos/10024417/pexels-photo-10024417.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1083 x 1600
    bytes: 167275
    sha256: 03501ca74daf60fd2219a8148106325000a776ee9218346149461375eccac5e8
    correspondencia: Chaqueta casual tipo bomber para un conjunto de entretiempo.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_t001 =
    codigo: T001
    archivo: frontend/imagenes/T001.jpg
    foto_id: 6284888
    autor: Gustavo Fring
    fuente: https://www.pexels.com/photo/a-man-wearing-a-black-suit-6284888/
    descarga: https://images.pexels.com/photos/6284888/pexels-photo-6284888.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1067 x 1600
    bytes: 250617
    sha256: dc0623e0a888611ea098e56fc9c5c4ca94e54b03e242f90d9e6647f59b7e6a1d
    correspondencia: Traje negro clásico de dos piezas para ocasiones formales.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_t002 =
    codigo: T002
    archivo: frontend/imagenes/T002.jpg
    foto_id: 13849227
    autor: Puskar Rai
    fuente: https://www.pexels.com/photo/a-bearded-man-wearing-black-suit-13849227/
    descarga: https://images.pexels.com/photos/13849227/pexels-photo-13849227.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1067 x 1600
    bytes: 151890
    sha256: aabf25ecb5282cded444cf99d850d18512032260aceb81f77b5be6096b0e88a5
    correspondencia: Traje oscuro con solapas de gala para ceremonias y bodas.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_t003 =
    codigo: T003
    archivo: frontend/imagenes/T003.jpg
    foto_id: 29242239
    autor: Bruno Casttro
    fuente: https://www.pexels.com/photo/elegant-man-in-stylish-cream-suit-fashion-portrait-29242239/
    descarga: https://images.pexels.com/photos/29242239/pexels-photo-29242239.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1067 x 1600
    bytes: 102291
    sha256: 4f4f589fae2ff2c3a07da4c26a6e7a0eca842ae030af9bf953c54eb06d24c0a9
    correspondencia: Traje claro para una referencia de evento de día; la ligereza del tejido no puede certificarse visualmente.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_t004 =
    codigo: T004
    archivo: frontend/imagenes/T004.jpg
    foto_id: 11982600
    autor: zaid mohammed
    fuente: https://www.pexels.com/photo/man-in-gray-suit-jacket-11982600/
    descarga: https://images.pexels.com/photos/11982600/pexels-photo-11982600.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 900 x 1600
    bytes: 152972
    sha256: b8de9d2ee2438612587e13694088586bfaa06f1f927b366ed382fccb677b0b5f
    correspondencia: Traje gris formal de estilo moderno para reuniones.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

reemplazo_t005 =
    codigo: T005
    archivo: frontend/imagenes/T005.jpg
    foto_id: 37263479
    autor: Taiye Salawu
    fuente: https://www.pexels.com/photo/confident-man-in-tuxedo-posing-outdoors-37263479/
    descarga: https://images.pexels.com/photos/37263479/pexels-photo-37263479.jpeg
    licencia: Pexels License
    licencia_url: https://www.pexels.com/license/
    comprobacion_licencia: ficha oficial marcada Free / Free to use y licencia general de Pexels.
    fecha_verificacion: 2026-11-17
    tratamiento: JPEG calidad 88; lado mayor 1600 px; proporciones originales; sin recorte ni EXIF.
    resolucion: 1067 x 1600
    bytes: 154596
    sha256: 8e64c7ee1038889cbf6e67a3b7e30b51350e541e5c5579b63da69573f3fc1551
    correspondencia: Esmoquin de gala con solapas satinadas y tejido con detalles brillantes.
    alcance: imagen de referencia; no certifica tejido, fabricación ni disponibilidad real.

[producto:CL-MU-004]
codigo = CL-MU-004
nombre = Blusa Alba Demo
seccion = Mujer
tipo = Blusa
precio = 59000
descripcion = Blusa blanca con lazo y caída suave. Referencia académica.
existencias = S:3, M:4, L:2
foto_id = 7716936
autor = cottonbro studio
fuente = https://www.pexels.com/photo/a-person-wearing-white-blouse-7716936/
archivo = frontend/imagenes/CL-MU-004.jpg
descarga = https://images.pexels.com/photos/7716936/pexels-photo-7716936.jpeg
resolucion = 1600 x 1067
sha256 = ea6c1129a8b93cca4f9b813fcb522a5aa694e3e9ac2907a52e6eed995f0b7559
bytes = 117300

[producto:CL-MU-005]
codigo = CL-MU-005
nombre = Vestido Jardín Demo
seccion = Mujer
tipo = Vestido
precio = 115000
descripcion = Vestido de estampado floral para ocasiones de día. Referencia académica.
existencias = S:2, M:3, L:2
foto_id = 8305929
autor = Vika Glitter
fuente = https://www.pexels.com/photo/a-woman-wearing-floral-dress-8305929/
archivo = frontend/imagenes/CL-MU-005.jpg
descarga = https://images.pexels.com/photos/8305929/pexels-photo-8305929.jpeg
resolucion = 1066 x 1600
sha256 = d99923839f01091f04104e8be8db908a7def0767093ef737965d1264c35d635f
bytes = 317358

[producto:CL-MU-006]
codigo = CL-MU-006
nombre = Falda Aurora Demo
seccion = Mujer
tipo = Falda
precio = 79000
descripcion = Falda plisada con tonos degradados y movimiento ligero. Referencia académica.
existencias = S:3, M:3, L:2
foto_id = 4663319
autor = Maksim Goncharenok
fuente = https://www.pexels.com/photo/a-person-wearing-a-pleated-skirt-4663319/
archivo = frontend/imagenes/CL-MU-006.jpg
descarga = https://images.pexels.com/photos/4663319/pexels-photo-4663319.jpeg
resolucion = 1067 x 1600
sha256 = 06f0873eae9d82e5f25099d21e2a3fc1158e925891038318e2bc48710415a385
bytes = 148635

[producto:CL-UNI-002]
codigo = CL-UNI-002
nombre = Chaqueta Índigo Demo
seccion = Unisex
tipo = Chaqueta
precio = 139000
descripcion = Chaqueta de mezclilla azul con botones y bolsillos frontales. Referencia académica.
existencias = S:2, M:4, L:3, XL:2
foto_id = 6843224
autor = Antoni Shkraba
fuente = https://www.pexels.com/photo/blue-denim-button-up-jacket-6843224/
archivo = frontend/imagenes/CL-UNI-002.jpg
descarga = https://images.pexels.com/photos/6843224/pexels-photo-6843224.jpeg
resolucion = 1067 x 1600
sha256 = ebb65a1dd53bbd2267f252d1503a82d4c0a71fa598424fa0823d08cd7177fdd3
bytes = 992256

[producto:CL-HO-003]
codigo = CL-HO-003
nombre = Camisa Nácar Demo
seccion = Hombre
tipo = Camisa
precio = 68000
descripcion = Camisa blanca de botones para combinar con prendas formales. Referencia académica.
existencias = S:2, M:4, L:3, XL:2
foto_id = 28576622
autor = Jonathan Borba
fuente = https://www.pexels.com/photo/minimalist-white-shirt-hanging-on-hanger-28576622/
archivo = frontend/imagenes/CL-HO-003.jpg
descarga = https://images.pexels.com/photos/28576622/pexels-photo-28576622.jpeg
resolucion = 1067 x 1600
sha256 = e0ae5acf6297adedf764ef6aedf002d2cdfd6c170c3d1caeb5866007439c3f38
bytes = 203424

[producto:CL-MU-007]
codigo = CL-MU-007
nombre = Pantalón Arena Demo
seccion = Mujer
tipo = Pantalón
precio = 95000
descripcion = Pantalón beige de estilo urbano para conjuntos de día. Referencia académica.
existencias = 6:2, 8:3, 10:4, 12:2
foto_id = 27081006
autor = José Martin Segura Benites
fuente = https://www.pexels.com/photo/woman-wearing-beige-trousers-on-a-pavement-27081006/
archivo = frontend/imagenes/CL-MU-007.jpg
descarga = https://images.pexels.com/photos/27081006/pexels-photo-27081006.jpeg
resolucion = 1600 x 1600
sha256 = 6f0832fb0bdbb49c543bc65c6f848a3944dae39cca9685f9dc66aeb2febd1e68
bytes = 458751

[producto:CL-HO-004]
codigo = CL-HO-004
nombre = Camisa Cobalto Demo
seccion = Hombre
tipo = Camisa
precio = 74000
descripcion = Camisa azul de manga larga para un conjunto casual. Referencia académica.
existencias = S:2, M:3, L:3, XL:1
foto_id = 12529233
autor = Dennis Ojenomoh
fuente = https://www.pexels.com/photo/portrait-of-a-man-in-a-blue-shirt-posing-with-his-arms-crossed-12529233/
archivo = frontend/imagenes/CL-HO-004.jpg
descarga = https://images.pexels.com/photos/12529233/pexels-photo-12529233.jpeg
resolucion = 1333 x 1600
sha256 = b83e68487b35035ba352ea4ea851df587486686003f687b260da23415ef64747
bytes = 307433

[producto:CL-MU-008]
codigo = CL-MU-008
nombre = Chaqueta Marfil Demo
seccion = Mujer
tipo = Chaqueta
precio = 149000
descripcion = Chaqueta blanca de estilo moderno para combinar con tonos neutros. Referencia académica.
existencias = S:2, M:3, L:2
foto_id = 20016578
autor = Daniel Neves Cotta
fuente = https://www.pexels.com/photo/studio-shot-of-a-young-woman-wearing-a-jacket-20016578/
archivo = frontend/imagenes/CL-MU-008.jpg
descarga = https://images.pexels.com/photos/20016578/pexels-photo-20016578.jpeg
resolucion = 1067 x 1600
sha256 = c1663db3e6935d5ab7a2bb20acb306bcbb99548362bccbe2c0fa25beef03706b
bytes = 258247

[traje:T006]
codigo = T006
nombre = Traje Azul Ceremonia Demo
tallas = S, M, L, XL
precio = 160000
descripcion = Traje azul para ceremonias y eventos de día. Imagen de referencia académica.
foto_id = 12031208
autor = Jonathan Borba
fuente = https://www.pexels.com/photo/a-man-wearing-a-blue-suit-12031208/
archivo = frontend/imagenes/T006.jpg
descarga = https://images.pexels.com/photos/12031208/pexels-photo-12031208.jpeg
resolucion = 1067 x 1600
sha256 = b58307e9a7a5c1eee818fbfe5596eb7db050ff2c97fcc0cfd15588c75112f8e7
bytes = 398355

[traje:T007]
codigo = T007
nombre = Traje Beige Balcón Demo
tallas = S, M, L
precio = 145000
descripcion = Traje beige de estilo claro para celebraciones de día. Imagen de referencia académica.
foto_id = 5856080
autor = Sandeep Singh
fuente = https://www.pexels.com/photo/bearded-man-wearing-his-beige-suit-5856080/
archivo = frontend/imagenes/T007.jpg
descarga = https://images.pexels.com/photos/5856080/pexels-photo-5856080.jpeg
resolucion = 1600 x 1067
sha256 = a96d05fbb199237b73b11f070be2a26250d24ccad933a56965b7785d02942a55
bytes = 147971

[traje:T008]
codigo = T008
nombre = Traje Negro Ejecutivo Demo
tallas = M, L, XL
precio = 155000
descripcion = Traje negro clásico para reuniones y eventos formales. Imagen de referencia académica.
foto_id = 6766361
autor = Tima Miroshnichenko
fuente = https://www.pexels.com/photo/man-wearing-black-suit-6766361/
archivo = frontend/imagenes/T008.jpg
descarga = https://images.pexels.com/photos/6766361/pexels-photo-6766361.jpeg
resolucion = 1600 x 1067
sha256 = d6986c39a12f7c6a9a9c82c97fe44fb84cd3c3fb815fd859b94bec9c86b8e348
bytes = 255469

[traje:T009]
codigo = T009
nombre = Esmoquin Gala Demo
tallas = S, M, L
precio = 185000
descripcion = Esmoquin negro para celebraciones y ocasiones especiales. Imagen de referencia académica.
foto_id = 17420227
autor = Varun Ish Nanda
fuente = https://www.pexels.com/photo/man-in-black-suit-17420227/
archivo = frontend/imagenes/T009.jpg
descarga = https://images.pexels.com/photos/17420227/pexels-photo-17420227.jpeg
resolucion = 1067 x 1600
sha256 = 2c8d44d6eac42430a3b78c6de22c0c1b1309c01d50a06f09db332299d02b69ce
bytes = 148331

[traje:T010]
codigo = T010
nombre = Traje Gris Urbano Demo
tallas = S, M, L, XL
precio = 150000
descripcion = Traje gris de estilo formal para grados y reuniones. Imagen de referencia académica.
foto_id = 8276133
autor = PNW Production
fuente = https://www.pexels.com/photo/man-wearing-a-gray-suit-8276133/
archivo = frontend/imagenes/T010.jpg
descarga = https://images.pexels.com/photos/8276133/pexels-photo-8276133.jpeg
resolucion = 1067 x 1600
sha256 = f19140bb93f46e395d9befd13265588e93cbc555fa19120679fb06953f4dc361
bytes = 224161
```

</details>

<a id="informe-tecnico-31"></a>

### Informe técnico histórico de 31 pruebas

Esta revisión contiene siete casos del catálogo y 24 adicionales. La prueba 25 de presentación se incorporó después: véase el registro final de 32 pruebas. Los estados de pago citados aquí corresponden a aquella ejecución; las etiquetas visibles actuales son Pendiente y No procesado, según la tabla de métodos de pago.

<details>
<summary>Ver informe técnico histórico de 31 pruebas</summary>

Efrata Minimall — Universidad Autónoma de Occidente, Algoritmia y Programación, 2026.

### Objetivo y resultado

Ampliar la evidencia reproducible de funciones críticas, entradas válidas, inválidas, límites e integración sin alterar producción ni datos originales. No se reconstruyeron resultados históricos.

**Resultado final: 31 pruebas ejecutadas, 31 aprobadas, 0 fallidas, 0 errores y 0 omitidas.** Había siete pruebas; se conservaron sus casos y se añadieron 24. Los subcasos de cada método no se cuentan como pruebas independientes.

### Entorno y reproducción

- Python: 3.12.10
- Sistema: Windows
- customtkinter: 6.0.0
- pandas: 3.0.6
- openpyxl: 3.1.5
- Pillow: 12.2.0
- tkcalendar: 1.6.1

En aquella revisión se ejecutaron los siguientes comandos, con las dependencias instaladas y un escritorio gráfico disponible:

```powershell
python -B -m unittest discover -s tests -v
git diff --check
```

La salida completa de la ejecución final está en [RESULTADOS_PRUEBAS_TECNICAS.txt](#registro-31-pruebas). El comando de unittest terminó con código cero: `Ran 31 tests in 31.841s`, `OK`. Se verificó la compilación de los 16 archivos Python con `compile()` en memoria, sin producir bytecode. `git diff --check` terminó con código cero y sin errores.

### Aislamiento y datos de prueba

- Cada caso nuevo crea un directorio temporal distinto y dos Excel totalmente sintéticos: una prenda activa con cinco unidades, otra inactiva, un traje activo y otro inactivo. No copia cuentas u operaciones reales.
- Antes de ejecutar operaciones se parchean todas las constantes Path de archivos y directorios importadas por los módulos del backend. Cada ruta resultante debe estar dentro del directorio temporal; una aserción impide continuar si no lo está.
- Perfiles, cuentas, contraseñas y últimos cuatro dígitos son ficticios. No se usan tarjetas reales.
- Las siete pruebas anteriores mantienen sus aserciones y su inventario de referencia; su preparación ahora repone las copias temporales y vacía los registros temporales antes de cada caso para no depender de operaciones anteriores.
- Cada caso comprueba hashes SHA-256 de los datos originales antes/después o contra la línea base de su clase. La ejecución final también comparó todos los archivos del proyecto antes y después de correr y compilar: no hubo cambios.
- Los parches, sesiones y directorios temporales se limpian incluso cuando una aserción falla. Las pruebas gráficas cancelan callbacks Tk pendientes antes de destruir su raíz.
- En pruebas gráficas solo se sustituyen avisos informativos y la respuesta del diálogo de confirmación. Los validadores, callbacks de envío, backend y persistencia reales permanecen activos.

### Siete pruebas conservadas

Estos casos pertenecían a la suite del catálogo, ahora retirada. No deben confundirse con las seis regresiones históricas eliminadas.

| Función y caso | Resultado esperado | Resultado obtenido | Evidencia | Estado |
| --- | --- | --- | --- | --- |
| Ampliación cerca del borde | Diálogo y Cerrar dentro de límites | Límites verificados | `test_00_ampliacion_dentro_de_pantalla` (suite retirada) | Aprobado |
| Catálogos y existencias | 13 prendas activas, 10 trajes y fichas coincidentes | Totales, precios, tallas y filtros coincidentes | `test_01_catalogos_y_existencias` (suite retirada) | Aprobado |
| Fotos y apertura | Hashes/resolución/EXIF de 13 fotos y ampliación del catálogo activo | 13 verificaciones de integridad y 23 diálogos abiertos | `test_02_fotos_fuentes_y_apertura` (suite retirada) | Aprobado |
| Búsquedas y distribución | Una tarjeta por búsqueda y límites horizontales correctos | Búsquedas por nombre/código y mediciones a 360 × 560 y 1100 × 800 correctas | `test_03_busqueda_filtros_y_tarjetas` (suite retirada) | Aprobado |
| Carrito y compra | Conservar artículo, comprar y actualizar archivos | Stock 4 a 3, pedido leído y carrito vacío | `test_04_carrito_compra_y_stock` (suite retirada) | Aprobado |
| Alquiler y registro previo | Aceptar cinco alquileres y rechazar cruces | Cinco registros válidos; histórico ficticio conservado; cruces rechazados | `test_05_alquiler_conflicto_y_registro_historico` (suite retirada) | Aprobado |
| Consulta administrativa | 14 prendas, 44 variantes y 10 trajes | Totales y existencias comprobados | `test_06_inventario_administrativo` (suite retirada) | Aprobado |

### Veinticuatro pruebas nuevas

Los métodos 01–20 son de backend y almacenamiento; los métodos 21–24 utilizan widgets reales de CustomTkinter. Sus datos se recrean para cada método.

| Función | Caso | Resultado esperado | Resultado obtenido | Evidencia | Estado |
| --- | --- | --- | --- | --- | --- |
| Acceso | Registro, hash y duplicado | Cuenta única, hash PBKDF2 y acceso válido. | Cuenta creada; duplicado rechazado; contraseña incorrecta sin sesión; acceso correcto y dos registros de inicio. El archivo contiene PBKDF2, no la contraseña ficticia. | `test_01_registro_acceso_hash_duplicado` (suite retirada) | Aprobado |
| Acceso | Correo y contraseña inválidos | Rechazo sin escribir cuentas. | Se rechazaron seis correos y seis contraseñas inválidos; las huellas temporales no cambiaron. | `test_02_formatos_registro_invalidos` (suite retirada) | Aprobado |
| Seguridad | Sin sesión y cuenta ajena | PermissionError sin escrituras. | Las cuatro operaciones sin sesión y la consulta del carrito ajeno lanzaron PermissionError; no hubo escrituras. | `test_03_operaciones_sin_sesion_y_otro_usuario` (suite retirada) | Aprobado |
| Perfil | Cada campo vacío individualmente | Compra y alquiler bloqueados sin escrituras. | Cada uno de los siete campos vacío bloqueó compra y alquiler; el faltante fue identificado y las huellas se conservaron. | `test_04_siete_campos_obligatorios` (suite retirada) | Aprobado |
| Perfil | Perfil inexistente | Ambas operaciones bloqueadas sin archivos nuevos. | Compra y alquiler bloqueados sin perfil; no se generaron operaciones. | `test_05_perfil_ausente` (suite retirada) | Aprobado |
| Pagos | Tres métodos y perfil válido | Método y estado conservados en ambas operaciones. | Efectivo quedó Pendiente; crédito y débito quedaron No procesado; demostración académica, en compras y alquileres leídos del TXT. | `test_06_tres_metodos_y_estados` (suite retirada) | Aprobado |
| Pagos | Método no permitido | ValueError y datos temporales intactos. | Los dos métodos no permitidos se rechazaron en ambas operaciones sin alterar archivos. | `test_07_metodos_invalidos` (suite retirada) | Aprobado |
| Carrito | Dos usuarios ficticios | Compra de uno conserva el carrito del otro. | El primer usuario compró una unidad; el segundo conservó dos unidades en su carrito. | `test_08_carritos_separados` (suite retirada) | Aprobado |
| Carrito | Cero, negativos, fracciones y exceso | Rechazo sin modificar carrito ni stock. | Se rechazaron cero, negativo, fracción, texto, NaN, infinito y cantidad superior a cinco; archivos intactos. | `test_09_cantidades_invalidas` (suite retirada) | Aprobado |
| Compra | Comprar todas las existencias | Stock cero, pedido y comprobante correctos; carrito vacío. | Compra de cinco unidades: total 250000, stock cero, carrito vacío, pedido con cinco unidades y comprobante con identificador, producto, cantidad, importe y método. | `test_10_compra_stock_exacto_comprobante_historial` (suite retirada) | Aprobado |
| Compra | Cancelar confirmación | Inventario, carrito y registros sin cambios. | Cancelación con resultado no confirmado y hashes temporales idénticos. | `test_11_cancelacion` (suite retirada) | Aprobado |
| Compra | Inventario menor que carrito guardado | Compra rechazada y carrito conservado. | Tras reducir el stock de cinco a cuatro, la compra de cinco fue rechazada y el carrito permaneció intacto. | `test_12_stock_reducido_antes_de_comprar` (suite retirada) | Aprobado |
| Persistencia | Leer carrito desde otro intérprete | Recuperar exactamente artículo, talla y cantidad. | Un intérprete Python nuevo recuperó exactamente P1, talla M, cantidad 2 desde el TXT temporal; terminó con código cero. | `test_13_carrito_en_proceso_nuevo` (suite retirada) | Aprobado |
| Alquiler | Formatos, fecha pasada y devolución no posterior | Rechazo sin escrituras. | Se rechazaron fecha inexistente, formato incorrecto, inicio pasado, devolución igual y devolución anterior; sin escrituras. | `test_14_fechas_invalidas` (suite retirada) | Aprobado |
| Alquiler | Talla inexistente y traje inactivo o ausente | Rechazo sin registros. | Se rechazaron talla inexistente, traje inactivo y código ausente; sin registros nuevos. | `test_15_tallas_y_trajes_invalidos` (suite retirada) | Aprobado |
| Disponibilidad | Último día de revisión y día siguiente | Rechazo hasta devolución +2; aceptación en +3. | Se rechazaron reservas en la devolución y en los días +1 y +2; se aceptó el día +3. | `test_16_limites_revision_dos_dias` (suite retirada) | Aprobado |
| Devolución | Devolver desde el día de inicio y repetir | Fecha real y pago conservados; repetición rechazada. | Devolución desde el día inicial: estado Devuelto y fecha real de hoy; método y estado de pago conservados. Repetición rechazada. Revisión bloqueada hasta +2 y libre en +3. | `test_17_devolucion_y_pago_conservado` (suite retirada) | Aprobado |
| Devolución | Antes del inicio | Rechazo conservando el alquiler activo. | La devolución antes del inicio fue rechazada; las huellas del alquiler permanecieron intactas. | `test_18_devolucion_anticipada` (suite retirada) | Aprobado |
| Administración | Cuenta normal | Consultas y modificación denegadas sin cambios. | La cuenta normal no pudo consultar inventario, compras o alquileres ni cambiar existencias; sin cambios. | `test_19_administracion_denegada` (suite retirada) | Aprobado |
| Administración | Consultar y modificar copias | Operaciones visibles y existencias actualizadas sin perder registros. | El administrador leyó una compra y un alquiler, cambió stock a siete y volvió a leerlo. Cantidad negativa rechazada sin escrituras. | `test_20_administracion_autorizada` (suite retirada) | Aprobado |
| Interfaz | Tarjetas incompletas e inválidas | Ambos formularios rechazan sin escrituras. | Veinte combinaciones de formulario (dos tarjetas, cinco entradas y dos operaciones) bloquearon el envío, mostraron el mensaje esperado y no escribieron datos. | `test_21_tarjetas_invalidas_formularios` (suite retirada) | Aprobado |
| Integración gráfica | Enviar widgets reales con tres métodos | Pedido, comprobante, stock y alquiler persistidos; tarjeta no guardada. | Tres compras y tres alquileres enviados desde widgets: métodos/estados leídos, stock final dos, carritos vacíos y comprobantes presentes. Ningún TXT guardó el titular ni los cuatro dígitos ficticios. | `test_22_compra_y_alquiler_desde_formularios` (suite retirada) | Aprobado |
| Interfaz administrativa | Panel autorizado | Panel visible y consulta del inventario temporal. | Panel administrativo visible con sesión autorizada, mensaje sin error y dos productos consultados. | `test_23_panel_administrativo_real` (suite retirada) | Aprobado |
| Integración administrativa | Guardar edición de traje desde widgets | Precio y descripción persisten en Excel temporal. | Botón Guardar traje invocado: código T1 conservado, precio 125000 y descripción actualizada leídos del Excel temporal; sin diálogo de error. | `test_24_edicion_administrativa_formulario` (suite retirada) | Aprobado |

### Integración gráfica ejecutada

- **Compra:** se rellenan campos reales de titular y cuatro dígitos, se selecciona el método y se ejecuta el callback real `comprar`. Se verifican pedido, estado de pago, comprobante, inventario y carrito en archivos temporales.
- **Alquiler:** se rellenan talla, fechas y método en widgets reales y se ejecuta `confirmar_alquiler_interfaz`. Se comprueba el registro TXT leído por el backend.
- **Administración:** se abre el panel autorizado y un formulario real de edición de traje. Se editan sus campos y se invoca el botón Guardar traje; se vuelve a leer precio y descripción del Excel temporal.
- No se automatizan movimientos de ratón o teclado físico ni se afirma una inspección visual humana de todos los formularios. Se ejecutan sus controles/callbacks programáticamente con Tk real.

### Errores, correcciones y repetición

No se detectaron nuevos fallos de producción con los casos ejecutados y no se modificó código de producción.

Durante la preparación de la nueva infraestructura se observaron avisos de callbacks Tk pendientes al destruir y recrear raíces entre pruebas. Se corrigió la limpieza en las pruebas, cancelando los eventos pendientes. La ejecución final de 31 casos no contiene esos avisos. No se atribuye esa corrección al comportamiento de la aplicación para el usuario.

La advertencia de fuente de CustomTkinter persiste; usa su método alternativo de dibujo y las pruebas terminan correctamente.

El [informe de ampliación](#correccion-fotografia) conserva la descripción del error anterior del diálogo de fotografía fuera de pantalla y su corrección de escala/posición. `test_00_ampliacion_dentro_de_pantalla` volvió a aprobar en esta ejecución; no se recreó artificialmente el fallo antiguo ni se afirmó una ejecución de su versión previa.

### Diferencia respecto de las seis regresiones históricas

La suite `tests/test_revision.py` y su informe original `INFORME_REVISION.md` siguen ausentes. Sus seis resultados anteriores son antecedentes documentados en el README y la conversación, no ejecuciones actuales. Los 24 casos nuevos prueban la versión presente con código y datos nuevos; no se presentan como restauración de aquella evidencia.

### Límites y pendientes

- La nueva prueba de persistencia abre otro intérprete Python que lee el mismo TXT temporal; no es una demostración de cerrar y reabrir toda la interfaz con autenticación manual.
- No se prueban concurrencia entre escritores, cortes de energía, recuperación ante errores de disco, corrupción general de archivos, rendimiento ni matrices de todas las escalas de Windows.
- El test de contraseña verifica hash PBKDF2 y ausencia de la contraseña ficticia en el archivo de cuentas; no es una auditoría criptográfica ni sanea credenciales antiguas del historial Git.
- La suite del catálogo comprueba hashes detallados de las trece fotografías nuevas y abre las imágenes del catálogo activo; las verificaciones adicionales de las once sustituidas continúan documentadas en su [informe](#sustitucion-fotografias), sin atribuirlas como nuevos métodos.
- La selección/copia de fotografías desde el formulario administrativo y los flujos bancarios o de transporte no se ejecutaron: no forman parte de estas pruebas; los pagos son académicos.
- El informe no atribuye un porcentaje de cobertura de líneas o ramas; no se realizó esa medición.
- No hay pruebas omitidas en esta ejecución. Los límites anteriores son alcance no cubierto, no resultados aprobados ni pruebas pendientes contadas dentro de las 31.
- La validación con usuarios sigue en pausa; no se inventaron participantes ni resultados.

### Archivos de esta tarea

- Añadido: `tests/test_criticos.py`.
- Modificado: `tests/test_catalogo.py`, solo preparación y verificaciones de aislamiento; se conservan los siete casos originales.
- Añadidos: este informe y `registro de ejecución de 31 pruebas integrado en este README`.
- README, producción, datos originales, Excel, comprobantes y fotografías: intactos. Sin JSON, commits ni push.

</details>

<a id="registro-31-pruebas"></a>

### Registro completo de la ejecución de 31 pruebas

Salida histórica original conservada íntegramente. Los comandos y rutas de pruebas mencionados no indican disponibilidad de la suite en la entrega actual.

<details>
<summary>Ver registro completo de la ejecución de 31 pruebas</summary>

```text
Efrata Minimall - ejecución técnica final
Fecha de registro: 17 de noviembre de 2026
Python: 3.12.10
Sistema: Windows
customtkinter: 6.0.0
pandas: 3.0.6
openpyxl: 3.1.5
Pillow: 12.2.0
tkcalendar: 1.6.1

Comando: python -B -m unittest discover -s tests -v

customtkinter.windows.widgets.font warning: Preferred drawing method 'font_shapes' can not be used because the font file could not be loaded.
Using 'circle_shapes' instead. The rendering quality will be bad!
test_00_ampliacion_dentro_de_pantalla (test_catalogo.CatalogoAmpliado.test_00_ampliacion_dentro_de_pantalla) ... ok
test_01_catalogos_y_existencias (test_catalogo.CatalogoAmpliado.test_01_catalogos_y_existencias) ... ok
test_02_fotos_fuentes_y_apertura (test_catalogo.CatalogoAmpliado.test_02_fotos_fuentes_y_apertura) ... ok
test_03_busqueda_filtros_y_tarjetas (test_catalogo.CatalogoAmpliado.test_03_busqueda_filtros_y_tarjetas) ... ok
test_04_carrito_compra_y_stock (test_catalogo.CatalogoAmpliado.test_04_carrito_compra_y_stock) ... ok
test_05_alquiler_conflicto_y_registro_historico (test_catalogo.CatalogoAmpliado.test_05_alquiler_conflicto_y_registro_historico) ... ok
test_06_inventario_administrativo (test_catalogo.CatalogoAmpliado.test_06_inventario_administrativo) ... ok
test_01_registro_acceso_hash_duplicado (test_criticos.BackendCritico.test_01_registro_acceso_hash_duplicado)
Acceso | Registro, hash y duplicado | Cuenta única, hash PBKDF2 y acceso válido. ... ok
test_02_formatos_registro_invalidos (test_criticos.BackendCritico.test_02_formatos_registro_invalidos)
Acceso | Correo y contraseña inválidos | Rechazo sin escribir cuentas. ... ok
test_03_operaciones_sin_sesion_y_otro_usuario (test_criticos.BackendCritico.test_03_operaciones_sin_sesion_y_otro_usuario)
Seguridad | Sin sesión y cuenta ajena | PermissionError sin escrituras. ... ok
test_04_siete_campos_obligatorios (test_criticos.BackendCritico.test_04_siete_campos_obligatorios)
Perfil | Cada campo vacío individualmente | Compra y alquiler bloqueados sin escrituras. ... ok
test_05_perfil_ausente (test_criticos.BackendCritico.test_05_perfil_ausente)
Perfil | Perfil inexistente | Ambas operaciones bloqueadas sin archivos nuevos. ... ok
test_06_tres_metodos_y_estados (test_criticos.BackendCritico.test_06_tres_metodos_y_estados)
Pagos | Tres métodos y perfil válido | Método y estado conservados en ambas operaciones. ... ok
test_07_metodos_invalidos (test_criticos.BackendCritico.test_07_metodos_invalidos)
Pagos | Método no permitido | ValueError y datos temporales intactos. ... ok
test_08_carritos_separados (test_criticos.BackendCritico.test_08_carritos_separados)
Carrito | Dos usuarios ficticios | Compra de uno conserva el carrito del otro. ... ok
test_09_cantidades_invalidas (test_criticos.BackendCritico.test_09_cantidades_invalidas)
Carrito | Cero, negativos, fracciones y exceso | Rechazo sin modificar carrito ni stock. ... ok
test_10_compra_stock_exacto_comprobante_historial (test_criticos.BackendCritico.test_10_compra_stock_exacto_comprobante_historial)
Compra | Comprar todas las existencias | Stock cero, pedido y comprobante correctos; carrito vacío. ... ok
test_11_cancelacion (test_criticos.BackendCritico.test_11_cancelacion)
Compra | Cancelar confirmación | Inventario, carrito y registros sin cambios. ... ok
test_12_stock_reducido_antes_de_comprar (test_criticos.BackendCritico.test_12_stock_reducido_antes_de_comprar)
Compra | Inventario menor que carrito guardado | Compra rechazada y carrito conservado. ... ok
test_13_carrito_en_proceso_nuevo (test_criticos.BackendCritico.test_13_carrito_en_proceso_nuevo)
Persistencia | Leer carrito desde otro intérprete | Recuperar exactamente artículo, talla y cantidad. ... ok
test_14_fechas_invalidas (test_criticos.BackendCritico.test_14_fechas_invalidas)
Alquiler | Formatos, fecha pasada y devolución no posterior | Rechazo sin escrituras. ... ok
test_15_tallas_y_trajes_invalidos (test_criticos.BackendCritico.test_15_tallas_y_trajes_invalidos)
Alquiler | Talla inexistente y traje inactivo o ausente | Rechazo sin registros. ... ok
test_16_limites_revision_dos_dias (test_criticos.BackendCritico.test_16_limites_revision_dos_dias)
Disponibilidad | Último día de revisión y día siguiente | Rechazo hasta devolución +2; aceptación en +3. ... ok
test_17_devolucion_y_pago_conservado (test_criticos.BackendCritico.test_17_devolucion_y_pago_conservado)
Devolución | Devolver desde el día de inicio y repetir | Fecha real y pago conservados; repetición rechazada. ... ok
test_18_devolucion_anticipada (test_criticos.BackendCritico.test_18_devolucion_anticipada)
Devolución | Antes del inicio | Rechazo conservando el alquiler activo. ... ok
test_19_administracion_denegada (test_criticos.BackendCritico.test_19_administracion_denegada)
Administración | Cuenta normal | Consultas y modificación denegadas sin cambios. ... ok
test_20_administracion_autorizada (test_criticos.BackendCritico.test_20_administracion_autorizada)
Administración | Consultar y modificar copias | Operaciones visibles y existencias actualizadas sin perder registros. ... ok
test_21_tarjetas_invalidas_formularios (test_criticos.Formularios.test_21_tarjetas_invalidas_formularios)
Interfaz | Tarjetas incompletas e inválidas | Ambos formularios rechazan sin escrituras. ... ok
test_22_compra_y_alquiler_desde_formularios (test_criticos.Formularios.test_22_compra_y_alquiler_desde_formularios)
Integración gráfica | Enviar widgets reales con tres métodos | Pedido, comprobante, stock y alquiler persistidos; tarjeta no guardada. ... ok
test_23_panel_administrativo_real (test_criticos.Formularios.test_23_panel_administrativo_real)
Interfaz administrativa | Panel autorizado | Panel visible y consulta del inventario temporal. ... ok
test_24_edicion_administrativa_formulario (test_criticos.Formularios.test_24_edicion_administrativa_formulario)
Integración administrativa | Guardar edición de traje desde widgets | Precio y descripción persisten en Excel temporal. ... ok

----------------------------------------------------------------------
Ran 31 tests in 31.841s

OK

Código de salida unittest: 0
Compilación en memoria: 16 archivos Python correctos; sin generar bytecode.
Integridad SHA-256: todos los archivos del proyecto sin cambios durante las pruebas.
Comando: git diff --check
Código de salida diff: 0
Salida diff: (sin salida)
Advertencias diff: (ninguna)

Los datos y credenciales usados por los casos son ficticios. No se guardan rutas personales en este registro.
```

</details>

### Caso adicional de presentación — resultado histórico 32

| Función y caso | Resultado esperado | Resultado obtenido | Evidencia | Estado histórico |
| --- | --- | --- | --- | --- |
| `test_25_etiquetas_y_compatibilidad_historica` | Mostrar «No procesado» y el indicador «Valor de pedidos registrados»; leer estados históricos sin reescribir registros. | La ejecución registró `ok` para la compatibilidad de estados y las etiquetas nuevas. | Registro íntegro de 32 pruebas incluido a continuación. | Aprobado antes de retirar la suite. |

<a id="registro-32-pruebas"></a>

### Registro completo de la ejecución final de 32 pruebas

Salida histórica original conservada íntegramente. Los comandos y rutas de pruebas mencionados no indican disponibilidad de la suite en la entrega actual.

<details>
<summary>Ver registro completo de la ejecución final de 32 pruebas</summary>

```text
Ejecución antes de retirar la suite. Resultado histórico; los archivos de pruebas serán eliminados.
Comando ejecutado: python -B -m unittest discover -s tests -v

customtkinter.windows.widgets.font warning: Preferred drawing method 'font_shapes' can not be used because the font file could not be loaded.
Using 'circle_shapes' instead. The rendering quality will be bad!
test_00_ampliacion_dentro_de_pantalla (test_catalogo.CatalogoAmpliado.test_00_ampliacion_dentro_de_pantalla) ... ok
test_01_catalogos_y_existencias (test_catalogo.CatalogoAmpliado.test_01_catalogos_y_existencias) ... ok
test_02_fotos_fuentes_y_apertura (test_catalogo.CatalogoAmpliado.test_02_fotos_fuentes_y_apertura) ... ok
test_03_busqueda_filtros_y_tarjetas (test_catalogo.CatalogoAmpliado.test_03_busqueda_filtros_y_tarjetas) ... ok
test_04_carrito_compra_y_stock (test_catalogo.CatalogoAmpliado.test_04_carrito_compra_y_stock) ... ok
test_05_alquiler_conflicto_y_registro_historico (test_catalogo.CatalogoAmpliado.test_05_alquiler_conflicto_y_registro_historico) ... ok
test_06_inventario_administrativo (test_catalogo.CatalogoAmpliado.test_06_inventario_administrativo) ... ok
test_01_registro_acceso_hash_duplicado (test_criticos.BackendCritico.test_01_registro_acceso_hash_duplicado)
Acceso | Registro, hash y duplicado | Cuenta única, hash PBKDF2 y acceso válido. ... ok
test_02_formatos_registro_invalidos (test_criticos.BackendCritico.test_02_formatos_registro_invalidos)
Acceso | Correo y contraseña inválidos | Rechazo sin escribir cuentas. ... ok
test_03_operaciones_sin_sesion_y_otro_usuario (test_criticos.BackendCritico.test_03_operaciones_sin_sesion_y_otro_usuario)
Seguridad | Sin sesión y cuenta ajena | PermissionError sin escrituras. ... ok
test_04_siete_campos_obligatorios (test_criticos.BackendCritico.test_04_siete_campos_obligatorios)
Perfil | Cada campo vacío individualmente | Compra y alquiler bloqueados sin escrituras. ... ok
test_05_perfil_ausente (test_criticos.BackendCritico.test_05_perfil_ausente)
Perfil | Perfil inexistente | Ambas operaciones bloqueadas sin archivos nuevos. ... ok
test_06_tres_metodos_y_estados (test_criticos.BackendCritico.test_06_tres_metodos_y_estados)
Pagos | Tres métodos y perfil válido | Método y estado conservados en ambas operaciones. ... ok
test_07_metodos_invalidos (test_criticos.BackendCritico.test_07_metodos_invalidos)
Pagos | Método no permitido | ValueError y datos temporales intactos. ... ok
test_08_carritos_separados (test_criticos.BackendCritico.test_08_carritos_separados)
Carrito | Dos usuarios ficticios | Compra de uno conserva el carrito del otro. ... ok
test_09_cantidades_invalidas (test_criticos.BackendCritico.test_09_cantidades_invalidas)
Carrito | Cero, negativos, fracciones y exceso | Rechazo sin modificar carrito ni stock. ... ok
test_10_compra_stock_exacto_comprobante_historial (test_criticos.BackendCritico.test_10_compra_stock_exacto_comprobante_historial)
Compra | Comprar todas las existencias | Stock cero, pedido y comprobante correctos; carrito vacío. ... ok
test_11_cancelacion (test_criticos.BackendCritico.test_11_cancelacion)
Compra | Cancelar confirmación | Inventario, carrito y registros sin cambios. ... ok
test_12_stock_reducido_antes_de_comprar (test_criticos.BackendCritico.test_12_stock_reducido_antes_de_comprar)
Compra | Inventario menor que carrito guardado | Compra rechazada y carrito conservado. ... ok
test_13_carrito_en_proceso_nuevo (test_criticos.BackendCritico.test_13_carrito_en_proceso_nuevo)
Persistencia | Leer carrito desde otro intérprete | Recuperar exactamente artículo, talla y cantidad. ... ok
test_14_fechas_invalidas (test_criticos.BackendCritico.test_14_fechas_invalidas)
Alquiler | Formatos, fecha pasada y devolución no posterior | Rechazo sin escrituras. ... ok
test_15_tallas_y_trajes_invalidos (test_criticos.BackendCritico.test_15_tallas_y_trajes_invalidos)
Alquiler | Talla inexistente y traje inactivo o ausente | Rechazo sin registros. ... ok
test_16_limites_revision_dos_dias (test_criticos.BackendCritico.test_16_limites_revision_dos_dias)
Disponibilidad | Último día de revisión y día siguiente | Rechazo hasta devolución +2; aceptación en +3. ... ok
test_17_devolucion_y_pago_conservado (test_criticos.BackendCritico.test_17_devolucion_y_pago_conservado)
Devolución | Devolver desde el día de inicio y repetir | Fecha real y pago conservados; repetición rechazada. ... ok
test_18_devolucion_anticipada (test_criticos.BackendCritico.test_18_devolucion_anticipada)
Devolución | Antes del inicio | Rechazo conservando el alquiler activo. ... ok
test_19_administracion_denegada (test_criticos.BackendCritico.test_19_administracion_denegada)
Administración | Cuenta normal | Consultas y modificación denegadas sin cambios. ... ok
test_20_administracion_autorizada (test_criticos.BackendCritico.test_20_administracion_autorizada)
Administración | Consultar y modificar copias | Operaciones visibles y existencias actualizadas sin perder registros. ... ok
test_21_tarjetas_invalidas_formularios (test_criticos.Formularios.test_21_tarjetas_invalidas_formularios)
Interfaz | Tarjetas incompletas e inválidas | Ambos formularios rechazan sin escrituras. ... ok
test_22_compra_y_alquiler_desde_formularios (test_criticos.Formularios.test_22_compra_y_alquiler_desde_formularios)
Integración gráfica | Enviar widgets reales con tres métodos | Pedido, comprobante, stock y alquiler persistidos; tarjeta no guardada. ... ok
test_23_panel_administrativo_real (test_criticos.Formularios.test_23_panel_administrativo_real)
Interfaz administrativa | Panel autorizado | Panel visible y consulta del inventario temporal. ... ok
test_24_edicion_administrativa_formulario (test_criticos.Formularios.test_24_edicion_administrativa_formulario)
Integración administrativa | Guardar edición de traje desde widgets | Precio y descripción persisten en Excel temporal. ... ok
test_25_etiquetas_y_compatibilidad_historica (test_criticos.Formularios.test_25_etiquetas_y_compatibilidad_historica)
Presentación | Estados históricos y etiquetas nuevas | Mostrar No procesado sin reescribir registros; indicador de pedidos claro. ... ok

----------------------------------------------------------------------
Ran 32 tests in 29.888s

OK

Verificaciones posteriores a la simplificación (18 de noviembre de 2026):
- Inicialización en directorio temporal: ocho TXT vacíos creados desde las plantillas; archivo existente conservado al reinicializar.
- Copia temporal de los archivos públicos actuales, sin cuentas ni comprobantes privados: entrada main.py ejecutada; interfaz Tk abierta y cerrada mediante temporizador, sin operaciones de negocio.
- Aviso de CustomTkinter: fuente font_shapes no disponible; utilizó circle_shapes. No impidió el arranque.
- Compilación en memoria de los 14 archivos Python restantes: correcta, sin generar bytecode.
- Cuatro capturas del README abiertas y verificadas con Pillow; 17 enlaces relativos de README e informes Markdown resueltos.
- Integridad SHA-256: 58 archivos de datos, comprobantes, fotografías y capturas sin cambios; respaldo completo con .git sin cambios.
```

</details>

## Comprobación de la documentación unificada

El 18 de noviembre de 2026 se comprobaron las cuatro capturas mediante Pillow, los enlaces relativos y las anclas internas de este documento. Los seis textos anteriores se integraron antes de retirar su carpeta: los tres registros TXT se conservan íntegros en los desplegables y los tres informes mantienen sus casos, resultados, correcciones y limitaciones, con enlaces internos y contexto histórico actualizado.

La aplicación se abrió y cerró mediante un temporizador en una copia temporal de los archivos públicos sin la antigua carpeta de documentación, cuentas ni comprobantes privados. La inicialización creó los ocho TXT operativos vacíos. No se realizaron compras, alquileres ni cambios administrativos en los datos originales, ni se volvió a ejecutar la suite eliminada. Persistió la advertencia conocida de CustomTkinter sobre `font_shapes`, con uso alternativo de `circle_shapes`; no impidió el arranque.

## Limitaciones y mejoras futuras

- **Uso local:** los datos se almacenan en TXT y Excel; no hay base de datos centralizada ni sincronización entre equipos.
- **Pagos:** los formularios de tarjeta son académicos y no procesan transacciones bancarias.
- **Entregas:** no hay integración con servicios de transporte ni seguimiento real de envíos.
- **Fotografías de referencia:** las imágenes del catálogo no corresponden necesariamente a las prendas y trajes físicos del negocio; se utilizan para demostrar las funciones.
- **Arreglos de ropa:** es un servicio del negocio, pero no cuenta con un módulo de gestión dentro del programa.
- **Seguridad y escalabilidad:** los permisos administrativos dependen de archivos locales. Esta versión está pensada para demostración académica y no para operación comercial en red.

Como mejoras futuras podrían considerarse una base de datos, fotografías propias del inventario con autorización del negocio, una gestión específica de arreglos y servicios de pagos o entregas integrados, siempre que se adapte primero el proyecto a los requisitos de seguridad correspondientes.

## Recorrido sugerido para la sustentación

Se recomienda hacer una demostración de principio a fin **con datos ficticios y una copia del proyecto**, de manera que los registros originales no se vean afectados:

1. **Acceso:** registrar o iniciar sesión y explicar las diferencias entre las cuentas de cliente y administrador.
2. **Catálogo y carrito:** buscar una prenda, filtrar, elegir talla y añadirla al carrito.
3. **Compra y validaciones:** intentar confirmar sin los datos personales completos; completarlos, finalizar la compra y mostrar comprobante, estado de pago e inventario actualizado.
4. **Alquiler:** seleccionar traje y talla, comprobar fechas disponibles y registrar la operación.
5. **Administración:** consultar compras, alquileres, clientes y existencias; mostrar una modificación de prueba.
6. **Cierre:** relacionar las operaciones mostradas con los requisitos de aceptación, las pruebas realizadas y las limitaciones del sistema.

## Créditos académicos

- **Universidad:** Universidad Autónoma de Occidente (UAO).
- **Asignatura:** Algoritmia y Programación.
- **Año:** 2026.
- **Integrantes:** Isabella Caro Giraldo y Allison Castrillón Núñez.
- **Docente:** Juan Manuel Nuñez Velasco.

> **Trabajo de campo:** los participantes, las evidencias generales y los cambios realizados a partir de sus comentarios se presentan en [Validación con usuarios y mejoras](#validación-con-usuarios-y-mejoras). La comprobación de los avisos fue realizada por una integrante del equipo; no se documentó una nueva sesión con los usuarios después del cambio. La publicación de imágenes identificables requiere verificar las autorizaciones correspondientes.
