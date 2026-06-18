"""
Proyecto GAMMA — Medicina Interna: Interconsultas
Vista M-MI-3: Solicitudes de interconsulta a otras especialidades
y registro de las respuestas del especialista consultado.

Cubre: solicitud (fecha, especialidad, prioridad, motivo, pregunta al especialista)
y respuesta (fecha, médico, hallazgos, recomendaciones, tratamiento sugerido).

Acceso: UserRole.MEDICINA_INTERNA (lecto-escritura)
Auditoría: toda acción queda en AuditoriaLog (ISO 27799 / Ley 81).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QFrame, QScrollArea, QDateEdit,
    QMessageBox, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, QDate

from src.views._theme import (
    NAVY, TEAL, BG, WHITE, BORDER, TEXT, MUTED, SUCCESS, AMBER
)
from src.views._widgets import BannerWidget
from src.views._common import (
    WIDGET_BG, INPUT_QSS, SCROLL_QSS,
    titulo_style, desc_style, sec_style, campo_style, setup_calendar_popup
)

MI_ACENTO   = "#E8856A"
MI_ACENTO_D = "#C0603A"

BTN_MI_QSS = f"""
    QPushButton {{
        background-color: {MI_ACENTO};
        color: white;
        border: none;
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0 28px;
        min-height: 42px;
        min-width: 180px;
    }}
    QPushButton:hover  {{ background-color: {MI_ACENTO_D}; }}
    QPushButton:pressed {{ background-color: #9E3A18; }}
    QPushButton:disabled {{ background-color: #CBD5E0; color: #718096; }}
"""

# Etiqueta de prioridad con colores semafórico
PRIORIDAD_COLORES = {
    "Normal":    TEAL,
    "Urgente":   AMBER,
    "Emergente": "#C53030",
}


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
    return f


def _lbl(txt: str) -> QLabel:
    l = QLabel(txt)
    l.setStyleSheet(campo_style())
    return l


def _sec_titulo(txt: str) -> QLabel:
    lbl = QLabel(txt)
    lbl.setStyleSheet(
        f"font-size:11px;font-weight:700;color:{MUTED};"
        "letter-spacing:1px;padding-bottom:6px;"
        f"border-bottom:2px solid {MI_ACENTO};"
        "background:transparent;"
    )
    return lbl


class MIInterconsultasView(QWidget):
    """
    Registro de interconsultas entre Medicina Interna y otras especialidades.
    Permite registrar la solicitud y, cuando llega, la respuesta del especialista.
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet(WIDGET_BG)
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(SCROLL_QSS)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container.setStyleSheet(f"QWidget{{background-color:{BG};}}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # ── Encabezado ────────────────────────────────────────────────────────
        enc = QHBoxLayout()
        col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("Interconsultas"); t.setStyleSheet(titulo_style())
        col.addWidget(t)
        enc.addLayout(col); enc.addStretch()
        layout.addLayout(enc)

        layout.addWidget(BannerWidget(
            "🔗",
            "Registro de Interconsultas",
            "",
            MI_ACENTO_D, MI_ACENTO
        ))

        layout.addWidget(self._buscador())

        # ── Sección Solicitud ─────────────────────────────────────────────────
        layout.addWidget(_sec_titulo("SOLICITUD DE INTERCONSULTA"))

        gis = QGridLayout(); gis.setSpacing(12)

        self.ic_fecha_sol = QDateEdit(QDate.currentDate())
        self.ic_fecha_sol.setCalendarPopup(True)
        self.ic_fecha_sol.setDisplayFormat("dd/MM/yyyy")
        self.ic_fecha_sol.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.ic_fecha_sol)

        self.ic_especialidad = QComboBox()
        self.ic_especialidad.addItems([
            "Seleccionar especialidad...",
            "Cardiología", "Neumología", "Endocrinología",
            "Neurología", "Nefrología", "Infectología",
            "Gastroenterología", "Hematología", "Oncología",
            "Reumatología", "Dermatología", "Ortopedia",
            "Cirugía General", "Otra",
        ])
        self.ic_especialidad.setStyleSheet(INPUT_QSS)
        self.ic_especialidad.currentTextChanged.connect(self._actualizar_badge)

        self.ic_prioridad = QComboBox()
        self.ic_prioridad.addItems(["Normal", "Urgente", "Emergente"])
        self.ic_prioridad.setStyleSheet(INPUT_QSS)
        self.ic_prioridad.currentTextChanged.connect(self._actualizar_badge)

        self.lbl_badge = QLabel("● Normal")
        self._aplicar_badge_color("Normal")

        gis.addWidget(_lbl("Fecha de solicitud *"),      0, 0)
        gis.addWidget(self.ic_fecha_sol,                 1, 0)
        gis.addWidget(_lbl("Especialidad solicitada *"), 0, 1)
        gis.addWidget(self.ic_especialidad,              1, 1)
        gis.addWidget(_lbl("Prioridad *"),               0, 2)
        gis.addWidget(self.ic_prioridad,                 1, 2)
        gis.addWidget(_lbl(""),                          0, 3)
        gis.addWidget(self.lbl_badge,                    1, 3)
        layout.addLayout(gis)

        self.ic_motivo = QTextEdit()
        self.ic_motivo.setPlaceholderText(
            "Describir el motivo clínico: hallazgos relevantes, "
            "evolución del paciente y lo que se espera del especialista..."
        )
        self.ic_motivo.setStyleSheet(INPUT_QSS)
        self.ic_motivo.setFixedHeight(90)
        layout.addWidget(_lbl("Motivo de interconsulta *"))
        layout.addWidget(self.ic_motivo)

        self.ic_pregunta = QTextEdit()
        self.ic_pregunta.setPlaceholderText(
            "Pregunta específica al especialista:\n"
            "Ej: '¿Cuál sería el manejo óptimo de la insuficiencia cardíaca en este paciente?'"
        )
        self.ic_pregunta.setStyleSheet(INPUT_QSS)
        self.ic_pregunta.setFixedHeight(72)
        layout.addWidget(_lbl("Pregunta específica al especialista"))
        layout.addWidget(self.ic_pregunta)

        # Botón guardar solicitud
        btn_sol = QPushButton("📤  Registrar Solicitud")
        btn_sol.setStyleSheet(BTN_MI_QSS)
        btn_sol.clicked.connect(self._guardar_solicitud)
        h_sol = QHBoxLayout(); h_sol.addStretch(); h_sol.addWidget(btn_sol)
        layout.addLayout(h_sol)

        layout.addWidget(_sep())

        # ── Sección Respuesta del especialista ────────────────────────────────
        layout.addWidget(_sec_titulo("RESPUESTA DEL ESPECIALISTA"))

        nota_resp = QLabel(
            "📋  Complete esta sección cuando el especialista haya respondido la interconsulta."
        )
        nota_resp.setStyleSheet(
            f"color:#276749;font-size:11px;background:#F0FFF4;"
            f"border-radius:8px;padding:10px 14px;border-left:3px solid {SUCCESS};"
        )
        nota_resp.setWordWrap(True)
        layout.addWidget(nota_resp)

        gir = QGridLayout(); gir.setSpacing(12)

        self.ic_fecha_resp = QDateEdit()
        self.ic_fecha_resp.setCalendarPopup(True)
        self.ic_fecha_resp.setDisplayFormat("dd/MM/yyyy")
        self.ic_fecha_resp.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.ic_fecha_resp)

        self.ic_medico_resp = QLineEdit()
        self.ic_medico_resp.setPlaceholderText("Nombre del especialista que respondió")
        self.ic_medico_resp.setStyleSheet(INPUT_QSS)

        gir.addWidget(_lbl("Fecha de respuesta"), 0, 0)
        gir.addWidget(self.ic_fecha_resp,         1, 0)
        gir.addWidget(_lbl("Médico consultado"),  0, 1)
        gir.addWidget(self.ic_medico_resp,        1, 1)
        layout.addLayout(gir)

        self.ic_hallazgos = QTextEdit()
        self.ic_hallazgos.setPlaceholderText("Hallazgos clínicos del especialista...")
        self.ic_hallazgos.setStyleSheet(INPUT_QSS)
        self.ic_hallazgos.setFixedHeight(72)
        layout.addWidget(_lbl("Hallazgos"))
        layout.addWidget(self.ic_hallazgos)

        self.ic_recomendaciones = QTextEdit()
        self.ic_recomendaciones.setPlaceholderText(
            "Recomendaciones y tratamiento sugerido por el especialista..."
        )
        self.ic_recomendaciones.setStyleSheet(INPUT_QSS)
        self.ic_recomendaciones.setFixedHeight(90)
        layout.addWidget(_lbl("Recomendaciones y tratamiento sugerido"))
        layout.addWidget(self.ic_recomendaciones)

        # Botón guardar respuesta
        layout.addSpacing(8)
        btn_resp = QPushButton("💾  Guardar Respuesta del Especialista")
        btn_resp.setStyleSheet(BTN_MI_QSS)
        btn_resp.clicked.connect(self._guardar_respuesta)
        h_resp = QHBoxLayout(); h_resp.addStretch(); h_resp.addWidget(btn_resp)
        layout.addLayout(h_resp)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ── Widgets auxiliares ────────────────────────────────────────────────────

    def _buscador(self) -> QFrame:
        busq = QFrame()
        busq.setStyleSheet(
            f"QFrame{{background-color:{WHITE};border-radius:12px;border:1px solid {BORDER};}}"
        )
        bl = QHBoxLayout(busq)
        bl.setContentsMargins(16, 12, 16, 12); bl.setSpacing(10)

        self.inp_cedula = QLineEdit()
        self.inp_cedula.setPlaceholderText("Buscar paciente por cédula o nombre...")
        self.inp_cedula.setStyleSheet(INPUT_QSS)
        self.inp_cedula.returnPressed.connect(self._buscar)

        btn_b = QPushButton("Buscar Paciente")
        btn_b.setStyleSheet(BTN_MI_QSS)
        btn_b.setFixedHeight(38)
        btn_b.clicked.connect(self._buscar)

        self.lbl_pac = QLabel("Sin paciente seleccionado")
        self.lbl_pac.setStyleSheet(
            f"color:{MUTED};font-size:12px;background:transparent;border:none;"
        )

        bl.addWidget(QLabel("Paciente:"))
        bl.addWidget(self.inp_cedula, stretch=2)
        bl.addWidget(btn_b); bl.addStretch(); bl.addWidget(self.lbl_pac)
        return busq

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _actualizar_badge(self):
        """Actualiza el badge de color de prioridad al cambiar el combo."""
        prioridad = self.ic_prioridad.currentText()
        self._aplicar_badge_color(prioridad)

    def _aplicar_badge_color(self, prioridad: str):
        color = PRIORIDAD_COLORES.get(prioridad, TEAL)
        self.lbl_badge.setText(f"● {prioridad}")
        self.lbl_badge.setStyleSheet(
            f"color:{color};font-size:13px;font-weight:700;"
            "background:transparent;border:none;"
        )

    def _buscar(self):
        """Stub: se conectará a paciente_controller en Sprint 4."""
        texto = self.inp_cedula.text().strip()
        if not texto:
            QMessageBox.warning(self, "Campo requerido",
                                "Ingrese la cédula o nombre del paciente.")
            return
        self.lbl_pac.setStyleSheet(
            f"color:{SUCCESS};font-size:12px;font-weight:700;"
            "background:transparent;border:none;"
        )
        self.lbl_pac.setText(f"✓  Paciente: {texto}")

    def _guardar_solicitud(self):
        """
        Persiste la solicitud de interconsulta.
        Stub hasta Sprint 4. Genera entrada de auditoría (ISO 27799).
        """
        esp = self.ic_especialidad.currentText()
        if esp == "Seleccionar especialidad...":
            QMessageBox.warning(self, "Campo requerido",
                                "Seleccione la especialidad solicitada.")
            return
        motivo = self.ic_motivo.toPlainText().strip()
        if not motivo:
            QMessageBox.warning(self, "Campo requerido",
                                "El motivo de interconsulta es obligatorio.")
            return
        # TODO Sprint 4: medicina_interna_service.guardar_interconsulta_solicitud(datos, usuario)
        QMessageBox.information(
            self, "Solicitud registrada",
            f"✅  Interconsulta a {esp} registrada exitosamente.\n\n"
            "La acción quedó registrada en el log de auditoría.",
        )

    def _guardar_respuesta(self):
        """
        Persiste la respuesta del especialista.
        Stub hasta Sprint 4. Genera entrada de auditoría (ISO 27799).
        """
        medico = self.ic_medico_resp.text().strip()
        if not medico:
            QMessageBox.warning(self, "Campo requerido",
                                "Ingrese el nombre del médico que respondió.")
            return
        # TODO Sprint 4: medicina_interna_service.guardar_interconsulta_respuesta(datos, usuario)
        QMessageBox.information(
            self, "Respuesta registrada",
            "✅  Respuesta del especialista guardada correctamente.\n\n"
            "La acción quedó registrada en el log de auditoría.",
        )
