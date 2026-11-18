"""Casos nuevos de la versión actual; no reconstruyen la suite histórica eliminada."""
import datetime as dt
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from openpyxl import Workbook
import backend
from backend import administracion as admin, alquileres, carrito, catalogo, compras
from backend import datos_personales as perfiles, usuarios
from backend.sesion import sesion_actual

RAIZ = Path(__file__).resolve().parents[1]
CLIENTE = "cliente.prueba@gmail.com"
OTRO = "segunda.prueba@hotmail.com"
ADMIN = "admin.prueba@gmail.com"
CLAVE = "EjemploFicticio123"
PERFIL = dict(Nombre="Ana", Apellidos="Prueba", Telefono="3000000000",
              TipoDocumento="CC", NumeroDocumento="10000000",
              Direccion="Dirección ficticia", CodigoPostal="110111")
METODOS = ("Efectivo al recibir", "Tarjeta de crédito", "Tarjeta débito")


def huellas(base):
    return {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in base.rglob("*") if p.is_file()}


def originales():
    return {carpeta: huellas(RAIZ / carpeta) for carpeta in ("data", "comprobantes")}


def redirigir(base):
    """Parchear todas las copias importadas, antes de abrir la interfaz u operar."""
    parches = []
    for modulo in list(sys.modules.values()):
        if getattr(modulo, "__name__", "").startswith("backend"):
            for nombre, valor in list(vars(modulo).items()):
                if isinstance(valor, Path) and nombre.startswith(("ARCHIVO_", "DIRECTORIO_")):
                    destino = (base / "data" / valor.name if nombre.startswith("ARCHIVO_")
                               else base / "data" if nombre == "DIRECTORIO_DATOS"
                               else base / "comprobantes" if nombre == "DIRECTORIO_COMPROBANTES"
                               else base)
                    parche = patch.object(modulo, nombre, destino)
                    parche.start()
                    parches.append(parche)
    return parches


class Aislada(unittest.TestCase):
    def setUp(self):
        self.antes = originales()
        self.addCleanup(self.comprobar_originales)
        self.tmp = tempfile.TemporaryDirectory(prefix="efrata_criticos_")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        (self.base / "data").mkdir()
        self.sesion_previa = vars(sesion_actual).copy()
        self.addCleanup(lambda: vars(sesion_actual).update(self.sesion_previa))
        self.parches = redirigir(self.base)
        for parche in self.parches:
            self.addCleanup(parche.stop)
        for modulo in list(sys.modules.values()):
            if getattr(modulo, "__name__", "").startswith("backend"):
                for nombre, valor in vars(modulo).items():
                    if isinstance(valor, Path) and nombre.startswith(("ARCHIVO_", "DIRECTORIO_")):
                        self.assertTrue(valor.is_relative_to(self.base), nombre)
        # Libros enteramente sintéticos: no se leen datos operativos originales.
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Productos"
        hoja.append(["Codigo", "Nombre", "Seccion", "Tipo", "Precio", "Estado", "Descripcion"])
        hoja.append(["P1", "Camisa de prueba", "Unisex", "Camisa", 50000, "Activo", "Referencia ficticia"])
        hoja.append(["P2", "Prenda inactiva", "Mujer", "Blusa", 10000, "Inactivo", "Referencia ficticia"])
        hoja = libro.create_sheet("Existencias")
        hoja.append(["Codigo", "Talla", "Cantidad"])
        hoja.append(["P1", "M", 5])
        hoja.append(["P2", "M", 2])
        libro.save(compras.ARCHIVO_ROPA)
        libro.close()
        libro = Workbook()
        hoja = libro.active
        hoja.append(["Codigo", "Nombre", "Tallas", "Precio", "Estado", "Descripcion"])
        hoja.append(["T1", "Traje de prueba", "M, L", 100000, "Activo", "Referencia ficticia"])
        hoja.append(["T2", "Traje inactivo", "M", 80000, "Inactivo", "Referencia ficticia"])
        libro.save(catalogo.ARCHIVO_INVENTARIO_TRAJES)
        libro.close()
        admin.ARCHIVO_ADMINISTRADORES.write_text(ADMIN + "\n", encoding="utf-8")
        self.sesion(CLIENTE)
        perfiles.guardar_datos_personales(CLIENTE, PERFIL)

    def comprobar_originales(self):
        self.assertEqual(originales(), self.antes, "Cambió un archivo operativo original")

    def sesion(self, correo):
        sesion_actual.correo = correo
        sesion_actual.activa = True
        sesion_actual.contrasena = ""

    def stock(self):
        return catalogo.cargar_catalogo_ropa()[0]["Tallas"][0]["Cantidad"]

    def fechas(self, dias=10):
        inicio = dt.date.today() + dt.timedelta(days=dias)
        return inicio.strftime("%d/%m/%Y"), (inicio + dt.timedelta(days=1)).strftime("%d/%m/%Y")

    def alquilar(self, metodo=METODOS[0], dias=10):
        return alquileres.registrar_alquiler(CLIENTE, "T1", "M", *self.fechas(dias), metodo)


class BackendCritico(Aislada):
    def test_01_registro_acceso_hash_duplicado(self):
        """Acceso | Registro, hash y duplicado | Cuenta única, hash PBKDF2 y acceso válido."""
        usuarios.registrar_usuario(CLIENTE, CLAVE)
        guardado = usuarios.ARCHIVO_USUARIOS.read_text(encoding="utf-8")
        self.assertNotIn(CLAVE, guardado)
        self.assertTrue(guardado.split("|")[1].startswith("pbkdf2$"))
        with self.assertRaises(ValueError):
            usuarios.registrar_usuario(CLIENTE.upper(), CLAVE)
        usuarios.cerrar_sesion()
        self.assertFalse(usuarios.autenticar_usuario(CLIENTE, "Incorrecta123"))
        self.assertFalse(sesion_actual.activa)
        self.assertTrue(usuarios.autenticar_usuario(CLIENTE, CLAVE))
        self.assertEqual(sesion_actual.correo, CLIENTE)
        self.assertEqual(len(usuarios.ARCHIVO_REGISTRO_SESIONES.read_text().splitlines()), 2)

    def test_02_formatos_registro_invalidos(self):
        """Acceso | Correo y contraseña inválidos | Rechazo sin escribir cuentas."""
        antes = huellas(self.base)
        for correo in ("", "sin-arroba", "a@@gmail.com", "a b@gmail.com", "a@gmail.com\nX", "a|b@gmail.com"):
            with self.subTest(correo=correo), self.assertRaises(ValueError):
                usuarios.registrar_usuario(correo, CLAVE)
        for clave in ("", "Ab1", "sinmayuscula1", "SINMINUSCULA1", "SinNumero", "Valida123\n"):
            with self.subTest(tipo="clave inválida"), self.assertRaises(ValueError):
                usuarios.registrar_usuario(CLIENTE, clave)
        self.assertEqual(huellas(self.base), antes)

    def test_03_operaciones_sin_sesion_y_otro_usuario(self):
        """Seguridad | Sin sesión y cuenta ajena | PermissionError sin escrituras."""
        antes = huellas(self.base)
        usuarios.cerrar_sesion()
        for operacion in (lambda: carrito.leer_carrito(CLIENTE),
                          lambda: compras.confirmar_compra(CLIENTE, True), self.alquilar,
                          admin.cargar_inventario_administracion):
            with self.assertRaises(PermissionError):
                operacion()
        self.sesion(CLIENTE)
        with self.assertRaises(PermissionError):
            carrito.leer_carrito(OTRO)
        self.assertEqual(huellas(self.base), antes)

    def test_04_siete_campos_obligatorios(self):
        """Perfil | Cada campo vacío individualmente | Compra y alquiler bloqueados sin escrituras."""
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
        for clave, etiqueta in perfiles.CAMPOS_DATOS_PERSONALES_OBLIGATORIOS:
            with self.subTest(campo=clave):
                datos = dict(PERFIL, **{clave: " "})
                perfiles.ARCHIVO_DATOS_PERSONALES.write_text("|".join([CLIENTE] + list(datos.values())) + "\n", encoding="utf-8")
                antes = huellas(self.base)
                self.assertIn(etiqueta, perfiles.campos_personales_faltantes(CLIENTE))
                self.assertFalse(compras.confirmar_compra(CLIENTE, True)["ok"])
                with self.assertRaises(ValueError):
                    self.alquilar()
                self.assertEqual(huellas(self.base), antes)

    def test_05_perfil_ausente(self):
        """Perfil | Perfil inexistente | Ambas operaciones bloqueadas sin archivos nuevos."""
        perfiles.ARCHIVO_DATOS_PERSONALES.unlink()
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
        antes = huellas(self.base)
        self.assertFalse(compras.confirmar_compra(CLIENTE, True)["ok"])
        with self.assertRaises(ValueError):
            self.alquilar()
        self.assertEqual(huellas(self.base), antes)

    def test_06_tres_metodos_y_estados(self):
        """Pagos | Tres métodos y perfil válido | Método y estado conservados en ambas operaciones."""
        for indice, metodo in enumerate(METODOS):
            with self.subTest(metodo=metodo):
                carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
                r = compras.confirmar_compra(CLIENTE, True, metodo_pago=metodo)
                self.assertTrue(r["ok"], r["message"])
                p = compras.obtener_detalle_compra(CLIENTE, r["pedido"])
                estado = "Pendiente" if indice == 0 else "No procesado"
                self.assertEqual((p["MetodoPago"], p["EstadoPago"]), (metodo, estado))
                a = self.alquilar(metodo, dias=10 + indice * 10)
                leido = next(x for x in alquileres.obtener_alquileres_usuario(CLIENTE) if x["Id"] == a["Id"])
                self.assertEqual((leido["MetodoPago"], leido["EstadoPago"]), (metodo, estado))

    def test_07_metodos_invalidos(self):
        """Pagos | Método no permitido | ValueError y datos temporales intactos."""
        antes = huellas(self.base)
        for metodo in ("", "Transferencia inexistente"):
            with self.assertRaises(ValueError):
                compras.confirmar_compra(CLIENTE, True, metodo_pago=metodo)
            with self.assertRaises(ValueError):
                self.alquilar(metodo)
        self.assertEqual(huellas(self.base), antes)

    def test_08_carritos_separados(self):
        """Carrito | Dos usuarios ficticios | Compra de uno conserva el carrito del otro."""
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
        self.sesion(OTRO)
        carrito.agregar_al_carrito(OTRO, "P1", "M", 2)
        self.assertEqual(carrito.leer_carrito(OTRO)[0]["Cantidad"], 2)
        self.sesion(CLIENTE)
        self.assertEqual(carrito.leer_carrito(CLIENTE)[0]["Cantidad"], 1)
        self.assertTrue(compras.confirmar_compra(CLIENTE, True)["ok"])
        self.sesion(OTRO)
        self.assertEqual(carrito.leer_carrito(OTRO)[0]["Cantidad"], 2)

    def test_09_cantidades_invalidas(self):
        """Carrito | Cero, negativos, fracciones y exceso | Rechazo sin modificar carrito ni stock."""
        antes = huellas(self.base)
        for cantidad in (0, -1, 1.5, "texto", float("nan"), float("inf"), 6):
            with self.subTest(cantidad=str(cantidad)), self.assertRaises(ValueError):
                carrito.agregar_al_carrito(CLIENTE, "P1", "M", cantidad)
        self.assertEqual(huellas(self.base), antes)

    def test_10_compra_stock_exacto_comprobante_historial(self):
        """Compra | Comprar todas las existencias | Stock cero, pedido y comprobante correctos; carrito vacío."""
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 5)
        self.assertEqual(carrito.leer_carrito(CLIENTE)[0]["Cantidad"], 5)
        r = compras.confirmar_compra(CLIENTE, True)
        self.assertTrue(r["ok"], r["message"])
        self.assertEqual(r["total"], 250000)
        self.assertEqual(self.stock(), 0)
        self.assertEqual(carrito.leer_carrito(CLIENTE), [])
        p = compras.listar_compras(CLIENTE)[0]
        self.assertEqual((p["Pedido"], p["Total"], p["Articulos"][0]["Cantidad"]), (r["pedido"], 250000, 5))
        recibo = Path(r["comprobante"])
        self.assertTrue(recibo.is_relative_to(self.base))
        texto = recibo.read_text(encoding="utf-8")
        for valor in (r["pedido"], "P1", "Cantidad: 5", "250,000.00", METODOS[0]):
            self.assertIn(valor, texto)

    def test_11_cancelacion(self):
        """Compra | Cancelar confirmación | Inventario, carrito y registros sin cambios."""
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
        antes = huellas(self.base)
        self.assertFalse(compras.confirmar_compra(CLIENTE, False)["ok"])
        self.assertEqual(huellas(self.base), antes)

    def test_12_stock_reducido_antes_de_comprar(self):
        """Compra | Inventario menor que carrito guardado | Compra rechazada y carrito conservado."""
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 5)
        self.sesion(ADMIN)
        admin.actualizar_existencias("P1", "M", 4)
        self.sesion(CLIENTE)
        antes = huellas(self.base)
        self.assertFalse(compras.confirmar_compra(CLIENTE, True)["ok"])
        self.assertEqual(huellas(self.base), antes)

    def test_13_carrito_en_proceso_nuevo(self):
        """Persistencia | Leer carrito desde otro intérprete | Recuperar exactamente artículo, talla y cantidad."""
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 2)
        programa = """from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from test_criticos import redirigir, CLIENTE
from backend.sesion import sesion_actual
from backend.carrito import leer_carrito
parches = redirigir(Path(sys.argv[2]))
sesion_actual.correo = CLIENTE
sesion_actual.activa = True
assert leer_carrito(CLIENTE) == [{'Codigo':'P1','Talla':'M','Cantidad':2}]
print('CARRITO_RECUPERADO')
"""
        r = subprocess.run([sys.executable, "-B", "-c", programa, str(RAIZ / "tests"), str(self.base)],
                           cwd=RAIZ, capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, "El subproceso no pudo recuperar el carrito temporal")
        self.assertEqual(r.stdout.strip(), "CARRITO_RECUPERADO")

    def test_14_fechas_invalidas(self):
        """Alquiler | Formatos, fecha pasada y devolución no posterior | Rechazo sin escrituras."""
        inicio, fin = self.fechas()
        ayer = (dt.date.today() - dt.timedelta(days=1)).strftime("%d/%m/%Y")
        antes = huellas(self.base)
        for fi, ff in (("31/02/2027", fin), ("2027-01-01", fin), (ayer, fin), (inicio, inicio), (fin, inicio)):
            with self.subTest(inicio=fi, fin=ff), self.assertRaises(ValueError):
                alquileres.registrar_alquiler(CLIENTE, "T1", "M", fi, ff)
        self.assertEqual(huellas(self.base), antes)

    def test_15_tallas_y_trajes_invalidos(self):
        """Alquiler | Talla inexistente y traje inactivo o ausente | Rechazo sin registros."""
        antes = huellas(self.base)
        for codigo, talla in (("T1", "XXXL"), ("T2", "M"), ("NOEXISTE", "M")):
            with self.assertRaises(ValueError):
                alquileres.registrar_alquiler(CLIENTE, codigo, talla, *self.fechas())
        self.assertEqual(huellas(self.base), antes)

    def test_16_limites_revision_dos_dias(self):
        """Disponibilidad | Último día de revisión y día siguiente | Rechazo hasta devolución +2; aceptación en +3."""
        a = self.alquilar()
        fin = dt.datetime.strptime(a["FechaProgramada"], "%d/%m/%Y").date()
        for dias in (0, 1, 2):
            fi = fin + dt.timedelta(days=dias)
            with self.subTest(dias=dias), self.assertRaises(ValueError):
                alquileres.registrar_alquiler(CLIENTE, "T1", "M", fi.strftime("%d/%m/%Y"), (fi + dt.timedelta(days=1)).strftime("%d/%m/%Y"))
        fi = fin + dt.timedelta(days=3)
        alquileres.registrar_alquiler(CLIENTE, "T1", "M", fi.strftime("%d/%m/%Y"), (fi + dt.timedelta(days=1)).strftime("%d/%m/%Y"))
        self.assertEqual(len(alquileres.obtener_alquileres_usuario(CLIENTE)), 2)

    def test_17_devolucion_y_pago_conservado(self):
        """Devolución | Devolver desde el día de inicio y repetir | Fecha real y pago conservados; repetición rechazada."""
        a = self.alquilar(METODOS[2], dias=0)
        r = alquileres.devolver_alquiler(CLIENTE, a["Id"])
        self.assertEqual(r["Estado"], "Devuelto")
        leido = alquileres.obtener_alquileres_usuario(CLIENTE)[0]
        self.assertEqual(leido["FechaReal"], dt.date.today().strftime("%d/%m/%Y"))
        self.assertEqual((leido["MetodoPago"], leido["EstadoPago"]), (a["MetodoPago"], a["EstadoPago"]))
        antes = huellas(self.base)
        with self.assertRaises(ValueError):
            alquileres.devolver_alquiler(CLIENTE, a["Id"])
        self.assertEqual(huellas(self.base), antes)
        hoy = dt.date.today()
        self.assertTrue(alquileres.hay_conflicto_alquiler("T1", "M", hoy + dt.timedelta(days=2), hoy + dt.timedelta(days=3)))
        self.assertFalse(alquileres.hay_conflicto_alquiler("T1", "M", hoy + dt.timedelta(days=3), hoy + dt.timedelta(days=4)))

    def test_18_devolucion_anticipada(self):
        """Devolución | Antes del inicio | Rechazo conservando el alquiler activo."""
        a = self.alquilar()
        antes = huellas(self.base)
        with self.assertRaises(ValueError):
            alquileres.devolver_alquiler(CLIENTE, a["Id"])
        self.assertEqual(huellas(self.base), antes)

    def test_19_administracion_denegada(self):
        """Administración | Cuenta normal | Consultas y modificación denegadas sin cambios."""
        antes = huellas(self.base)
        for operacion in (admin.cargar_inventario_administracion, admin.listar_compras_administracion,
                          admin.listar_alquileres_administracion, lambda: admin.actualizar_existencias("P1", "M", 20)):
            with self.assertRaises(PermissionError):
                operacion()
        self.assertEqual(huellas(self.base), antes)

    def test_20_administracion_autorizada(self):
        """Administración | Consultar y modificar copias | Operaciones visibles y existencias actualizadas sin perder registros."""
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
        self.assertTrue(compras.confirmar_compra(CLIENTE, True)["ok"])
        self.alquilar()
        self.sesion(ADMIN)
        self.assertTrue(admin.es_administrador(ADMIN))
        self.assertEqual(len(admin.listar_compras_administracion()), 1)
        self.assertEqual(len(admin.listar_alquileres_administracion()), 1)
        admin.actualizar_existencias("P1", "M", 7)
        productos, existencias = admin.cargar_inventario_administracion()
        self.assertEqual(len(productos), 2)
        self.assertEqual(int(existencias.loc[existencias.Codigo == "P1", "Cantidad"].iloc[0]), 7)
        antes = huellas(self.base)
        with self.assertRaises(ValueError):
            admin.actualizar_existencias("P1", "M", -1)
        self.assertEqual(huellas(self.base), antes)


class Formularios(Aislada):
    @staticmethod
    def cancelar_callbacks(ventana):
        # Los intérpretes Tk comparten cola de eventos entre raíces sucesivas.
        for identificador in ventana.tk.call("after", "info"):
            ventana.tk.call("after", "cancel", identificador)

    def cerrar_interfaz(self):
        self.cancelar_callbacks(self.ui.ventana)
        self.ui.ventana.destroy()

    def setUp(self):
        super().setUp()
        anterior = sys.modules.get("frontend.app")
        if anterior is not None:
            self.cancelar_callbacks(anterior.ventana)
        spec = importlib.util.spec_from_file_location("_efrata_ui_aislada", RAIZ / "frontend/app.py")
        self.ui = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.ui)
        self.addCleanup(self.cerrar_interfaz)
        # Solo diálogos informativos/confirmación; no se simula la lógica de negocio.
        for nombre, reemplazo in (("mostrar_aviso", lambda *args, **kwargs: None),
                                  ("preguntar_confirmacion_cliente", lambda *args, **kwargs: True)):
            parche = patch.object(self.ui, nombre, reemplazo)
            parche.start()
            self.addCleanup(parche.stop)

    def preparar_formularios(self, metodo):
        u = self.ui
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
        u.mostrar_carrito()
        u.selector_metodo_pago.set(metodo)
        u.actualizar_formulario_tarjeta(metodo)
        u.abrir_formulario_alquiler("T1", "Traje de prueba", "M, L", 100000)
        u.selector_talla.set("M")
        u.fecha_alquiler.set(self.fechas()[0])
        u.fecha_devolucion.set(self.fechas()[1])
        u.selector_metodo_alquiler.set(metodo)
        u.actualizar_formulario_tarjeta_alquiler(metodo)

    def tarjeta(self, titular, digitos):
        for campo, valor in ((self.ui.campo_titular_tarjeta, titular), (self.ui.campo_ultimos_tarjeta, digitos),
                             (self.ui.campo_titular_alquiler, titular), (self.ui.campo_ultimos_alquiler, digitos)):
            campo.delete(0, "end")
            campo.insert(0, valor)

    def test_21_tarjetas_invalidas_formularios(self):
        """Interfaz | Tarjetas incompletas e inválidas | Ambos formularios rechazan sin escrituras."""
        self.preparar_formularios(METODOS[1])
        for metodo in METODOS[1:]:
            self.ui.selector_metodo_pago.set(metodo)
            self.ui.selector_metodo_alquiler.set(metodo)
            for titular, digitos in (("", "9876"), ("Ficticio", ""), ("Ficticio", "123"), ("Ficticio", "12345"), ("Ficticio", "abcd")):
                with self.subTest(metodo=metodo, entrada=digitos):
                    self.tarjeta(titular, digitos)
                    antes = huellas(self.base)
                    self.ui.comprar()
                    self.ui.confirmar_alquiler_interfaz()
                    self.assertIn("cuatro dígitos", self.ui.mensaje_carrito.cget("text"))
                    self.assertIn("cuatro dígitos", self.ui.mensaje_alquiler.cget("text"))
                    self.assertEqual(huellas(self.base), antes)

    def test_22_compra_y_alquiler_desde_formularios(self):
        """Integración gráfica | Enviar widgets reales con tres métodos | Pedido, comprobante, stock y alquiler persistidos; tarjeta no guardada."""
        for indice, metodo in enumerate(METODOS):
            with self.subTest(metodo=metodo):
                self.preparar_formularios(metodo)
                self.tarjeta("Titular Ficticio Evidencia", "9876")
                self.ui.fecha_alquiler.set(self.fechas(10 + indice * 10)[0])
                self.ui.fecha_devolucion.set(self.fechas(10 + indice * 10)[1])
                self.ui.comprar()
                self.ui.confirmar_alquiler_interfaz()
                self.assertIn("Compra confirmada", self.ui.mensaje_carrito.cget("text"))
                self.assertIn("exitosamente", self.ui.mensaje_alquiler.cget("text"))
                pedido = compras.listar_compras(CLIENTE)[-1]
                a = alquileres.obtener_alquileres_usuario(CLIENTE)[-1]
                estado = "Pendiente" if indice == 0 else "No procesado"
                self.assertEqual((pedido["MetodoPago"], pedido["EstadoPago"]), (metodo, estado))
                self.assertEqual((a["MetodoPago"], a["EstadoPago"]), (metodo, estado))
                self.assertEqual(self.stock(), 4 - indice)
                self.assertEqual(carrito.leer_carrito(CLIENTE), [])
                recibo = self.base / "comprobantes" / (pedido["Pedido"] + ".txt")
                self.assertIn(metodo, recibo.read_text(encoding="utf-8"))
                self.assertIn("Este sistema no procesa pagos reales", recibo.read_text(encoding="utf-8"))
                self.assertNotIn("demostración", recibo.read_text(encoding="utf-8"))
        for archivo in self.base.rglob("*.txt"):
            texto = archivo.read_text(encoding="utf-8")
            self.assertNotIn("Titular Ficticio Evidencia", texto)
            self.assertNotIn("9876", texto)

    def test_23_panel_administrativo_real(self):
        """Interfaz administrativa | Panel autorizado | Panel visible y consulta del inventario temporal."""
        self.sesion(ADMIN)
        self.ui.mostrar_panel_admin("Dashboard")
        self.ui.ventana.update()
        self.assertTrue(self.ui.pantalla_admin.winfo_ismapped())
        self.assertEqual(self.ui.mensaje_admin.cget("text"), "")
        self.assertEqual(len(admin.cargar_inventario_administracion()[0]), 2)

    def test_24_edicion_administrativa_formulario(self):
        """Integración administrativa | Guardar edición de traje desde widgets | Precio y descripción persisten en Excel temporal."""
        self.sesion(ADMIN)
        traje = admin.cargar_trajes_administracion().iloc[0].to_dict()
        self.ui._abrir_formulario_traje(traje, actualizar_lista=lambda: None)
        dialogo = next(w for w in self.ui.ventana.winfo_children() if isinstance(w, self.ui.ctk.CTkToplevel))

        def recorrer(widget):
            for hijo in widget.winfo_children():
                yield hijo
                yield from recorrer(hijo)

        campos = [w for w in recorrer(dialogo) if isinstance(w, self.ui.ctk.CTkEntry)]
        self.assertEqual(len(campos), 5)
        self.assertEqual(campos[0].get(), "T1")
        for campo, valor in ((campos[2], "125000"), (campos[3], "Descripción ficticia actualizada")):
            campo.delete(0, "end")
            campo.insert(0, valor)
        guardar = next(w for w in recorrer(dialogo) if isinstance(w, self.ui.ctk.CTkButton) and w.cget("text") == "Guardar traje")
        with patch.object(self.ui.messagebox, "showerror") as errores:
            guardar.invoke()
            errores.assert_not_called()
        guardado = admin.cargar_trajes_administracion().iloc[0]
        self.assertEqual(guardado["Codigo"], "T1")
        self.assertEqual(guardado["Precio"], 125000)
        self.assertEqual(guardado["Descripcion"], "Descripción ficticia actualizada")

    def test_25_etiquetas_y_compatibilidad_historica(self):
        """Presentación | Estados históricos y etiquetas nuevas | Mostrar No procesado sin reescribir registros; indicador de pedidos claro."""
        self.assertEqual(self.ui.texto_estado_pago("Pendiente"), "Pendiente")
        self.assertEqual(self.ui.texto_estado_pago("Pago anterior no registrado"), "Pago anterior no registrado")
        carrito.agregar_al_carrito(CLIENTE, "P1", "M", 1)
        self.assertTrue(compras.confirmar_compra(CLIENTE, True, metodo_pago=METODOS[1])["ok"])
        self.alquilar(METODOS[2])
        for archivo in (compras.ARCHIVO_COMPRAS, alquileres.ARCHIVO_ALQUILERES):
            archivo.write_text(archivo.read_text(encoding="utf-8").replace(
                "No procesado", "No procesado; demostración académica"), encoding="utf-8")
        antes = huellas(self.base)

        def textos(widget):
            resultado = []
            for hijo in widget.winfo_children():
                if isinstance(hijo, self.ui.ctk.CTkLabel):
                    resultado.append(hijo.cget("text"))
                resultado.extend(textos(hijo))
            return resultado

        self.ui.mostrar_compras()
        self.ui.mostrar_alquileres()
        for contenedor in (self.ui.lista_compras, self.ui.lista_alquileres):
            etiquetas = "\n".join(textos(contenedor))
            self.assertIn("Estado del pago: No procesado", etiquetas)
            self.assertNotIn("demostración", etiquetas)
        self.sesion(ADMIN)
        self.ui.mostrar_panel_admin("Dashboard")
        self.assertIn("Valor de pedidos registrados", textos(self.ui.contenido_admin))
        self.assertNotIn("Ventas simuladas", textos(self.ui.contenido_admin))
        self.ui._mostrar_estadisticas_admin()
        self.assertIn("Valor de pedidos registrados", textos(self.ui.contenido_admin))
        for mostrar in (self.ui._mostrar_compras_admin, self.ui._mostrar_alquileres_admin):
            mostrar()
            etiquetas = "\n".join(textos(self.ui.contenido_admin))
            self.assertIn("No procesado", etiquetas)
            self.assertNotIn("demostración", etiquetas)
        self.assertEqual(huellas(self.base), antes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
