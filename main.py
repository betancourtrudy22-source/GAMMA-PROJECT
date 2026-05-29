"""
Proyecto GAMMA — Sistema de Gestión de Expedientes Médicos
Punto de entrada principal de la aplicación.

Equipo: Gamma | Universidad Tecnológica de Panamá
Curso: Calidad del Software 2026

Stack:
    - Backend: Python 3.11+
    - Frontend: PyQt6
    - Base de datos: PostgreSQL + SQLAlchemy 2.0
    - Seguridad: bcrypt, ISO 27799, ISO 27001

Módulos:
    M1 - Registro de Pacientes
    M2 - Actualización de Expedientes
    M3 - Acceso y Consulta
    M4 - Generación de Reportes

Uso:
    python main.py
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont
from src.models.database import db_manager
from src.views.login_view import LoginWindow
from src.views.main_window import MainWindow


def inicializar_base_de_datos() -> bool:
    """
    Inicializa la conexión y verifica la base de datos.

    Returns:
        bool: True si la conexión es exitosa.
    """
    try:
        db_manager.initialize()
        return db_manager.test_connection()
    except Exception:
        return False


def main() -> int:
    """
    Función principal de la aplicación.

    Returns:
        int: Código de salida del proceso.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema GAMMA")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Hospital Gubernamental — Equipo Gamma")

    # Fuente por defecto de la aplicación
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)

    # Verificar conexión a la base de datos
    if not inicializar_base_de_datos():
        QMessageBox.critical(
            None,
            "Error de Conexión",
            "No se pudo conectar a la base de datos.\n\n"
            "Verifique que PostgreSQL esté activo y que el archivo "
            ".env tenga las credenciales correctas.\n\n"
            "Si es la primera vez que ejecuta el sistema, corra:\n"
            "  python scripts/init_db.py",
        )
        return 1

    # Ventana de login
    login = LoginWindow()

    def mostrar_dashboard() -> None:
        """Abre la ventana principal tras login exitoso."""
        login.hide()
        dashboard = MainWindow()
        dashboard.show()
        # Reconectar señal para volver al login si hace logout
        dashboard.logout_signal.connect(lambda: (login.show(), login.activateWindow()))
        # Guardar referencia para evitar garbage collection
        app._dashboard = dashboard  # noqa: SLF001

    login.login_exitoso.connect(mostrar_dashboard)
    login.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
