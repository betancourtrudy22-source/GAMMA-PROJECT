"""
Proyecto GAMMA - Ventana de Login
Interfaz de autenticación con diseño hospitalario limpio.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QIcon, QColor
from src.controllers.auth_controller import auth_controller


class LoginWindow(QWidget):
    """
    Ventana de inicio de sesión del Sistema GAMMA.
    Emite señal login_exitoso cuando el usuario se autentica correctamente.
    """

    login_exitoso = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._aplicar_estilos()

    def _setup_ui(self) -> None:
        """Construye los componentes de la interfaz."""
        self.setWindowTitle("Sistema GAMMA — Expedientes Médicos")
        self.setFixedSize(480, 560)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- Cabecera ---
        self.cabecera = QFrame()
        self.cabecera.setObjectName("cabecera")
        self.cabecera.setFixedHeight(160)
        layout_cabecera = QVBoxLayout(self.cabecera)
        layout_cabecera.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_logo = QLabel("Γ")
        lbl_logo.setObjectName("logo")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_titulo = QLabel("Sistema GAMMA")
        lbl_titulo.setObjectName("titulo")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_subtitulo = QLabel("Gestión de Expedientes Médicos")
        lbl_subtitulo.setObjectName("subtitulo")
        lbl_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_cabecera.addWidget(lbl_logo)
        layout_cabecera.addWidget(lbl_titulo)
        layout_cabecera.addWidget(lbl_subtitulo)

        # --- Cuerpo del formulario ---
        self.cuerpo = QFrame()
        self.cuerpo.setObjectName("cuerpo")
        layout_cuerpo = QVBoxLayout(self.cuerpo)
        layout_cuerpo.setContentsMargins(50, 40, 50, 40)
        layout_cuerpo.setSpacing(16)

        lbl_usuario = QLabel("Usuario")
        lbl_usuario.setObjectName("lbl_campo")
        self.input_usuario = QLineEdit()
        self.input_usuario.setObjectName("input_campo")
        self.input_usuario.setPlaceholderText("Ingrese su usuario")
        self.input_usuario.setFixedHeight(44)

        lbl_password = QLabel("Contraseña")
        lbl_password.setObjectName("lbl_campo")
        self.input_password = QLineEdit()
        self.input_password.setObjectName("input_campo")
        self.input_password.setPlaceholderText("Ingrese su contraseña")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setFixedHeight(44)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("lbl_error")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setWordWrap(True)

        self.btn_login = QPushButton("Iniciar Sesión")
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setFixedHeight(48)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self._intentar_login)

        lbl_version = QLabel("v1.0.0 — Hospital Gubernamental | UTP Equipo Gamma")
        lbl_version.setObjectName("lbl_version")
        lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_cuerpo.addWidget(lbl_usuario)
        layout_cuerpo.addWidget(self.input_usuario)
        layout_cuerpo.addWidget(lbl_password)
        layout_cuerpo.addWidget(self.input_password)
        layout_cuerpo.addSpacing(8)
        layout_cuerpo.addWidget(self.lbl_error)
        layout_cuerpo.addWidget(self.btn_login)
        layout_cuerpo.addStretch()
        layout_cuerpo.addWidget(lbl_version)

        layout_principal.addWidget(self.cabecera)
        layout_principal.addWidget(self.cuerpo)

        # Enter para enviar
        self.input_password.returnPressed.connect(self._intentar_login)
        self.input_usuario.returnPressed.connect(
            lambda: self.input_password.setFocus()
        )

    def _intentar_login(self) -> None:
        """Procesa el intento de inicio de sesión."""
        self.lbl_error.setText("")
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Verificando...")

        usuario = self.input_usuario.text().strip()
        password = self.input_password.text()

        exitoso, mensaje = auth_controller.login(usuario, password)

        if exitoso:
            self.login_exitoso.emit()
        else:
            self.lbl_error.setText(mensaje)
            self.input_password.clear()
            self.input_password.setFocus()

        self.btn_login.setEnabled(True)
        self.btn_login.setText("Iniciar Sesión")

    def _aplicar_estilos(self) -> None:
        """Aplica la hoja de estilos QSS al formulario."""
        self.setStyleSheet("""
            QWidget {
                background-color: #F4F7FA;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            #cabecera {
                background-color: #0D3B66;
            }
            #logo {
                color: #4ECDC4;
                font-size: 48px;
                font-weight: bold;
                font-family: Georgia, serif;
            }
            #titulo {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            #subtitulo {
                color: #8BBCDD;
                font-size: 12px;
                letter-spacing: 2px;
            }
            #cuerpo {
                background-color: #FFFFFF;
                border-radius: 0px;
            }
            #lbl_campo {
                color: #2D3748;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            #input_campo {
                background-color: #F4F7FA;
                border: 2px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: #2D3748;
            }
            #input_campo:focus {
                border-color: #0D3B66;
                background-color: #FFFFFF;
            }
            #btn_login {
                background-color: #0D3B66;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            #btn_login:hover {
                background-color: #1565C0;
            }
            #btn_login:disabled {
                background-color: #A0AEC0;
            }
            #lbl_error {
                color: #E53E3E;
                font-size: 13px;
            }
            #lbl_version {
                color: #A0AEC0;
                font-size: 10px;
            }
        """)
