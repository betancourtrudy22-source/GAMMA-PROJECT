"""
Proyecto GAMMA - Vista M2: Actualización de Expedientes
Registro de visitas, signos vitales, diagnósticos y notas médicas.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame, QScrollArea, QGridLayout,
    QMessageBox, QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt
from src.controllers.paciente_controller import paciente_controller


ESTILOS = """
    QLabel[objectName="lbl_campo"] { color: #4A5568; font-size: 11px; font-weight: 600; }
    QLineEdit, QTextEdit, QDoubleSpinBox, QSpinBox {
        background-color: #FFFFFF; border: 1.5px solid #E2E8F0;
        border-radius: 6px; padding: 6px 10px; font-size: 13px; color: #2D3748; min-height: 32px;
    }
    QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus { border-color: #0D3B66; }
    QPushButton#btn_buscar { background-color: #0D3B66; color: white; border: none;
        border-radius: 6px; font-size: 13px; padding: 8px 18px; }
    QPushButton#btn_buscar:hover { background-color: #1565C0; }
    QPushButton#btn_registrar_visita { background-color: #276749; color: white; border: none;
        border-radius: 8px; font-size: 14px; font-weight: bold; padding: 10px 24px; }
    QPushButton#btn_registrar_visita:hover { background-color: #2F855A; }
    QPushButton#btn_agregar_nota { background-color: #2B6CB0; color: white; border: none;
        border-radius: 6px; font-size: 13px; padding: 8px 18px; }
    QPushButton#btn_agregar_nota:hover { background-color: #3182CE; }
"""


def _lbl(texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setObjectName("lbl_campo")
    return lbl


class ExpedienteView(QWidget):
    """Vista M2: Actualización de expediente y registro de visitas."""

    def __init__(self) -> None:
        super().__init__()
        self._paciente_actual = None
        self._setup_ui()
        self.setStyleSheet(ESTILOS)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)

        # Encabezado
        lbl_titulo = QLabel("M2 — Actualización de Expedientes")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #0D3B66;")
        layout.addWidget(lbl_titulo)

        # Búsqueda de paciente
        busq_frame = QFrame()
        busq_frame.setStyleSheet(
            "QFrame { background: #FFFFFF; border-radius: 10px; "
            "border: 1px solid #E2E8F0; }"
        )
        busq_layout = QHBoxLayout(busq_frame)
        busq_layout.setContentsMargins(16, 12, 16, 12)

        lbl_buscar = QLabel("Paciente:")
        lbl_buscar.setStyleSheet("font-weight: 600; color: #2D3748;")
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("Buscar por cédula o nombre...")
        btn_buscar = QPushButton("Buscar")
        btn_buscar.setObjectName("btn_buscar")
        btn_buscar.clicked.connect(self._buscar_paciente)
        self.inp_buscar.returnPressed.connect(self._buscar_paciente)

        self.lbl_paciente_sel = QLabel("Ningún paciente seleccionado")
        self.lbl_paciente_sel.setStyleSheet("color: #718096; font-size: 12px;")

        busq_layout.addWidget(lbl_buscar)
        busq_layout.addWidget(self.inp_buscar)
        busq_layout.addWidget(btn_buscar)
        busq_layout.addSpacing(20)
        busq_layout.addWidget(self.lbl_paciente_sel)
        layout.addWidget(busq_frame)

        # Formulario de visita (scroll)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        form_widget = QWidget()
        self.form_layout = QVBoxLayout(form_widget)
        self.form_layout.setSpacing(18)

        # Panel signos vitales
        self.form_layout.addWidget(self._titulo_seccion("Signos Vitales"))
        grid_sv = QGridLayout()
        grid_sv.setSpacing(10)

        self.inp_presion = QLineEdit()
        self.inp_presion.setPlaceholderText("120/80 mmHg")
        self.inp_temp = QDoubleSpinBox()
        self.inp_temp.setRange(30.0, 45.0)
        self.inp_temp.setValue(36.5)
        self.inp_temp.setSuffix(" °C")
        self.inp_sat_o2 = QDoubleSpinBox()
        self.inp_sat_o2.setRange(50.0, 100.0)
        self.inp_sat_o2.setValue(98.0)
        self.inp_sat_o2.setSuffix(" %")
        self.inp_frec_card = QSpinBox()
        self.inp_frec_card.setRange(30, 250)
        self.inp_frec_card.setValue(72)
        self.inp_frec_card.setSuffix(" bpm")
        self.inp_peso = QDoubleSpinBox()
        self.inp_peso.setRange(1.0, 300.0)
        self.inp_peso.setValue(70.0)
        self.inp_peso.setSuffix(" kg")
        self.inp_talla = QDoubleSpinBox()
        self.inp_talla.setRange(30.0, 250.0)
        self.inp_talla.setValue(170.0)
        self.inp_talla.setSuffix(" cm")

        grid_sv.addWidget(_lbl("Presión Arterial"), 0, 0)
        grid_sv.addWidget(self.inp_presion, 1, 0)
        grid_sv.addWidget(_lbl("Temperatura"), 0, 1)
        grid_sv.addWidget(self.inp_temp, 1, 1)
        grid_sv.addWidget(_lbl("Saturación O₂"), 0, 2)
        grid_sv.addWidget(self.inp_sat_o2, 1, 2)
        grid_sv.addWidget(_lbl("Frec. Cardíaca"), 0, 3)
        grid_sv.addWidget(self.inp_frec_card, 1, 3)
        grid_sv.addWidget(_lbl("Peso"), 2, 0)
        grid_sv.addWidget(self.inp_peso, 3, 0)
        grid_sv.addWidget(_lbl("Talla"), 2, 1)
        grid_sv.addWidget(self.inp_talla, 3, 1)
        self.form_layout.addLayout(grid_sv)

        # Panel clínico
        self.form_layout.addWidget(self._titulo_seccion("Evaluación Clínica"))
        grid_cl = QGridLayout()
        grid_cl.setSpacing(10)

        self.inp_motivo = QTextEdit()
        self.inp_motivo.setPlaceholderText("Motivo de consulta (obligatorio)...")
        self.inp_motivo.setMaximumHeight(70)
        self.inp_area = QLineEdit()
        self.inp_area.setPlaceholderText("Ej. Medicina General, Cardiología")
        self.inp_diag_prelim = QTextEdit()
        self.inp_diag_prelim.setPlaceholderText("Diagnóstico preliminar...")
        self.inp_diag_prelim.setMaximumHeight(70)
        self.inp_tratamiento = QTextEdit()
        self.inp_tratamiento.setPlaceholderText("Plan de tratamiento...")
        self.inp_tratamiento.setMaximumHeight(70)
        self.inp_observaciones = QTextEdit()
        self.inp_observaciones.setPlaceholderText("Observaciones adicionales...")
        self.inp_observaciones.setMaximumHeight(65)

        grid_cl.addWidget(_lbl("Motivo de Consulta *"), 0, 0, 1, 2)
        grid_cl.addWidget(self.inp_motivo, 1, 0, 1, 2)
        grid_cl.addWidget(_lbl("Área / Especialidad"), 2, 0)
        grid_cl.addWidget(self.inp_area, 3, 0)
        grid_cl.addWidget(_lbl("Diagnóstico Preliminar"), 4, 0)
        grid_cl.addWidget(self.inp_diag_prelim, 5, 0)
        grid_cl.addWidget(_lbl("Plan de Tratamiento"), 4, 1)
        grid_cl.addWidget(self.inp_tratamiento, 5, 1)
        grid_cl.addWidget(_lbl("Observaciones"), 6, 0, 1, 2)
        grid_cl.addWidget(self.inp_observaciones, 7, 0, 1, 2)
        self.form_layout.addLayout(grid_cl)

        # Botón registrar visita
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_reg = QPushButton("Registrar Visita Médica")
        btn_reg.setObjectName("btn_registrar_visita")
        btn_reg.clicked.connect(self._registrar_visita)
        btn_row.addWidget(btn_reg)
        self.form_layout.addLayout(btn_row)

        # Panel notas
        self.form_layout.addWidget(self._titulo_seccion("Agregar Nota Médica"))
        self.inp_visita_id = QLineEdit()
        self.inp_visita_id.setPlaceholderText("ID de la visita a anotar")
        self.inp_visita_id.setMaximumWidth(180)
        self.inp_nota = QTextEdit()
        self.inp_nota.setPlaceholderText("Escriba la nota médica aquí...")
        self.inp_nota.setMaximumHeight(90)

        nota_row = QHBoxLayout()
        nota_row.addWidget(QLabel("Visita ID:"))
        nota_row.addWidget(self.inp_visita_id)
        nota_row.addStretch()
        btn_nota = QPushButton("Agregar Nota")
        btn_nota.setObjectName("btn_agregar_nota")
        btn_nota.clicked.connect(self._agregar_nota)
        nota_row.addWidget(btn_nota)

        self.form_layout.addLayout(nota_row)
        self.form_layout.addWidget(self.inp_nota)
        self.form_layout.addSpacing(20)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

    def _titulo_seccion(self, titulo: str) -> QLabel:
        lbl = QLabel(titulo)
        lbl.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #0D3B66;"
            "border-bottom: 2px solid #4ECDC4; padding-bottom: 3px;"
        )
        return lbl

    def _buscar_paciente(self) -> None:
        termino = self.inp_buscar.text().strip()
        if not termino:
            return
        resultados = paciente_controller.buscar_pacientes(termino)
        if resultados:
            self._paciente_actual = resultados[0]
            self.lbl_paciente_sel.setText(
                f"✓ {self._paciente_actual.nombre_completo} "
                f"(ID: {self._paciente_actual.id})"
            )
            self.lbl_paciente_sel.setStyleSheet("color: #276749; font-weight: bold;")
        else:
            self._paciente_actual = None
            self.lbl_paciente_sel.setText("Paciente no encontrado.")
            self.lbl_paciente_sel.setStyleSheet("color: #C53030;")

    def _registrar_visita(self) -> None:
        if self._paciente_actual is None:
            QMessageBox.warning(self, "Atención", "Seleccione un paciente primero.")
            return

        datos = {
            "motivo_consulta": self.inp_motivo.toPlainText(),
            "area_especialidad": self.inp_area.text(),
            "presion_arterial": self.inp_presion.text() or None,
            "temperatura": self.inp_temp.value(),
            "saturacion_oxigeno": self.inp_sat_o2.value(),
            "frecuencia_cardiaca": self.inp_frec_card.value(),
            "peso_kg": self.inp_peso.value(),
            "talla_cm": self.inp_talla.value(),
            "diagnostico_preliminar": self.inp_diag_prelim.toPlainText(),
            "plan_tratamiento": self.inp_tratamiento.toPlainText(),
            "observaciones": self.inp_observaciones.toPlainText(),
        }

        exitoso, mensaje, visita = paciente_controller.registrar_visita(
            self._paciente_actual.id, datos
        )
        if exitoso:
            QMessageBox.information(
                self, "Visita Registrada",
                f"{mensaje}\nID de visita: {visita.id}"
            )
            self.inp_visita_id.setText(str(visita.id))
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def _agregar_nota(self) -> None:
        visita_id_txt = self.inp_visita_id.text().strip()
        if not visita_id_txt.isdigit():
            QMessageBox.warning(self, "Atención", "Ingrese un ID de visita válido.")
            return

        contenido = self.inp_nota.toPlainText().strip()
        exitoso, mensaje = paciente_controller.agregar_nota(
            int(visita_id_txt), contenido
        )
        if exitoso:
            QMessageBox.information(self, "Nota Guardada", mensaje)
            self.inp_nota.clear()
        else:
            QMessageBox.warning(self, "Error", mensaje)
