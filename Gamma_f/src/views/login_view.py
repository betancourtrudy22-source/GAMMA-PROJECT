"""
Proyecto GAMMA - Ventana de Login
Autenticación con diseño hospitalario moderno y limpio.
ISO 27001 - Autenticación segura.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from src.controllers.auth_controller import auth_controller

NAVY      = "#0A2540"
NAVY2     = "#123059"
TEAL      = "#00B8A9"
WHITE     = "#FFFFFF"
BG        = "#F0F4F9"
BORDER    = "#D1DCE8"
TEXT      = "#1A2B3C"
MUTED     = "#64748B"
DANGER    = "#C53030"
LABEL_CLR = "#7A92A8"

QSS = f"""
    QWidget#login_root {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #0A2540, stop:0.5 #0E3057, stop:1 #061829);
    }}
    QFrame#card {{
        background-color: {WHITE};
        border-radius: 20px;
    }}
    QFrame#card_header {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 {NAVY}, stop:1 {NAVY2});
        border-top-left-radius: 20px;
        border-top-right-radius: 20px;
    }}
    QFrame#logo_circle {{
        background-color: rgba(0,184,169,0.15);
        border: 2.5px solid {TEAL};
        border-radius: 36px;
    }}
    QLabel#lbl_logo {{
        color: {TEAL};
        font-size: 38px;
        font-weight: bold;
        font-family: Georgia, serif;
    }}
    QLabel#lbl_titulo {{
        color: {WHITE};
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }}
    QLabel#lbl_subtitulo {{
        color: #8BBCDD;
        font-size: 11px;
        letter-spacing: 2px;
    }}
    QFrame#card_body {{
        background-color: {WHITE};
        border-bottom-left-radius: 20px;
        border-bottom-right-radius: 20px;
    }}
    QLabel#lbl_campo {{
        color: {LABEL_CLR};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    QLineEdit#input_campo {{
        background-color: #F7FAFC;
        border: 1.5px solid {BORDER};
        border-radius: 10px;
        padding: 0 14px;
        font-size: 14px;
        color: {TEXT};
        selection-background-color: {TEAL};
    }}
    QLineEdit#input_campo:focus {{
        border-color: {NAVY};
        background-color: {WHITE};
    }}
    QLineEdit#input_campo:hover {{ border-color: #A8BDD4; }}
    QPushButton#btn_login {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {NAVY}, stop:1 {NAVY2});
        color: {WHITE};
        border: none;
        border-radius: 11px;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }}
    QPushButton#btn_login:hover {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {NAVY2}, stop:1 #1A3F70);
    }}
    QPushButton#btn_login:pressed {{ background-color: #061829; }}
    QPushButton#btn_login:disabled {{ background-color: #B0BEC5; color: #78909C; }}
    QLabel#lbl_error {{
        color: {DANGER};
        font-size: 12px;
        font-weight: 600;
        background-color: #FFF5F5;
        border: 1px solid #FEB2B2;
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QLabel#lbl_version {{ color: #A0AEC0; font-size: 10px; }}
    QFrame#divider {{
        background-color: {BORDER};
        max-height: 1px;
    }}
"""


class LoginWindow(QWidget):
    """Ventana de inicio de sesión del Sistema GAMMA."""

    login_exitoso = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("login_root")
        self._setup_ui()
        self.setStyleSheet(QSS)

    def _setup_ui(self) -> None:
        self.setWindowTitle("Sistema GAMMA — Expedientes Médicos")
        self.setFixedSize(480, 580)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(30, 30, 30, 30)
        raiz.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Tarjeta ──────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(420)

        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(60)
        sombra.setOffset(0, 12)
        sombra.setColor(QColor(6, 24, 41, 80))
        card.setGraphicsEffect(sombra)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── Cabecera ─────────────────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("card_header")
        header.setFixedHeight(185)
        hl = QVBoxLayout(header)
        hl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hl.setSpacing(10)

        logo_frame = QFrame()
        logo_frame.setObjectName("logo_circle")
        logo_frame.setFixedSize(72, 72)
        ll = QVBoxLayout(logo_frame)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo = QLabel("Γ")
        lbl_logo.setObjectName("lbl_logo")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll.addWidget(lbl_logo)

        lbl_titulo = QLabel("Sistema GAMMA")
        lbl_titulo.setObjectName("lbl_titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_sub = QLabel("GESTIÓN DE EXPEDIENTES MÉDICOS")
        lbl_sub.setObjectName("lbl_subtitulo")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hl.addWidget(logo_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        hl.addWidget(lbl_titulo)
        hl.addWidget(lbl_sub)
        card_layout.addWidget(header)

        # ── Cuerpo ───────────────────────────────────────────────────────────
        body = QFrame()
        body.setObjectName("card_body")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(40, 32, 40, 28)
        bl.setSpacing(14)

        # Usuario
        lbl_u = QLabel("USUARIO")
        lbl_u.setObjectName("lbl_campo")
        self.inp_usuario = QLineEdit()
        self.inp_usuario.setObjectName("input_campo")
        self.inp_usuario.setPlaceholderText("Ingrese su usuario")
        self.inp_usuario.setFixedHeight(46)

        # Contraseña
        lbl_p = QLabel("CONTRASEÑA")
        lbl_p.setObjectName("lbl_campo")
        self.inp_password = QLineEdit()
        self.inp_password.setObjectName("input_campo")
        self.inp_password.setPlaceholderText("Ingrese su contraseña")
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.inp_password.setFixedHeight(46)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("lbl_error")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setVisible(False)

        # Botón
        self.btn_login = QPushButton("  Iniciar Sesión")
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self._intentar_login)

        # Versión
        lbl_ver = QLabel("v1.0.0 — Hospital Gubernamental  ·  UTP Equipo Gamma")
        lbl_ver.setObjectName("lbl_version")
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bl.addWidget(lbl_u)
        bl.addWidget(self.inp_usuario)
        bl.addSpacing(2)
        bl.addWidget(lbl_p)
        bl.addWidget(self.inp_password)
        bl.addSpacing(4)
        bl.addWidget(self.lbl_error)
        bl.addWidget(self.btn_login)
        bl.addStretch()
        bl.addWidget(lbl_ver)
        card_layout.addWidget(body)

        raiz.addWidget(card)

        self.inp_usuario.returnPressed.connect(lambda: self.inp_password.setFocus())
        self.inp_password.returnPressed.connect(self._intentar_login)

    def _intentar_login(self) -> None:
        self.lbl_error.setVisible(False)
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Verificando...")

        usuario  = self.inp_usuario.text().strip()
        password = self.inp_password.text()

        exitoso, mensaje = auth_controller.login(usuario, password)

        if exitoso:
            self.login_exitoso.emit()
        else:
            self.lbl_error.setText(f"⚠  {mensaje}")
            self.lbl_error.setVisible(True)
            self.inp_password.clear()
            self.inp_password.setFocus()

        self.btn_login.setEnabled(True)
        self.btn_login.setText("  Iniciar Sesión")
