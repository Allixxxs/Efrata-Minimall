"""Estado de sesión compartido por la consola y los servicios."""

from dataclasses import dataclass


@dataclass
class SessionState:
    email: str = ""
    password: str = ""
    active: bool = False


current_session = SessionState()


def require_user(email=None):
    if not current_session.active or not current_session.email:
        raise PermissionError("Debes iniciar sesión para realizar esta operación.")
    requested = current_session.email.casefold()
    if email is not None and str(email).strip().casefold() != requested:
        raise PermissionError("Solo puedes consultar o modificar tu propia información.")
    return requested
