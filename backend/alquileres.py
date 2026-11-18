import datetime
import os
import tempfile
import uuid
from .rutas import ARCHIVO_ALQUILERES, DIRECTORIO_DATOS
from .catalogo import cargar_trajes
from .sesion import requerir_usuario
from .datos_personales import validar_perfil_completo

METODOS_PAGO_ALQUILER = {"Efectivo al recibir", "Tarjeta de crédito", "Tarjeta débito"}


def _interpretar_linea(linea):
    campos = linea.rstrip("\r\n").split("|")
    return campos if len(campos) in {8, 10, 12, 13} else None


def _convertir_fecha(valor):
    return datetime.datetime.strptime(str(valor), "%d/%m/%Y").date()


def validar_metodo_pago_alquiler(metodo_pago):
    metodo = str(metodo_pago or "").strip()
    if metodo not in METODOS_PAGO_ALQUILER:
        raise ValueError("Seleccione un método de pago válido.")
    return metodo


def hay_conflicto_alquiler(codigo, talla, fecha_inicio, fecha_fin):
    if not ARCHIVO_ALQUILERES.exists():
        return False
    fecha_inicio = _convertir_fecha(fecha_inicio) if isinstance(fecha_inicio, str) else fecha_inicio
    fecha_fin = _convertir_fecha(fecha_fin) if isinstance(fecha_fin, str) else fecha_fin
    if isinstance(fecha_inicio, datetime.datetime):
        fecha_inicio = fecha_inicio.date()
    if isinstance(fecha_fin, datetime.datetime):
        fecha_fin = fecha_fin.date()
    with ARCHIVO_ALQUILERES.open("r", encoding="utf-8") as archivo:
        for linea in archivo:
            campos = _interpretar_linea(linea)
            if campos is None or campos[1] != str(codigo).strip():
                continue
            if campos[3].strip().casefold() != str(talla).strip().casefold():
                continue
            try:
                inicio_existente, devolucion_programada = _convertir_fecha(campos[4]), _convertir_fecha(campos[5])
            except ValueError:
                continue
            estado = campos[6].strip().casefold()
            if estado == "devuelto":
                if len(campos) not in {10, 12, 13} or not campos[9].strip():
                    continue
                try:
                    devolucion_real = _convertir_fecha(campos[9])
                except ValueError:
                    continue
                if devolucion_real < inicio_existente:
                    continue
                ocupado_hasta = devolucion_real + datetime.timedelta(days=2)
            elif estado == "activo":
                ocupado_hasta = devolucion_programada + datetime.timedelta(days=2)
            else:
                continue
            if fecha_inicio <= ocupado_hasta and fecha_fin >= inicio_existente:
                return True
    return False


def obtener_alquileres_usuario(correo):
    correo = requerir_usuario(correo)
    if not ARCHIVO_ALQUILERES.exists():
        return []
    alquileres = []
    with ARCHIVO_ALQUILERES.open("r", encoding="utf-8") as archivo:
        for numero_linea, linea in enumerate(archivo):
            campos = _interpretar_linea(linea)
            if campos and campos[0].strip().casefold() == correo:
                alquileres.append({
                    "Correo": correo, "Codigo": campos[1], "Nombre": campos[2],
                    "Talla": campos[3], "FechaAlquiler": campos[4],
                    "FechaProgramada": campos[5], "Estado": campos[6],
                    "Precio": campos[7],
                    "Id": campos[8] if len(campos) in {10, 12, 13} else "",
                    "FechaReal": campos[9] if len(campos) in {10, 12, 13} else "",
                    "MetodoPago": campos[10] if len(campos) in {12, 13} else "Método no registrado",
                    "EstadoPago": campos[11] if len(campos) in {12, 13} else "Pago anterior no registrado",
                    "IndiceArchivo": numero_linea,
                })
    return alquileres


def registrar_alquiler(correo, codigo, talla, fecha_inicio, devolucion_programada,
                       metodo_pago="Efectivo al recibir"):
    correo = requerir_usuario(correo)
    validar_perfil_completo(correo)
    metodo_pago = validar_metodo_pago_alquiler(metodo_pago)
    codigo, talla = str(codigo).strip(), str(talla).strip().upper()
    try:
        fecha_inicio, fecha_devolucion = _convertir_fecha(fecha_inicio), _convertir_fecha(devolucion_programada)
    except (TypeError, ValueError) as error:
        raise ValueError("Las fechas deben tener el formato dd/mm/aaaa.") from error
    if fecha_inicio < datetime.date.today():
        raise ValueError("La fecha de alquiler no puede ser anterior a hoy.")
    if fecha_devolucion <= fecha_inicio:
        raise ValueError("La devolución debe ser posterior al alquiler.")
    traje = next((elemento for elemento in cargar_trajes() if elemento[0] == codigo), None)
    if traje is None:
        raise ValueError("No se encontró el traje solicitado.")
    if str(traje[4]).strip().casefold() != "activo":
        raise ValueError("El traje seleccionado no está activo y no se puede alquilar.")
    tallas = {valor.strip().upper() for valor in str(traje[2]).split(",")}
    if talla not in tallas:
        raise ValueError("La talla no está disponible para este traje.")
    if hay_conflicto_alquiler(codigo, talla, fecha_inicio, fecha_devolucion):
        raise ValueError("Esta talla ya tiene un alquiler o revisión que se cruza con esas fechas.")
    id_alquiler = str(uuid.uuid4())
    if ARCHIVO_ALQUILERES.exists() and ARCHIVO_ALQUILERES.stat().st_size:
        with ARCHIVO_ALQUILERES.open("rb") as existente:
            existente.seek(-1, os.SEEK_END)
            if existente.read(1) not in {b"\n", b"\r"}:
                with ARCHIVO_ALQUILERES.open("a", encoding="utf-8") as archivo:
                    archivo.write("\n")
    with ARCHIVO_ALQUILERES.open("a", encoding="utf-8") as archivo:
        archivo.write(
            f"{correo}|{codigo}|{traje[1]}|{talla}|{fecha_inicio.strftime('%d/%m/%Y')}|"
            f"{fecha_devolucion.strftime('%d/%m/%Y')}|Activo|{traje[3]}|{id_alquiler}||"
            f"{metodo_pago}|{'Pendiente' if metodo_pago == 'Efectivo al recibir' else 'No procesado'}|\n"
        )
    return {
        "Correo": correo, "Codigo": codigo, "Nombre": traje[1], "Talla": talla,
        "FechaAlquiler": fecha_inicio.strftime("%d/%m/%Y"),
        "FechaProgramada": fecha_devolucion.strftime("%d/%m/%Y"),
        "Estado": "Activo", "Precio": traje[3], "Id": id_alquiler, "FechaReal": "",
        "MetodoPago": metodo_pago,
        "EstadoPago": "Pendiente" if metodo_pago == "Efectivo al recibir"
        else "No procesado",
    }


def devolver_alquiler(correo, identificador_alquiler):
    correo = requerir_usuario(correo)
    if not ARCHIVO_ALQUILERES.exists():
        raise ValueError("No hay alquileres registrados.")
    with ARCHIVO_ALQUILERES.open("r", encoding="utf-8", newline="") as archivo:
        lineas = archivo.readlines()
    alquileres = obtener_alquileres_usuario(correo)
    activa = [registro_r for registro_r in alquileres if registro_r["Estado"].strip().casefold() == "activo"]
    seleccionado = next((registro_r for registro_r in activa if str(registro_r["IndiceArchivo"]) == str(identificador_alquiler)
                     or (registro_r["Id"] and registro_r["Id"].casefold() == str(identificador_alquiler).casefold())), None)
    if seleccionado is None:
        raise ValueError("No se encontró un alquiler activo de esta cuenta.")
    campos = _interpretar_linea(lineas[seleccionado["IndiceArchivo"]])
    if campos is None:
        raise ValueError("El registro de alquiler tiene un formato inválido.")
    try:
        fecha_inicio = _convertir_fecha(campos[4])
    except (TypeError, ValueError) as error:
        raise ValueError("El registro tiene una fecha de inicio inválida.") from error
    hoy_fecha = datetime.date.today()
    if hoy_fecha < fecha_inicio:
        raise ValueError("No puedes registrar la devolución antes de la fecha de inicio del alquiler.")
    hoy = hoy_fecha.strftime("%d/%m/%Y")
    campos[6] = "Devuelto"
    if len(campos) == 8:
        campos.extend([str(uuid.uuid4()), hoy])
    else:
        if not campos[8].strip():
            campos[8] = str(uuid.uuid4())
        campos[9] = hoy
    lineas[seleccionado["IndiceArchivo"]] = "|".join(campos) + "\n"
    descripcion, nombre_temporal = tempfile.mkstemp(
        prefix=".alquiler_devolucion_", suffix=".tmp", dir=DIRECTORIO_DATOS
    )
    try:
        with os.fdopen(descripcion, "w", encoding="utf-8", newline="") as archivo:
            archivo.writelines(lineas)
        os.replace(nombre_temporal, ARCHIVO_ALQUILERES)
    except Exception:
        if os.path.exists(nombre_temporal):
            os.remove(nombre_temporal)
        raise
    seleccionado.update({"Estado": "Devuelto", "FechaReal": hoy, "Id": campos[8]})
    return seleccionado
