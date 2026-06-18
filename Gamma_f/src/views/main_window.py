"""
Proyecto GAMMA - Ventana Principal
Dashboard con navegación lateral diferenciada por rol.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush
from src.controllers.auth_controller import auth_controller
from src.models.models import UserRole
from src.views._theme import (
    NAVY, NAVY_DARK, NAVY_MID, TEAL, BG, WHITE, BORDER, TEXT, MUTED,
    LOGOUT_CLR, ROL_ETIQUETAS, ROL_COLORES, ROL_ICONOS
)

from src.views.paciente_view          import PacienteView
from src.views.expediente_view        import ExpedienteView
from src.views.consulta_view          import ConsultaView
from src.views.reporte_view           import ReporteView
from src.views.triage_view            import TriageView
from src.views.enfermeria_view        import EnfermeriaView
from src.views.admin_view             import AdminView
from src.views.recepcion_view         import RecepcionView
from src.views.director_view          import DirectorView
from src.views.acceso_denegado_view   import AccesoDenegadoView
from src.views.mi_evolucion_view      import MIEvolucionView
from src.views.mi_cronicas_view       import MICronicasView
from src.views.mi_interconsultas_view import MIInterconsultasView
from src.views.mi_seguimiento_view    import MISeguimientoView

NAV_TEXT = "#8BAEC8"
NAV_ACT  = "#FFFFFF"

STACK_IDX = {
    "paciente":          0,
    "expediente":        1,
    "consulta":          2,
    "reporte":           3,
    "triage":            4,
    "enfermeria":        5,
    "admin":             6,
    "recepcion":         7,
    "director":          8,
    "denegado":          9,
    "mi_evolucion":     10,  # Medicina Interna — Evolución Médica
    "mi_cronicas":      11,  # Medicina Interna — Enfermedades Crónicas
    "mi_interconsultas":12,  # Medicina Interna — Interconsultas
    "mi_seguimiento":   13,  # Medicina Interna — Seguimiento Clínico
}

MODULOS_POR_ROL = {
    UserRole.ADMIN: [
        ("Gestión de Usuarios",    "⚙️",  STACK_IDX["admin"]),
        ("Registro de Pacientes",  "👤",  STACK_IDX["paciente"]),
        ("Actualizar Expediente",  "📋",  STACK_IDX["expediente"]),
        ("Consulta de Expediente", "🔍",  STACK_IDX["consulta"]),
        ("Reportes",               "📊",  STACK_IDX["reporte"]),
    ],
    UserRole.MEDICO: [
        ("Actualizar Expediente",  "📋",  STACK_IDX["expediente"]),
        ("Consulta de Expediente", "🔍",  STACK_IDX["consulta"]),
    ],
    UserRole.ENF_TRIAGE: [
        ("Triage / Signos Vitales","🚑",  STACK_IDX["triage"]),
        ("Consulta de Expediente", "🔍",  STACK_IDX["consulta"]),
    ],
    UserRole.ENF_ASISTENCIAL: [
        ("Indicaciones y Notas",   "💉",  STACK_IDX["enfermeria"]),
        ("Consulta de Expediente", "🔍",  STACK_IDX["consulta"]),
    ],
    UserRole.DIRECTOR: [
        ("Panel del Director",     "📊",  STACK_IDX["director"]),
        ("Reportes y Estadísticas","📈",  STACK_IDX["reporte"]),
        ("Consulta de Expediente", "🔍",  STACK_IDX["consulta"]),
    ],
    UserRole.RECEPCION: [
        ("Panel de Recepción",     "🏥",  STACK_IDX["recepcion"]),
        ("Consulta de Expediente", "🔍",  STACK_IDX["consulta"]),
    ],
    UserRole.MEDICINA_INTERNA: [
        ("Evolución Médica",       "🗒",  STACK_IDX["mi_evolucion"]),
        ("Enfermedades Crónicas",  "🩺",  STACK_IDX["mi_cronicas"]),
        ("Interconsultas",         "🔗",  STACK_IDX["mi_interconsultas"]),
        ("Seguimiento Clínico",    "📈",  STACK_IDX["mi_seguimiento"]),
        ("Consulta de Expediente", "🔍",  STACK_IDX["consulta"]),
    ],
}


class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._botones_nav = []
        self._setup_ui()

    def _setup_ui(self):
        rol = auth_controller.current_user.rol
        etq = ROL_ETIQUETAS.get(rol, rol.value)
        self.setWindowTitle(f"Sistema GAMMA — {etq}")
        self.setMinimumSize(1200, 750)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._crear_sidebar(etq, rol))

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"QStackedWidget {{ background-color: {BG}; }}")
        self.stack.addWidget(PacienteView())           # 0
        self.stack.addWidget(ExpedienteView())          # 1
        self.stack.addWidget(ConsultaView())            # 2
        self.stack.addWidget(ReporteView())             # 3
        self.stack.addWidget(TriageView())              # 4
        self.stack.addWidget(EnfermeriaView())          # 5
        self.stack.addWidget(AdminView())               # 6
        self.stack.addWidget(RecepcionView())           # 7
        self.stack.addWidget(DirectorView())            # 8
        self.stack.addWidget(AccesoDenegadoView())      # 9
        self.stack.addWidget(MIEvolucionView())          # 10
        self.stack.addWidget(MICronicasView())           # 11
        self.stack.addWidget(MIInterconsultasView())     # 12
        self.stack.addWidget(MISeguimientoView())        # 13
        layout.addWidget(self.stack)

        modulos = MODULOS_POR_ROL.get(rol, [])
        if modulos:
            self._navegar(modulos[0][2])

    def _crear_sidebar(self, etq_rol: str, rol: UserRole) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"QFrame#sidebar {{ background-color: {NAVY_DARK}; }}")
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet(f"background-color: {NAVY_DARK};")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(12)

        logo_box = QFrame()
        logo_box.setFixedSize(44, 44)
        logo_box.setStyleSheet(f"QFrame {{ background-color: rgba(0,184,169,0.18); border: 2px solid {TEAL}; border-radius: 10px; }}")
        ll = QVBoxLayout(logo_box)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo = QLabel("Γ")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet(f"color: {TEAL}; font-size: 22px; font-weight: bold; font-family: Georgia, serif; background: transparent; border: none;")
        ll.addWidget(lbl_logo)

        texto = QWidget()
        texto.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(texto)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(2)
        lbl_nombre = QLabel("GAMMA")
        lbl_nombre.setStyleSheet(f"color: {WHITE}; font-size: 16px; font-weight: 800; letter-spacing: 3px; background: transparent; border: none;")
        lbl_sub = QLabel("EXPEDIENTES MÉDICOS")
        lbl_sub.setStyleSheet("color: #3A6080; font-size: 9px; letter-spacing: 2px; background: transparent; border: none;")
        tl.addWidget(lbl_nombre)
        tl.addWidget(lbl_sub)

        hl.addWidget(logo_box)
        hl.addWidget(texto)
        hl.addStretch()
        sb.addWidget(header)

        sep1 = QFrame()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet("background-color: rgba(255,255,255,0.07); border: none;")
        sb.addWidget(sep1)

        # Bloque usuario
        user_block = QWidget()
        user_block.setFixedHeight(76)
        user_block.setStyleSheet("background-color: rgba(0,0,0,0.20);")
        ul = QVBoxLayout(user_block)
        ul.setContentsMargins(18, 12, 18, 12)
        ul.setSpacing(3)

        usuario = auth_controller.current_user
        color_rol = ROL_COLORES.get(rol, TEAL)
        icono_rol = ROL_ICONOS.get(rol, "👤")

        lbl_name = QLabel(f"{icono_rol}  {usuario.nombre_completo[:22]}")
        lbl_name.setStyleSheet(f"color: #D4E4F0; font-size: 13px; font-weight: 700; background: transparent; border: none;")
        lbl_role = QLabel(etq_rol.upper())
        lbl_role.setStyleSheet(f"color: {color_rol}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; background: transparent; border: none;")
        ul.addWidget(lbl_name)
        ul.addWidget(lbl_role)
        sb.addWidget(user_block)

        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: rgba(255,255,255,0.07); border: none;")
        sb.addWidget(sep2)
        sb.addSpacing(10)

        lbl_mod = QLabel("MÓDULOS")
        lbl_mod.setStyleSheet("color: #2A4F6A; font-size: 9px; font-weight: 700; letter-spacing: 2px; padding-left: 20px; background: transparent; border: none;")
        sb.addWidget(lbl_mod)
        sb.addSpacing(6)

        # Botones de navegación
        modulos = MODULOS_POR_ROL.get(rol, [])
        for i, (texto_btn, icono, stack_idx) in enumerate(modulos):
            btn = QPushButton(f"  {icono}  {texto_btn}")
            btn.setObjectName(f"btn_nav_{i}")
            btn.setFixedHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {NAV_TEXT};
                    border: none;
                    border-left: 3px solid transparent;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                    padding-left: 20px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255,255,255,0.07);
                    color: {WHITE};
                    border-left: 3px solid rgba(0,184,169,0.5);
                }}
                QPushButton:checked {{
                    background-color: rgba(0,184,169,0.14);
                    color: {WHITE};
                    border-left: 3px solid {TEAL};
                    font-weight: 700;
                }}
            """)
            btn.clicked.connect(lambda chk, idx=stack_idx: self._navegar(idx))
            self._botones_nav.append((btn, stack_idx))
            sb.addWidget(btn)

        sb.addStretch()

        sep3 = QFrame()
        sep3.setFixedHeight(1)
        sep3.setStyleSheet("background-color: rgba(255,255,255,0.07); border: none;")
        sb.addWidget(sep3)
        sb.addSpacing(12)

        btn_logout = QPushButton("↩   Cerrar Sesión")
        btn_logout.setFixedHeight(38)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {LOGOUT_CLR};
                border: 1px solid rgba(252,129,129,0.35);
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                margin: 0 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(252,129,129,0.12);
                border-color: {LOGOUT_CLR};
            }}
        """)
        btn_logout.clicked.connect(self._cerrar_sesion)
        sb.addWidget(btn_logout)
        sb.addSpacing(14)

        if self._botones_nav:
            self._botones_nav[0][0].setChecked(True)

        return sidebar

    def _navegar(self, indice: int):
        self.stack.setCurrentIndex(indice)
        for btn, idx in self._botones_nav:
            btn.setChecked(idx == indice)

    def _cerrar_sesion(self):
        resp = QMessageBox.question(
            self, "Cerrar Sesión", "¿Desea cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            auth_controller.logout()
            self.logout_signal.emit()
            self.close()
