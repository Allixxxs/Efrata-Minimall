"""Estado de sesión compartido por la consola y los servicios."""

from dataclasses import dataclass


@dataclass
class EstadoSesion:
    correo: str = ""
    contrasena: str = ""
    activa: bool = False


sesion_actual = EstadoSesion()


def requerir_usuario(correo=None):
    if not sesion_actual.activa or not sesion_actual.correo:
        raise PermissionError("Debes iniciar sesión para realizar esta operación.")
    correo_solicitado = sesion_actual.correo.casefold()
    if correo is not None and str(correo).strip().casefold() != correo_solicitado:
        raise PermissionError("Solo puedes consultar o modificar tu propia información.")
    return correo_solicitado
