"""
Proyecto GAMMA - Vista M1: Registro de Pacientes
Formulario de captura de datos personales y médicos iniciales.
"""

from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QTextEdit, QFrame,
    QScrollArea, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from src.models.models import BloodType, Gender
from src.controllers.paciente_controller import paciente_controller


ESTILOS_COMUNES = """
    QLabel[objectName="lbl_campo"] {
        color: #4A5568;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    QLineEdit, QTextEdit, QComboBox, QDateEdit {
        background-color: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
        color: #2D3748;
        min-height: 32px;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
        border-color: #0D3B66;
    }
    QPushButton#btn_guardar {
        background-color: #0D3B66;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        padding: 10px 30px;
    }
    QPushButton#btn_guardar:hover { background-color: #1565C0; }
    QPushButton#btn_limpiar {
        background-color: #EDF2F7;
        color: #4A5568;
        border: none;
        border-radius: 8px;
        font-size: 13px;
        padding: 10px 24px;
    }
    QPushButton#btn_limpiar:hover { background-color: #E2E8F0; }
"""


def _lbl(texto: str) -> QLabel:
    """Crea un label de campo con estilo."""
    lbl = QLabel(texto)
    lbl.setObjectName("lbl_campo")
    return lbl


class PacienteView(QWidget):
    """Vista del Módulo M1: Registro de nuevos pacientes."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self.setStyleSheet(ESTILOS_COMUNES)

    def _setup_ui(self) -> None:
        """Construye el formulario de registro."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(0)

        # Encabezado
        encabezado = QFrame()
        encabezado.setObjectName("encabezado_modulo")
        enc_layout = QHBoxLayout(encabezado)
        lbl_titulo = QLabel("M1 — Registro de Pacientes")
        lbl_titulo.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0D3B66;"
        )
        lbl_desc = QLabel("Captura de datos personales y médicos iniciales")
        lbl_desc.setStyleSheet("color: #718096; font-size: 13px;")
        enc_layout.addWidget(lbl_titulo)
        enc_layout.addStretch()
        enc_layout.addWidget(lbl_desc)
        layout.addWidget(encabezado)
        layout.addSpacing(20)

        # Scroll para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)

        # Sección 1: Identificación
        form_layout.addWidget(self._crear_seccion("Datos de Identificación"))
        grid1 = QGridLayout()
        grid1.setSpacing(12)

        self.inp_cedula = QLineEdit()
        self.inp_cedula.setPlaceholderText("Ej. 8-123-456")
        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Primer nombre")
        self.inp_apellido = QLineEdit()
        self.inp_apellido.setPlaceholderText("Primer apellido")
        self.inp_fecha_nac = QDateEdit()
        self.inp_fecha_nac.setDisplayFormat("dd/MM/yyyy")
        self.inp_fecha_nac.setDate(QDate(1990, 1, 1))
        self.inp_fecha_nac.setCalendarPopup(True)
        self.cmb_genero = QComboBox()
        for g in Gender:
            self.cmb_genero.addItem(g.value, g)
        self.inp_nacionalidad = QLineEdit()
        self.inp_nacionalidad.setPlaceholderText("Panameño/a")
        self.inp_telefono = QLineEdit()
        self.inp_telefono.setPlaceholderText("6000-0000")
        self.inp_direccion = QTextEdit()
        self.inp_direccion.setPlaceholderText("Dirección completa")
        self.inp_direccion.setMaximumHeight(70)
        self.inp_contacto_emerg = QLineEdit()
        self.inp_contacto_emerg.setPlaceholderText("Nombre del contacto")
        self.inp_tel_emerg = QLineEdit()
        self.inp_tel_emerg.setPlaceholderText("6000-0001")

        grid1.addWidget(_lbl("Cédula / ID *"), 0, 0)
        grid1.addWidget(self.inp_cedula, 1, 0)
        grid1.addWidget(_lbl("Nombre *"), 0, 1)
        grid1.addWidget(self.inp_nombre, 1, 1)
        grid1.addWidget(_lbl("Apellido *"), 0, 2)
        grid1.addWidget(self.inp_apellido, 1, 2)

        grid1.addWidget(_lbl("Fecha de Nacimiento *"), 2, 0)
        grid1.addWidget(self.inp_fecha_nac, 3, 0)
        grid1.addWidget(_lbl("Género *"), 2, 1)
        grid1.addWidget(self.cmb_genero, 3, 1)
        grid1.addWidget(_lbl("Nacionalidad"), 2, 2)
        grid1.addWidget(self.inp_nacionalidad, 3, 2)

        grid1.addWidget(_lbl("Teléfono"), 4, 0)
        grid1.addWidget(self.inp_telefono, 5, 0)
        grid1.addWidget(_lbl("Contacto de Emergencia"), 4, 1)
        grid1.addWidget(self.inp_contacto_emerg, 5, 1)
        grid1.addWidget(_lbl("Tel. Emergencia"), 4, 2)
        grid1.addWidget(self.inp_tel_emerg, 5, 2)

        grid1.addWidget(_lbl("Dirección"), 6, 0)
        grid1.addWidget(self.inp_direccion, 7, 0, 1, 3)

        form_layout.addLayout(grid1)

        # Sección 2: Datos Médicos
        form_layout.addWidget(self._crear_seccion("Datos Médicos Iniciales"))
        grid2 = QGridLayout()
        grid2.setSpacing(12)

        self.cmb_tipo_sangre = QComboBox()
        self.cmb_tipo_sangre.addItem("— No especificado —", None)
        for bt in BloodType:
            self.cmb_tipo_sangre.addItem(bt.value, bt)

        self.inp_alergias = QTextEdit()
        self.inp_alergias.setPlaceholderText("Liste alergias conocidas")
        self.inp_alergias.setMaximumHeight(65)
        self.inp_enf_cronicas = QTextEdit()
        self.inp_enf_cronicas.setPlaceholderText("Enfermedades crónicas diagnosticadas")
        self.inp_enf_cronicas.setMaximumHeight(65)
        self.inp_medicamentos = QTextEdit()
        self.inp_medicamentos.setPlaceholderText("Medicamentos actuales")
        self.inp_medicamentos.setMaximumHeight(65)
        self.inp_antecedentes = QTextEdit()
        self.inp_antecedentes.setPlaceholderText("Antecedentes familiares relevantes")
        self.inp_antecedentes.setMaximumHeight(65)
        self.inp_vacunas = QTextEdit()
        self.inp_vacunas.setPlaceholderText("Vacunas aplicadas")
        self.inp_vacunas.setMaximumHeight(65)
        self.inp_cirugias = QTextEdit()
        self.inp_cirugias.setPlaceholderText("Cirugías previas")
        self.inp_cirugias.setMaximumHeight(65)

        grid2.addWidget(_lbl("Tipo de Sangre"), 0, 0)
        grid2.addWidget(self.cmb_tipo_sangre, 1, 0)

        grid2.addWidget(_lbl("Alergias"), 2, 0)
        grid2.addWidget(self.inp_alergias, 3, 0)
        grid2.addWidget(_lbl("Enfermedades Crónicas"), 2, 1)
        grid2.addWidget(self.inp_enf_cronicas, 3, 1)

        grid2.addWidget(_lbl("Medicamentos Actuales"), 4, 0)
        grid2.addWidget(self.inp_medicamentos, 5, 0)
        grid2.addWidget(_lbl("Antecedentes Familiares"), 4, 1)
        grid2.addWidget(self.inp_antecedentes, 5, 1)

        grid2.addWidget(_lbl("Vacunas Aplicadas"), 6, 0)
        grid2.addWidget(self.inp_vacunas, 7, 0)
        grid2.addWidget(_lbl("Cirugías Previas"), 6, 1)
        grid2.addWidget(self.inp_cirugias, 7, 1)

        form_layout.addLayout(grid2)

        # Botones de acción
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        btn_limpiar = QPushButton("Limpiar Formulario")
        btn_limpiar.setObjectName("btn_limpiar")
        btn_limpiar.clicked.connect(self._limpiar)
        self.btn_guardar = QPushButton("Registrar Paciente")
        self.btn_guardar.setObjectName("btn_guardar")
        self.btn_guardar.clicked.connect(self._guardar)
        botones_layout.addWidget(btn_limpiar)
        botones_layout.addSpacing(10)
        botones_layout.addWidget(self.btn_guardar)
        form_layout.addLayout(botones_layout)
        form_layout.addSpacing(20)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

    def _crear_seccion(self, titulo: str) -> QLabel:
        """Crea un título de sección en el formulario."""
        lbl = QLabel(titulo)
        lbl.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #0D3B66; "
            "border-bottom: 2px solid #4ECDC4; padding-bottom: 4px;"
        )
        return lbl

    def _guardar(self) -> None:
        """Recopila datos del formulario y llama al controlador."""
        fecha_qdate = self.inp_fecha_nac.date()
        fecha_py = date(
            fecha_qdate.year(), fecha_qdate.month(), fecha_qdate.day()
        )

        datos = {
            "cedula": self.inp_cedula.text(),
            "nombre": self.inp_nombre.text(),
            "apellido": self.inp_apellido.text(),
            "fecha_nacimiento": fecha_py,
            "genero": self.cmb_genero.currentData(),
            "nacionalidad": self.inp_nacionalidad.text(),
            "telefono": self.inp_telefono.text(),
            "direccion": self.inp_direccion.toPlainText(),
            "contacto_emergencia": self.inp_contacto_emerg.text(),
            "telefono_emergencia": self.inp_tel_emerg.text(),
            "tipo_sangre": self.cmb_tipo_sangre.currentData(),
            "alergias": self.inp_alergias.toPlainText(),
            "enfermedades_cronicas": self.inp_enf_cronicas.toPlainText(),
            "medicamentos_actuales": self.inp_medicamentos.toPlainText(),
            "antecedentes_familiares": self.inp_antecedentes.toPlainText(),
            "vacunas_aplicadas": self.inp_vacunas.toPlainText(),
            "cirugias_previas": self.inp_cirugias.toPlainText(),
        }

        self.btn_guardar.setEnabled(False)
        exitoso, mensaje, _ = paciente_controller.registrar_paciente(datos)
        self.btn_guardar.setEnabled(True)

        if exitoso:
            QMessageBox.information(self, "Éxito", mensaje)
            self._limpiar()
        else:
            QMessageBox.warning(self, "Error de Validación", mensaje)

    def _limpiar(self) -> None:
        """Reinicia todos los campos del formulario."""
        for widget in self.findChildren(QLineEdit):
            widget.clear()
        for widget in self.findChildren(QTextEdit):
            widget.clear()
        self.cmb_genero.setCurrentIndex(0)
        self.cmb_tipo_sangre.setCurrentIndex(0)
        self.inp_fecha_nac.setDate(QDate(1990, 1, 1))
        self.inp_cedula.setFocus()
