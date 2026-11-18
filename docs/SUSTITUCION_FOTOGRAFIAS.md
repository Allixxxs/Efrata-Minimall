# Sustitución de fotografías y revisión del logotipo

Fecha: 17 de noviembre de 2026.

## Resultado

Se sustituyeron las once fotografías indicadas, conservando sus códigos y nombres de archivo. No quedan reemplazos fotográficos pendientes. Las trece fotografías de la ampliación anterior se conservaron sin cambios. Los catálogos siguen teniendo 14 prendas (13 activas y una inactiva) y 10 trajes.

Se consultaron `data/ropa.xlsx` y `data/inventario.xlsx` antes de seleccionar referencias. No se editaron esos archivos. Las nuevas fotografías ilustran tipos y estilos de prendas; no certifican composición, ligereza, ajuste ni existencias de productos reales del negocio.

## Reemplazos y fuentes

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

## Permisos y tratamiento

En cada ficha oficial se comprobó la indicación «Free» o «Free to use». Se consultó la [licencia oficial de Pexels](https://www.pexels.com/license/): permite descargar, utilizar y modificar fotografías, sin exigir atribución, con restricciones como no sugerir respaldo de las personas o marcas retratadas y no redistribuirlas como un banco de imágenes. Los créditos se conservan voluntariamente.

Se revisaron visualmente las once referencias y no se observaron marcas de agua. Se descartaron opciones en las que la prenda se veía demasiado pequeña o aparecía una marca destacada en el fondo. Se mantuvieron las proporciones originales sin recortar; la optimización fue JPEG, calidad 88, lado mayor 1600 píxeles y sin EXIF.

El registro completo está en `docs/catalogo_referencia.txt`: código, archivo, identificador de Pexels, autor, ficha y descarga original, licencia, fecha de verificación, dimensiones, tamaño y SHA-256. Las once fichas de reemplazo se guardan como valores multilínea de la sección general, conservando las secciones originales para no cambiar el lector de pruebas.

Peso conjunto de los once reemplazos: 2.22 MiB.

## Respaldo privado

Las once imágenes originales se copiaron, antes de sustituirlas, a la carpeta `Efrata_respaldo_fotos_20261117` en Descargas, fuera del repositorio. Se verificó la igualdad byte a byte y se guardó un registro privado `SHA256.txt`. El respaldo no debe incorporarse a la entrega pública.

## Verificaciones ejecutadas

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

## Archivos de esta tarea

- Sustituidos: los once JPEG listados en la tabla.
- Actualizados: `docs/catalogo_referencia.txt` y las notas de estado en `docs/AMPLIACION_CATALOGO.md`.
- Añadido: este informe.
- No se incorporaron archivos JSON, ni se modificaron Excel, README, fotografías nuevas, código Python u operaciones existentes. Sin commits ni push.

## Revisión separada del logotipo

Archivo: `frontend/imagenes/efrata_logo_ui.png`. Se conservó sin cambios.

Se inspeccionó visualmente el PNG y sus metadatos, se revisaron las referencias del proyecto y el historial Git local. El archivo mide 436 × 281 píxeles y no aporta campos de autoría ni EXIF. El historial contiene una incorporación del recurso y un checkpoint posterior; eso acredita su presencia en el proyecto, no la autoría del diseño ni una autorización.

Un README histórico enlazaba una imagen alojada como adjunto de GitHub. Ese alojamiento no constituye por sí mismo una licencia ni permite establecer con certeza el origen del PNG actual. La búsqueda pública por el nombre del negocio tampoco aportó una fuente concluyente. No se encontró documentación que identifique autor, licencia de los adornos o tipografía, archivo editable original o permiso del titular.

**Estado: derechos de uso del logotipo no confirmados.** No se afirma que infrinja derechos, pero tampoco que sea de libre uso. Queda pendiente obtener del negocio o de quien lo diseñó una confirmación de autoría y autorización para la publicación académica, junto con las licencias de los recursos utilizados cuando corresponda. No se sustituyó ni se atribuyó una licencia de Pexels al logotipo.
