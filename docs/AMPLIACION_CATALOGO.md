# Ampliación del catálogo de demostración

> **Informe histórico:** la suite fue retirada durante la simplificación de la entrega. Los comandos y nombres de pruebas de este informe documentan ejecuciones anteriores; no son instrucciones reproducibles con la estructura actual. La [última ejecución antes de retirarla](RESULTADOS_PRUEBAS_ANTES_SIMPLIFICACION.txt) confirmó 32 pruebas aprobadas.

Fecha: 17 de noviembre de 2026.

## Resultado

- Ropa: 6 → 14 prendas; activas: 5 → 13. La prenda inactiva se conserva.
- Existencias de ropa: 16 → 44 variantes. Las 28 variantes nuevas tienen cantidades positivas.
- Alquiler: 5 → 10 trajes activos. Los trajes se reservan por código, talla y fechas; el modelo no maneja cantidades por talla de traje.
- Precios y existencias nuevos son ficticios, en pesos colombianos; no representan inventario confirmado del negocio.

## Respaldo y conservación

Antes de editar los Excel se guardaron y verificaron copias byte a byte en la carpeta privada `Efrata_respaldo_catalogo_20261117`, situada en Descargas y fuera del repositorio. Las filas originales de todas las hojas se compararon con esas copias y no cambiaron. Los registros de operaciones, cuentas, datos personales y comprobantes se mantuvieron intactos.

## Prendas añadidas

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

## Trajes añadidos

| Código | Traje | Alquiler COP | Tallas |
| --- | --- | ---: | --- |
| T006 | Traje Azul Ceremonia Demo | 160,000 | S, M, L, XL |
| T007 | Traje Beige Balcón Demo | 145,000 | S, M, L |
| T008 | Traje Negro Ejecutivo Demo | 155,000 | M, L, XL |
| T009 | Esmoquin Gala Demo | 185,000 | S, M, L |
| T010 | Traje Gris Urbano Demo | 150,000 | S, M, L, XL |

## Fotografías y licencias

Se incorporaron trece JPEG distintos. Se verificó la indicación «Free» en las fichas de Pexels y la [licencia oficial](https://www.pexels.com/license/), que permite descargarlas, usarlas y modificarlas, con restricciones como no sugerir respaldo de las personas o marcas retratadas. Se usan exclusivamente como referencias académicas, sin atribuirles relación con el negocio. Las fotografías no son prueba de características físicas, composición ni disponibilidad de productos reales.

Se conservaron las proporciones, sin recorte, con lado mayor de 1600 píxeles, calidad JPEG 88 y sin EXIF. Peso total: 3.79 MiB. El manifiesto `catalogo_referencia.txt` registra códigos, autores, fichas originales, URL de descarga, licencia, fecha, resolución y SHA-256 de cada archivo.

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

En esta ampliación se conservaron las once fotografías históricas, entonces sin permisos verificados. Posteriormente se sustituyeron por referencias de Pexels; véase [Sustitución de fotografías y revisión del logotipo](SUSTITUCION_FOTOGRAFIAS.md). Las trece fotografías añadidas en la ampliación se mantienen intactas. Los derechos del logotipo siguen pendientes de confirmación.

## Corrección mínima de interfaz

Se reprodujo un fallo en la ampliación: con la ventana principal próxima al borde inferior, el diálogo de fotografía salía de la pantalla. La prueba inicial falló porque su borde inferior superaba la altura disponible. Se ajustó únicamente `ampliar_fotografia` para considerar la escala de CustomTkinter en el tamaño de foto y ventana, y limitar las coordenadas a la pantalla. No se alteró la organización general de la interfaz.

## Pruebas

Ejecutar desde la carpeta principal, con las dependencias gráficas instaladas y una sesión de escritorio disponible:

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

## Archivos de esta tarea

- Modificados: `data/ropa.xlsx`, `data/inventario.xlsx` y la función `ampliar_fotografia` en `frontend/app.py`.
- Añadidos: trece fotos identificadas arriba, `docs/catalogo_referencia.txt`, este informe y `tests/test_catalogo.py`.
- README, código restante, fotografías históricas y registros operativos: sin modificaciones durante esta tarea.
- Sin commits ni push.

## Pendientes y límites

- Sustitución de las once imágenes históricas completada posteriormente; la autorización del logotipo sigue pendiente (véase el informe de sustitución).
- La advertencia de fuente de CustomTkinter persiste en este entorno; utiliza su método alternativo de dibujo y no impidió las pruebas.
- Las licencias se comprobaron en las fuentes oficiales; la correspondencia visual es de referencia, no una certificación de productos del negocio.
- Los riesgos de privacidad del historial Git señalados en la auditoría anterior no se han corregido: esta tarea no autorizaba sanearlo.
