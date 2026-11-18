"""Pruebas del catálogo ampliado; toda escritura operativa usa archivos temporales."""
import datetime
import hashlib
import importlib
import configparser
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from PIL import Image
import backend
from backend import administracion, alquileres, carrito, catalogo, compras, datos_personales, rutas
from backend.sesion import sesion_actual

RAIZ = Path(__file__).resolve().parents[1]
def leer_referencias_catalogo():
    referencias = configparser.ConfigParser(interpolation=None)
    with (RAIZ / "docs/catalogo_referencia.txt").open(encoding="utf-8") as archivo:
        referencias.read_file(archivo)
    resultado = dict(referencias["general"])
    resultado.update(productos=[], trajes=[])
    for seccion in referencias.sections():
        if seccion == "general":
            continue
        tipo, codigo = seccion.split(":", 1)
        producto = dict(referencias[seccion])
        if producto["codigo"] != codigo:
            raise ValueError(f"Código inconsistente en {seccion}")
        for campo in ("precio", "foto_id", "bytes"):
            producto[campo] = int(producto[campo])
        producto["resolucion"] = [int(valor.strip()) for valor in producto["resolucion"].split("x")]
        if "existencias" in producto:
            producto["existencias"] = {
                talla.strip(): int(cantidad)
                for talla, cantidad in (item.split(":") for item in producto["existencias"].split(","))
            }
        resultado[{"producto": "productos", "traje": "trajes"}[tipo]].append(producto)
    return resultado


MANIFIESTO = leer_referencias_catalogo()
CORREO = "catalogo.prueba@gmail.com"


class CatalogoAmpliado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                      for carpeta in (RAIZ / "data", RAIZ / "comprobantes")
                      for p in carpeta.glob("*") if p.is_file()}
        cls.tmp = tempfile.TemporaryDirectory(prefix="efrata_catalogo_")
        cls.base = Path(cls.tmp.name)
        cls.data = cls.base / "data"
        cls.data.mkdir()
        for nombre in ("ropa.xlsx", "inventario.xlsx"):
            shutil.copy2(RAIZ / "data" / nombre, cls.data / nombre)
        cls.parches = []
        for modulo in list(sys.modules.values()):
            if getattr(modulo, "__name__", "").startswith("backend"):
                for nombre, valor in list(vars(modulo).items()):
                    if isinstance(valor, Path) and nombre.startswith(("ARCHIVO_", "DIRECTORIO_")):
                        destino = (cls.data / valor.name if nombre.startswith("ARCHIVO_")
                                   else cls.data if nombre == "DIRECTORIO_DATOS"
                                   else cls.base / "comprobantes" if nombre == "DIRECTORIO_COMPROBANTES"
                                   else cls.base)
                        parche = patch.object(modulo, nombre, destino)
                        parche.start()
                        cls.parches.append(parche)
        cls.ui = importlib.import_module("frontend.app")
        cls.ui.mostrar_aviso = lambda *args, **kwargs: None

    @classmethod
    def tearDownClass(cls):
        if os.environ.get("EFRATA_VISTA") == "1":
            cls.ui.ventana.title("EFRATA - revisión aislada del catálogo")
            cls.ui.ventana.geometry("1100x800")
            cls.ui.mostrar_catalogo_ropa()
            print("VISTA AISLADA ABIERTA; cerrar la ventana para finalizar", flush=True)
            cls.ui.ventana.mainloop()
        else:
            cls.ui.ventana.destroy()
        for parche in reversed(cls.parches):
            parche.stop()
        sesion_actual.activa = False
        sesion_actual.correo = ""
        actuales = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                    for carpeta in (RAIZ / "data", RAIZ / "comprobantes")
                    for p in carpeta.glob("*") if p.is_file()}
        cls.tmp.cleanup()
        if actuales != cls.hashes:
            raise AssertionError("Cambió un archivo operativo original")

    def setUp(self):
        def verificar_originales():
            actuales = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                        for carpeta in (RAIZ / "data", RAIZ / "comprobantes")
                        for p in carpeta.glob("*") if p.is_file()}
            self.assertEqual(actuales, self.hashes, "Cambió un archivo operativo original")

        self.addCleanup(verificar_originales)
        # Cada caso parte del mismo inventario y de registros temporales vacíos.
        # Se mantienen los siete casos originales, sin depender de su orden.
        self.assertTrue(self.data.is_relative_to(self.base))
        for archivo in self.data.glob("*.txt"):
            archivo.unlink()
        for nombre in ("ropa.xlsx", "inventario.xlsx"):
            shutil.copy2(RAIZ / "data" / nombre, self.data / nombre)
        for archivo in (self.base / "comprobantes").glob("*.txt"):
            archivo.unlink()
        sesion_actual.correo = CORREO
        sesion_actual.activa = True
        datos_personales.guardar_datos_personales(CORREO, {
            "Nombre": "Ana", "Apellidos": "Prueba", "Telefono": "3000000000",
            "TipoDocumento": "CC", "NumeroDocumento": "10000000",
            "Direccion": "Dirección ficticia", "CodigoPostal": "110111"})

    def test_01_catalogos_y_existencias(self):
        prendas = catalogo.cargar_catalogo_ropa()
        self.assertEqual(len(prendas), 13)
        self.assertEqual(len(catalogo.cargar_trajes()), 10)
        for nuevo in MANIFIESTO["productos"]:
            p = next(p for p in prendas if p["Codigo"] == nuevo["codigo"])
            self.assertEqual(p["Precio"], nuevo["precio"])
            self.assertEqual({v["Talla"]: v["Cantidad"] for v in p["Tallas"]}, nuevo["existencias"])
            self.assertIn(p, catalogo.filtrar_catalogo_ropa(prendas, nuevo["seccion"], nuevo["tipo"]))

    def test_00_ampliacion_dentro_de_pantalla(self):
        ui = self.ui
        ui.ventana.geometry("420x760+20+500")
        ui.ventana.update()
        ui.ampliar_fotografia("CL-MU-007")
        ui.ventana.update()
        dialogo = next(w for w in ui.ventana.winfo_children() if isinstance(w, ui.ctk.CTkToplevel))
        try:
            self.assertLessEqual(dialogo.winfo_rooty() + dialogo.winfo_height(), dialogo.winfo_screenheight())
            self.assertLessEqual(dialogo.winfo_rootx() + dialogo.winfo_width(), dialogo.winfo_screenwidth())
            cerrar = next(w for w in dialogo.winfo_children()
                          if isinstance(w, ui.ctk.CTkButton) and w.cget("text") == "Cerrar")
            self.assertLessEqual(cerrar.winfo_rooty() + cerrar.winfo_height(), dialogo.winfo_rooty() + dialogo.winfo_height())
        finally:
            dialogo.destroy()
            ui.ventana.geometry("420x760+20+20")

    def test_02_fotos_fuentes_y_apertura(self):
        for p in MANIFIESTO["productos"] + MANIFIESTO["trajes"]:
            archivo = RAIZ / p["archivo"]
            self.assertEqual(hashlib.sha256(archivo.read_bytes()).hexdigest(), p["sha256"])
            with Image.open(archivo) as im:
                self.assertEqual(list(im.size), p["resolucion"])
                self.assertGreaterEqual(max(im.size), 1200)
                self.assertFalse(im.getexif())
                im.verify()
            self.assertTrue(p["fuente"].startswith("https://www.pexels.com/photo/"))
        ui = self.ui
        for p in catalogo.cargar_catalogo_ropa():
            ui.ampliar_fotografia(p["Codigo"])
            ui.ventana.update()
            ventanas = [w for w in ui.ventana.winfo_children() if isinstance(w, ui.ctk.CTkToplevel)]
            self.assertTrue(ventanas)
            ventanas[-1].destroy()
        for traje in catalogo.cargar_trajes():
            ui.ampliar_fotografia(traje[0])
            ui.ventana.update()
            ventanas = [w for w in ui.ventana.winfo_children() if isinstance(w, ui.ctk.CTkToplevel)]
            ventanas[-1].destroy()

    def test_03_busqueda_filtros_y_tarjetas(self):
        ui = self.ui
        ui.mostrar_catalogo_ropa()
        for p in MANIFIESTO["productos"]:
            ui.selector_seccion.set(p["seccion"])
            ui.selector_tipo.set(p["tipo"])
            ui.caja_busqueda.delete(0, "end")
            ui.caja_busqueda.insert(0, p["codigo"])
            ui.mostrar_productos_ropa()
            self.assertEqual(len(ui.lista_ropa.winfo_children()), 1)
            ui.caja_busqueda.delete(0, "end")
            ui.caja_busqueda.insert(0, p["nombre"])
            ui.mostrar_productos_ropa()
            self.assertEqual(len(ui.lista_ropa.winfo_children()), 1)
        ui.selector_seccion.set("Todas")
        ui.selector_tipo.set("Todos")
        ui.caja_busqueda.delete(0, "end")
        ui.mostrar_productos_ropa()
        for tamano in ("360x560", "1100x800"):
            ui.ventana.geometry(tamano)
            for _ in range(12):
                ui.ventana.update()
                time.sleep(0.02)
            for tarjeta in ui.lista_ropa.winfo_children():
                self.assertGreater(tarjeta.winfo_width(), 200)
                self.assertLessEqual(tarjeta.winfo_x() + tarjeta.winfo_width(), ui.lista_ropa.winfo_width())
        ui.mostrar_trajes()
        ui.ventana.update()
        self.assertEqual(len(ui.lista_trajes.winfo_children()), 10)
        ui.ventana.geometry("360x560")
        for _ in range(12):
            ui.ventana.update()
            time.sleep(0.02)
        for tarjeta in ui.lista_trajes.winfo_children():
            self.assertLessEqual(tarjeta.winfo_x() + tarjeta.winfo_width(), ui.lista_trajes.winfo_width())

    def test_04_carrito_compra_y_stock(self):
        p = MANIFIESTO["productos"][0]
        carrito.agregar_al_carrito(CORREO, p["codigo"], "M", 1)
        self.assertEqual(carrito.leer_carrito(CORREO)[0]["Cantidad"], 1)
        sesion_actual.activa = False
        sesion_actual.activa = True
        self.assertEqual(carrito.leer_carrito(CORREO)[0]["Codigo"], p["codigo"])
        resultado = compras.confirmar_compra(CORREO, True)
        self.assertTrue(resultado["ok"], resultado)
        actualizado = next(x for x in catalogo.cargar_catalogo_ropa() if x["Codigo"] == p["codigo"])
        self.assertEqual(next(x["Cantidad"] for x in actualizado["Tallas"] if x["Talla"] == "M"), 3)
        self.assertEqual(carrito.leer_carrito(CORREO), [])
        self.assertEqual(len(compras.listar_compras(CORREO)), 1)

    def test_05_alquiler_conflicto_y_registro_historico(self):
        inicio = datetime.date.today() + datetime.timedelta(days=20)
        fin = inicio + datetime.timedelta(days=2)
        fi, ff = inicio.strftime("%d/%m/%Y"), fin.strftime("%d/%m/%Y")
        historico = f"{CORREO}|T001|Traje histórico ficticio|M|{fi}|{ff}|Activo|120000\n"
        alquileres.ARCHIVO_ALQUILERES.write_text(historico, encoding="utf-8")
        for p in MANIFIESTO["trajes"]:
            resultado = alquileres.registrar_alquiler(CORREO, p["codigo"], "M", fi, ff)
            self.assertEqual(resultado["Codigo"], p["codigo"])
            self.assertTrue(alquileres.hay_conflicto_alquiler(p["codigo"], "M", fi, ff))
            with self.assertRaises(ValueError):
                alquileres.registrar_alquiler(CORREO, p["codigo"], "M", fi, ff)
        self.assertTrue(alquileres.ARCHIVO_ALQUILERES.read_text(encoding="utf-8").startswith(historico))
        self.assertEqual(len(alquileres.obtener_alquileres_usuario(CORREO)), 6)
        self.assertTrue(alquileres.hay_conflicto_alquiler("T001", "M", fi, ff))

    def test_06_inventario_administrativo(self):
        administracion.ARCHIVO_ADMINISTRADORES.write_text(CORREO + "\n", encoding="utf-8")
        productos, existencias = administracion.cargar_inventario_administracion()
        self.assertEqual(len(productos), 14)
        self.assertEqual(len(existencias), 44)
        self.assertEqual(len(administracion.cargar_trajes_administracion()), 10)
        for p in MANIFIESTO["productos"][1:]:
            filas = existencias[existencias["Codigo"] == p["codigo"]]
            self.assertEqual(dict(zip(filas["Talla"], filas["Cantidad"])), p["existencias"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
