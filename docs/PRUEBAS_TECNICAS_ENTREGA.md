# Evidencias técnicas de la entrega académica

> **Informe histórico:** la suite fue retirada durante la simplificación de la entrega. Los comandos y nombres de pruebas de este informe documentan ejecuciones anteriores; no son instrucciones reproducibles con la estructura actual. La [última ejecución antes de retirarla](RESULTADOS_PRUEBAS_ANTES_SIMPLIFICACION.txt) confirmó 32 pruebas aprobadas.

Efrata Minimall — Universidad Autónoma de Occidente, Algoritmia y Programación, 2026.

## Objetivo y resultado

Ampliar la evidencia reproducible de funciones críticas, entradas válidas, inválidas, límites e integración sin alterar producción ni datos originales. No se reconstruyeron resultados históricos.

**Resultado final: 31 pruebas ejecutadas, 31 aprobadas, 0 fallidas, 0 errores y 0 omitidas.** Había siete pruebas; se conservaron sus casos y se añadieron 24. Los subcasos de cada método no se cuentan como pruebas independientes.

## Entorno y reproducción

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

La salida completa de la ejecución final está en [RESULTADOS_PRUEBAS_TECNICAS.txt](RESULTADOS_PRUEBAS_TECNICAS.txt). El comando de unittest terminó con código cero: `Ran 31 tests in 31.841s`, `OK`. Se verificó la compilación de los 16 archivos Python con `compile()` en memoria, sin producir bytecode. `git diff --check` terminó con código cero y sin errores.

## Aislamiento y datos de prueba

- Cada caso nuevo crea un directorio temporal distinto y dos Excel totalmente sintéticos: una prenda activa con cinco unidades, otra inactiva, un traje activo y otro inactivo. No copia cuentas u operaciones reales.
- Antes de ejecutar operaciones se parchean todas las constantes Path de archivos y directorios importadas por los módulos del backend. Cada ruta resultante debe estar dentro del directorio temporal; una aserción impide continuar si no lo está.
- Perfiles, cuentas, contraseñas y últimos cuatro dígitos son ficticios. No se usan tarjetas reales.
- Las siete pruebas anteriores mantienen sus aserciones y su inventario de referencia; su preparación ahora repone las copias temporales y vacía los registros temporales antes de cada caso para no depender de operaciones anteriores.
- Cada caso comprueba hashes SHA-256 de los datos originales antes/después o contra la línea base de su clase. La ejecución final también comparó todos los archivos del proyecto antes y después de correr y compilar: no hubo cambios.
- Los parches, sesiones y directorios temporales se limpian incluso cuando una aserción falla. Las pruebas gráficas cancelan callbacks Tk pendientes antes de destruir su raíz.
- En pruebas gráficas solo se sustituyen avisos informativos y la respuesta del diálogo de confirmación. Los validadores, callbacks de envío, backend y persistencia reales permanecen activos.

## Siete pruebas conservadas

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

## Veinticuatro pruebas nuevas

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

## Integración gráfica ejecutada

- **Compra:** se rellenan campos reales de titular y cuatro dígitos, se selecciona el método y se ejecuta el callback real `comprar`. Se verifican pedido, estado de pago, comprobante, inventario y carrito en archivos temporales.
- **Alquiler:** se rellenan talla, fechas y método en widgets reales y se ejecuta `confirmar_alquiler_interfaz`. Se comprueba el registro TXT leído por el backend.
- **Administración:** se abre el panel autorizado y un formulario real de edición de traje. Se editan sus campos y se invoca el botón Guardar traje; se vuelve a leer precio y descripción del Excel temporal.
- No se automatizan movimientos de ratón o teclado físico ni se afirma una inspección visual humana de todos los formularios. Se ejecutan sus controles/callbacks programáticamente con Tk real.

## Errores, correcciones y repetición

No se detectaron nuevos fallos de producción con los casos ejecutados y no se modificó código de producción.

Durante la preparación de la nueva infraestructura se observaron avisos de callbacks Tk pendientes al destruir y recrear raíces entre pruebas. Se corrigió la limpieza en las pruebas, cancelando los eventos pendientes. La ejecución final de 31 casos no contiene esos avisos. No se atribuye esa corrección al comportamiento de la aplicación para el usuario.

La advertencia de fuente de CustomTkinter persiste; usa su método alternativo de dibujo y las pruebas terminan correctamente.

El [informe de ampliación](AMPLIACION_CATALOGO.md#corrección-mínima-de-interfaz) conserva la descripción del error anterior del diálogo de fotografía fuera de pantalla y su corrección de escala/posición. `test_00_ampliacion_dentro_de_pantalla` volvió a aprobar en esta ejecución; no se recreó artificialmente el fallo antiguo ni se afirmó una ejecución de su versión previa.

## Diferencia respecto de las seis regresiones históricas

La suite `tests/test_revision.py` y su informe original `INFORME_REVISION.md` siguen ausentes. Sus seis resultados anteriores son antecedentes documentados en el README y la conversación, no ejecuciones actuales. Los 24 casos nuevos prueban la versión presente con código y datos nuevos; no se presentan como restauración de aquella evidencia.

## Límites y pendientes

- La nueva prueba de persistencia abre otro intérprete Python que lee el mismo TXT temporal; no es una demostración de cerrar y reabrir toda la interfaz con autenticación manual.
- No se prueban concurrencia entre escritores, cortes de energía, recuperación ante errores de disco, corrupción general de archivos, rendimiento ni matrices de todas las escalas de Windows.
- El test de contraseña verifica hash PBKDF2 y ausencia de la contraseña ficticia en el archivo de cuentas; no es una auditoría criptográfica ni sanea credenciales antiguas del historial Git.
- La suite del catálogo comprueba hashes detallados de las trece fotografías nuevas y abre las imágenes del catálogo activo; las verificaciones adicionales de las once sustituidas continúan documentadas en su [informe](SUSTITUCION_FOTOGRAFIAS.md), sin atribuirlas como nuevos métodos.
- La selección/copia de fotografías desde el formulario administrativo y los flujos bancarios o de transporte no se ejecutaron: no forman parte de estas pruebas; los pagos son académicos.
- El informe no atribuye un porcentaje de cobertura de líneas o ramas; no se realizó esa medición.
- No hay pruebas omitidas en esta ejecución. Los límites anteriores son alcance no cubierto, no resultados aprobados ni pruebas pendientes contadas dentro de las 31.
- La validación con usuarios sigue en pausa; no se inventaron participantes ni resultados.

## Archivos de esta tarea

- Añadido: `tests/test_criticos.py`.
- Modificado: `tests/test_catalogo.py`, solo preparación y verificaciones de aislamiento; se conservan los siete casos originales.
- Añadidos: este informe y `docs/RESULTADOS_PRUEBAS_TECNICAS.txt`.
- README, producción, datos originales, Excel, comprobantes y fotografías: intactos. Sin JSON, commits ni push.
