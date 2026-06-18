"""
Proyecto GAMMA - Controlador de Autenticación
Gestión de login, sesión activa y auditoría de accesos.
Cumple ISO 27001 (autenticación segura) e ISO 27799.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
import bcrypt
from sqlalchemy.orm import Session
from src.models.models import Usuario, AuditoriaLog, UserRole
from src.models.database import db_manager


class AuthController:
    """
    Controlador de autenticación y gestión de sesión de usuario.
    Implementa hashing bcrypt y registro de auditoría.
    """

    def __init__(self) -> None:
        self._current_user: Optional[Usuario] = None

    @property
    def current_user(self) -> Optional[Usuario]:
        """Retorna el usuario actualmente autenticado."""
        return self._current_user

    @property
    def is_authenticated(self) -> bool:
        """Indica si hay un usuario autenticado."""
        return self._current_user is not None

    def login(self, nombre_usuario: str, password: str) -> tuple[bool, str]:
        """
        Autentica a un usuario en el sistema.

        Args:
            nombre_usuario: Nombre de usuario.
            password: Contraseña en texto plano.

        Returns:
            tuple[bool, str]: (éxito, mensaje).
        """
        if not nombre_usuario or not password:
            return False, "Usuario y contraseña son requeridos."

        session: Session = db_manager.get_session()
        try:
            usuario = (
                session.query(Usuario)
                .filter(
                    Usuario.nombre_usuario == nombre_usuario,
                    Usuario.activo.is_(True)
                )
                .first()
            )

            if usuario is None:
                return False, "Usuario no encontrado o inactivo."

            if not self._verify_password(password, usuario.password_hash):
                self._log_accion(
                    session, usuario.id,
                    "LOGIN_FALLIDO", detalle="Contraseña incorrecta"
                )
                session.commit()
                return False, "Contraseña incorrecta."

            # Actualizar último acceso
            usuario.ultimo_acceso = datetime.utcnow()
            self._log_accion(session, usuario.id, "LOGIN_EXITOSO")
            session.commit()

            # Refrescar para mantener objeto válido fuera de la sesión
            session.refresh(usuario)
            self._current_user = usuario
            return True, f"Bienvenido, {usuario.nombre_completo}."

        except Exception as exc:
            session.rollback()
            return False, f"Error de autenticación: {exc}"
        finally:
            session.close()

    def logout(self) -> None:
        """Cierra la sesión del usuario actual."""
        if self._current_user:
            session: Session = db_manager.get_session()
            try:
                self._log_accion(
                    session, self._current_user.id, "LOGOUT"
                )
                session.commit()
            finally:
                session.close()
        self._current_user = None

    def has_permission(self, roles_permitidos: list[UserRole]) -> bool:
        """
        Verifica si el usuario actual tiene uno de los roles permitidos.

        Args:
            roles_permitidos: Lista de roles con acceso autorizado.

        Returns:
            bool: True si el usuario tiene permiso.
        """
        if not self.is_authenticated:
            return False
        return self._current_user.rol in roles_permitidos

    # ------------------------------------------------------------------
    # Métodos de utilidad
    # ------------------------------------------------------------------

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera el hash bcrypt de una contraseña.

        Args:
            password: Contraseña en texto plano.

        Returns:
            str: Hash bcrypt.
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica una contraseña contra su hash bcrypt.

        Args:
            password: Contraseña en texto plano.
            password_hash: Hash almacenado.

        Returns:
            bool: True si coinciden.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    @staticmethod
    def _log_accion(
        session: Session,
        usuario_id: int,
        accion: str,
        tabla: str = None,
        registro_id: int = None,
        detalle: str = None,
    ) -> None:
        """
        Registra una acción en el log de auditoría (ISO 27799).

        Args:
            session: Sesión activa de SQLAlchemy.
            usuario_id: ID del usuario que realiza la acción.
            accion: Nombre de la acción realizada.
            tabla: Tabla afectada (opcional).
            registro_id: ID del registro afectado (opcional).
            detalle: Detalle adicional (opcional).
        """
        log = AuditoriaLog(
            usuario_id=usuario_id,
            accion=accion,
            tabla_afectada=tabla,
            registro_id=registro_id,
            detalle=detalle,
            timestamp=datetime.utcnow(),
        )
        session.add(log)


# Instancia global del controlador de autenticación
auth_controller = AuthController()
