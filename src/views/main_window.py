"""
Proyecto GAMMA - Ventana Principal
Dashboard con navegación lateral para los 4 módulos del sistema.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from src.controllers.auth_controller import auth_controller
from src.models.models import UserRole
from src.views.paciente_view import PacienteView
from src.views.expediente_view import ExpedienteView
from src.views.consulta_view import ConsultaView
from src.views.reporte_view import ReporteView


class MainWindow(QMainWindow):
    """Ventana principal con panel de navegación y área de contenido."""

    logout_signal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._botones_nav: list[QPushButton] = []
        self._setup_ui()
        self._aplicar_estilos()
        self._configurar_permisos()

    def _setup_ui(self) -> None:
        """Construye la interfaz principal."""
        self.setWindowTitle("Sistema GAMMA — Gestión de Expedientes Médicos")
        self.setMinimumSize(1100, 700)

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout = QHBoxLayout(widget_central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar de navegación
        sidebar = self._crear_sidebar()
        layout.addWidget(sidebar)

        # Área de contenido con páginas
        self.stack = QStackedWidget()
        self.stack.setObjectName("stack")

        self.pagina_pacientes = PacienteView()
        self.pagina_expediente = ExpedienteView()
        self.pagina_consulta = ConsultaView()
        self.pagina_reportes = ReporteView()

        self.stack.addWidget(self.pagina_pacientes)   # índice 0
        self.stack.addWidget(self.pagina_expediente)  # índice 1
        self.stack.addWidget(self.pagina_consulta)    # índice 2
        self.stack.addWidget(self.pagina_reportes)    # índice 3

        layout.addWidget(self.stack)

    def _crear_sidebar(self) -> QFrame:
        """Crea el panel de navegación lateral."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo y título
        encabezado = QFrame()
        encabezado.setObjectName("sidebar_header")
        encabezado.setFixedHeight(100)
        enc_layout = QVBoxLayout(encabezado)
        enc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_gamma = QLabel("Γ")
        lbl_gamma.setObjectName("sidebar_logo")
        lbl_gamma.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nombre = QLabel("GAMMA")
        lbl_nombre.setObjectName("sidebar_nombre")
        lbl_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        enc_layout.addWidget(lbl_gamma)
        enc_layout.addWidget(lbl_nombre)
        sidebar_layout.addWidget(encabezado)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("separador")
        sidebar_layout.addWidget(sep)

        # Info del usuario
        usuario = auth_controller.current_user
        lbl_user = QLabel(f"  {usuario.nombre_completo[:22]}")
        lbl_user.setObjectName("lbl_usuario_info")
        lbl_rol = QLabel(f"  {usuario.rol.value.capitalize()}")
        lbl_rol.setObjectName("lbl_rol_info")
        sidebar_layout.addWidget(lbl_user)
        sidebar_layout.addWidget(lbl_rol)
        sidebar_layout.addSpacing(12)

        # Botones de navegación
        nav_items = [
            ("  M1 — Registro", 0, "btn_m1"),
            ("  M2 — Expediente", 1, "btn_m2"),
            ("  M3 — Consulta", 2, "btn_m3"),
            ("  M4 — Reportes", 3, "btn_m4"),
        ]
        for texto, idx, nombre in nav_items:
            btn = QPushButton(texto)
            btn.setObjectName(nombre)
            btn.setFixedHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self._navegar(i))
            self._botones_nav.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Botón cerrar sesión
        btn_logout = QPushButton("  ↩  Cerrar Sesión")
        btn_logout.setObjectName("btn_logout")
        btn_logout.setFixedHeight(44)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self._cerrar_sesion)
        sidebar_layout.addWidget(btn_logout)
        sidebar_layout.addSpacing(10)

        # Activa el primer botón
        self._botones_nav[0].setChecked(True)

        return sidebar

    def _navegar(self, indice: int) -> None:
        """Cambia la página activa y resalta el botón correspondiente."""
        self.stack.setCurrentIndex(indice)
        for i, btn in enumerate(self._botones_nav):
            btn.setChecked(i == indice)

    def _cerrar_sesion(self) -> None:
        """Cierra la sesión del usuario y emite la señal de logout."""
        auth_controller.logout()
        self.logout_signal.emit()
        self.close()

    def _configurar_permisos(self) -> None:
        """Oculta módulos según el rol del usuario."""
        usuario = auth_controller.current_user
        if usuario.rol == UserRole.DIRECTOR:
            # El director solo ve reportes
            self._botones_nav[0].setVisible(False)
            self._botones_nav[1].setVisible(False)
            self._botones_nav[2].setVisible(False)
            self._navegar(3)
        elif usuario.rol == UserRole.ENFERMERA:
            # Enfermera no accede a reportes
            self._botones_nav[3].setVisible(False)

    def _aplicar_estilos(self) -> None:
        """Aplica hoja de estilos QSS."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F4F7FA;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            #sidebar {
                background-color: #0D3B66;
            }
            #sidebar_header {
                background-color: #0A2E52;
            }
            #sidebar_logo {
                color: #4ECDC4;
                font-size: 32px;
                font-weight: bold;
                font-family: Georgia, serif;
            }
            #sidebar_nombre {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 3px;
            }
            #separador {
                color: #1E4E80;
                margin: 0 12px;
            }
            #lbl_usuario_info {
                color: #CBD5E0;
                font-size: 12px;
                padding: 2px 0;
            }
            #lbl_rol_info {
                color: #4ECDC4;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QPushButton[objectName^="btn_m"] {
                background-color: transparent;
                color: #A0C4E8;
                border: none;
                text-align: left;
                font-size: 13px;
                padding-left: 20px;
                border-left: 3px solid transparent;
            }
            QPushButton[objectName^="btn_m"]:hover {
                background-color: #1565C0;
                color: #FFFFFF;
            }
            QPushButton[objectName^="btn_m"]:checked {
                background-color: #1565C0;
                color: #FFFFFF;
                border-left: 3px solid #4ECDC4;
                font-weight: bold;
            }
            #btn_logout {
                background-color: transparent;
                color: #FC8181;
                border: none;
                text-align: left;
                font-size: 12px;
                padding-left: 20px;
            }
            #btn_logout:hover {
                background-color: #742A2A;
                color: #FFFFFF;
            }
            #stack {
                background-color: #F4F7FA;
            }
        """)
