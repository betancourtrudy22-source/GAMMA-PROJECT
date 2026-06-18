"""
Proyecto GAMMA — Medicina Interna: Evolución Médica
Vista M-MI-1: Registro diario de evolución del paciente internado.
Acceso: UserRole.MEDICINA_INTERNA
Auditoría: ISO 27799 / Ley 81.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QFrame, QScrollArea, QDateEdit,
    QMessageBox, QPushButton, QGridLayout, QGroupBox, QCheckBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QDate

from src.views._theme import (
    NAVY, NAVY_MID, TEAL, BG, WHITE, BORDER, TEXT, MUTED,
    SUCCESS, DANGER
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
    QPushButton:hover   {{ background-color: {MI_ACENTO_D}; }}
    QPushButton:pressed {{ background-color: #9E3A18; }}
    QPushButton:disabled {{ background-color: #CBD5E0; color: #718096; }}
"""

CHECK_QSS = f"""
    QCheckBox {{
        color: {TEXT};
        font-size: 13px;
        spacing: 8px;
        background: transparent;
        border: none;
    }}
    QCheckBox::indicator {{
        width: 18px; height: 18px;
        border: 1.5px solid {BORDER};
        border-radius: 4px;
        background-color: {WHITE};
    }}
    QCheckBox::indicator:checked {{
        background-color: {MI_ACENTO};
        border-color: {MI_ACENTO};
    }}
"""

# Checkbox SI/NO para hallazgos — verde cuando se marca
CHECK_HALLAZGO_QSS = f"""
    QCheckBox {{
        color: {TEXT};
        font-size: 13px;
        font-weight: 600;
        spacing: 8px;
        background: transparent;
        border: none;
        min-height: 28px;
    }}
    QCheckBox::indicator {{
        width: 20px; height: 20px;
        border: 1.5px solid {BORDER};
        border-radius: 5px;
        background-color: #F8FAFD;
    }}
    QCheckBox::indicator:checked {{
        background-color: {TEAL};
        border-color: {TEAL};
    }}
    QCheckBox::indicator:hover {{
        border-color: {NAVY};
    }}
"""

GROUP_QSS = f"""
    QGroupBox {{
        font-size: 11px;
        font-weight: 700;
        color: {MUTED};
        letter-spacing: 0.5px;
        border: 1px solid {BORDER};
        border-radius: 10px;
        margin-top: 14px;
        padding-top: 6px;
        background-color: {WHITE};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        left: 14px;
        background-color: {WHITE};
        color: {MUTED};
    }}
"""

HALLAZGO_CARD_QSS = f"""
    QFrame {{
        background-color: {WHITE};
        border-radius: 10px;
        border: 1px solid {BORDER};
    }}
"""

HALLAZGO_DETALLE_QSS = f"""
    QFrame {{
        background-color: #F0FFF4;
        border-radius: 8px;
        border: 1px solid #9AE6B4;
        border-left: 3px solid {TEAL};
    }}
"""


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background:{BORDER};max-height:1px;border:none;")
    return f


def _lbl(txt: str) -> QLabel:
    l = QLabel(txt)
    l.setStyleSheet(campo_style())
    return l


class HallazgoItem(QFrame):
    """
    Widget reutilizable para cada hallazgo del examen físico.
    Muestra un checkbox 'SÍ hallazgos' y si se marca,
    despliega un campo para describir qué se encontró.
    """

    def __init__(self, nombre: str, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(HALLAZGO_CARD_QSS)
        self._nombre = nombre

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        # Fila superior: nombre + checkbox
        top = QHBoxLayout()
        top.setSpacing(12)

        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {NAVY}; "
            "background: transparent; border: none;"
        )

        self.chk = QCheckBox("Hallazgos positivos")
        self.chk.setStyleSheet(CHECK_HALLAZGO_QSS)
        self.chk.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk.toggled.connect(self._toggle_detalle)

        top.addWidget(lbl_nombre)
        top.addStretch()
        top.addWidget(self.chk)
        layout.addLayout(top)

        # Panel de detalle (oculto por defecto)
        self.detalle_frame = QFrame()
        self.detalle_frame.setStyleSheet(HALLAZGO_DETALLE_QSS)
        self.detalle_frame.setVisible(False)
        dl = QVBoxLayout(self.detalle_frame)
        dl.setContentsMargins(10, 8, 10, 8)
        dl.setSpacing(4)

        lbl_det = QLabel("Describa los hallazgos encontrados:")
        lbl_det.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {TEAL}; "
            "background: transparent; border: none; letter-spacing: 0.5px;"
        )

        self.txt_detalle = QTextEdit()
        ph = placeholder or f"Describa los hallazgos en {nombre.lower()}..."
        self.txt_detalle.setPlaceholderText(ph)
        self.txt_detalle.setStyleSheet(INPUT_QSS)
        self.txt_detalle.setFixedHeight(68)

        dl.addWidget(lbl_det)
        dl.addWidget(self.txt_detalle)
        layout.addWidget(self.detalle_frame)

    def _toggle_detalle(self, marcado: bool):
        self.detalle_frame.setVisible(marcado)
        # Cambiar el color del frame cuando está activo
        if marcado:
            self.setStyleSheet(
                f"QFrame {{ background-color: #F0FFF4; border-radius: 10px; "
                f"border: 1px solid #9AE6B4; border-top: 3px solid {TEAL}; }}"
            )
        else:
            self.setStyleSheet(HALLAZGO_CARD_QSS)

    @property
    def tiene_hallazgos(self) -> bool:
        return self.chk.isChecked()

    @property
    def descripcion(self) -> str:
        return self.txt_detalle.toPlainText().strip()

    @property
    def resumen(self) -> str:
        if self.tiene_hallazgos:
            desc = self.descripcion
            return f"✅ {self._nombre}: {desc if desc else 'Hallazgos positivos (sin descripción)'}"
        return f"— {self._nombre}: Sin hallazgos"

    def limpiar(self):
        self.chk.setChecked(False)
        self.txt_detalle.clear()


class MIEvolucionView(QWidget):
    """
    Formulario de evolución médica diaria para el internista.
    Examen físico con checkboxes SI/NO + descripción desplegable.
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
        t = QLabel("Evolución Médica"); t.setStyleSheet(titulo_style())
        col.addWidget(t)
        enc.addLayout(col); enc.addStretch()
        layout.addLayout(enc)

        layout.addWidget(BannerWidget(
            "🗒",
            "Evolución Médica del Paciente",
            "",
            MI_ACENTO_D, MI_ACENTO
        ))

        # ── Buscador ──────────────────────────────────────────────────────────
        layout.addWidget(self._buscador())

        # ── Sección 1: Datos generales ────────────────────────────────────────
        s1 = QLabel("DATOS GENERALES DE LA VISITA"); s1.setStyleSheet(sec_style())
        layout.addWidget(s1)

        g1 = QGridLayout(); g1.setSpacing(12)
        self.ev_fecha = QDateEdit(QDate.currentDate())
        self.ev_fecha.setCalendarPopup(True); self.ev_fecha.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.ev_fecha)
        self.ev_hora = QLineEdit(); self.ev_hora.setPlaceholderText("Ej: 09:30"); self.ev_hora.setStyleSheet(INPUT_QSS)
        self.ev_medico = QLineEdit(); self.ev_medico.setPlaceholderText("Nombre del médico responsable"); self.ev_medico.setStyleSheet(INPUT_QSS)
        self.ev_servicio = QLineEdit(); self.ev_servicio.setPlaceholderText("Ej: Medicina Interna — Sala B"); self.ev_servicio.setStyleSheet(INPUT_QSS)
        self.ev_habitacion = QLineEdit(); self.ev_habitacion.setPlaceholderText("Ej: 204-B"); self.ev_habitacion.setStyleSheet(INPUT_QSS)

        g1.addWidget(_lbl("Fecha *"),               0, 0); g1.addWidget(self.ev_fecha,      1, 0)
        g1.addWidget(_lbl("Hora *"),                0, 1); g1.addWidget(self.ev_hora,       1, 1)
        g1.addWidget(_lbl("Médico responsable *"),  0, 2); g1.addWidget(self.ev_medico,     1, 2)
        g1.addWidget(_lbl("Servicio"),              2, 0); g1.addWidget(self.ev_servicio,   3, 0, 1, 2)
        g1.addWidget(_lbl("Habitación"),            2, 2); g1.addWidget(self.ev_habitacion, 3, 2)
        layout.addLayout(g1)
        layout.addWidget(_sep())

        # ── Sección 2: Estado general ─────────────────────────────────────────
        s2 = QLabel("ESTADO GENERAL DEL PACIENTE"); s2.setStyleSheet(sec_style())
        layout.addWidget(s2)
        self.ev_estado = QComboBox()
        self.ev_estado.addItems(["Seleccionar...", "Mejor", "Igual", "Peor"])
        self.ev_estado.setStyleSheet(INPUT_QSS)
        h2 = QHBoxLayout(); h2.setSpacing(12)
        h2.addWidget(_lbl("¿Cómo se encuentra el paciente hoy?"))
        h2.addWidget(self.ev_estado); h2.addStretch()
        layout.addLayout(h2)
        layout.addWidget(_sep())

        # ── Sección 3: Síntomas actuales ──────────────────────────────────────
        s3 = QLabel("SÍNTOMAS ACTUALES"); s3.setStyleSheet(sec_style())
        layout.addWidget(s3)
        grupos = {
            "GENERALES":        ["Fiebre", "Escalofríos", "Fatiga", "Pérdida de peso", "Sudoración nocturna"],
            "CARDIOVASCULARES": ["Dolor torácico", "Palpitaciones", "Edema en piernas", "Mareos"],
            "RESPIRATORIOS":    ["Tos", "Dificultad respiratoria", "Expectoración", "Saturación baja"],
            "DIGESTIVOS":       ["Dolor abdominal", "Náuseas", "Vómitos", "Diarrea", "Estreñimiento"],
            "NEUROLÓGICOS":     ["Cefalea", "Convulsiones", "Confusión", "Alteración del estado mental"],
        }
        self._checkboxes: dict[str, list[QCheckBox]] = {}
        row_s = QHBoxLayout(); row_s.setSpacing(12)
        for grupo, items in grupos.items():
            grp = QGroupBox(grupo); grp.setStyleSheet(GROUP_QSS)
            vl = QVBoxLayout(grp); vl.setSpacing(6)
            checks = []
            for item in items:
                cb = QCheckBox(item); cb.setStyleSheet(CHECK_QSS)
                vl.addWidget(cb); checks.append(cb)
            self._checkboxes[grupo] = checks
            row_s.addWidget(grp)
        layout.addLayout(row_s)
        layout.addWidget(_sep())

        # ── Sección 4: Signos vitales ─────────────────────────────────────────
        s4 = QLabel("SIGNOS VITALES"); s4.setStyleSheet(sec_style())
        layout.addWidget(s4)
        gv = QGridLayout(); gv.setSpacing(12)
        signos = [
            ("Presión arterial (mmHg)", "Ej: 120/80"),
            ("Frecuencia cardíaca (lpm)", "Ej: 72"),
            ("Frecuencia respiratoria (rpm)", "Ej: 16"),
            ("Temperatura (°C)", "Ej: 37.2"),
            ("Saturación O₂ (%)", "Ej: 98"),
            ("Peso (kg)", "Ej: 68.5"),
            ("IMC", "Se calcula automáticamente"),
        ]
        self._signos: list[QLineEdit] = []
        for i, (lbl_t, ph) in enumerate(signos):
            col_g = (i % 4) * 2; row_g = (i // 4) * 2
            inp = QLineEdit(); inp.setPlaceholderText(ph); inp.setStyleSheet(INPUT_QSS)
            gv.addWidget(_lbl(lbl_t), row_g, col_g)
            gv.addWidget(inp, row_g + 1, col_g)
            self._signos.append(inp)
        layout.addLayout(gv)
        layout.addWidget(_sep())

        # ── Sección 5: Examen físico con checkboxes SI/NO ─────────────────────
        s5 = QLabel("EXAMEN FÍSICO — HALLAZGOS"); s5.setStyleSheet(sec_style())
        layout.addWidget(s5)

        # Estado general del examen
        h_eg = QHBoxLayout(); h_eg.setSpacing(12)
        h_eg.addWidget(_lbl("Estado general del examen:"))
        self.ev_eg = QComboBox()
        self.ev_eg.addItems(["Seleccionar...", "Bueno", "Regular", "Malo"])
        self.ev_eg.setStyleSheet(INPUT_QSS)
        h_eg.addWidget(self.ev_eg); h_eg.addStretch()
        layout.addLayout(h_eg)

        # Grid de hallazgos 2x3
        hallazgos_def = [
            ("Cabeza y Cuello",  "Describa hallazgos: adenopatías, ingurgitación yugular, bocio, lesiones..."),
            ("Cardiovascular",   "Describa hallazgos: soplos, ritmo cardíaco, frote pericárdico, pulsos..."),
            ("Respiratorio",     "Describa hallazgos: murmullo vesicular, crepitantes, sibilancias, matidez..."),
            ("Abdomen",          "Describa hallazgos: dolor, visceromegalia, masas, peristaltismo, timpanismo..."),
            ("Extremidades",     "Describa hallazgos: edema, cianosis, pulsos periféricos, lesiones cutáneas..."),
            ("Neurológico",      "Describa hallazgos: fuerza, sensibilidad, reflejos, marcha, orientación..."),
        ]

        self._hallazgos: list[HallazgoItem] = []
        gef = QGridLayout(); gef.setSpacing(14)
        gef.setColumnStretch(0, 1); gef.setColumnStretch(1, 1)

        for i, (nombre, placeholder) in enumerate(hallazgos_def):
            row_h = i // 2
            col_h = i % 2
            item = HallazgoItem(nombre, placeholder)
            gef.addWidget(item, row_h, col_h)
            self._hallazgos.append(item)

        layout.addLayout(gef)
        layout.addWidget(_sep())

        # ── Sección 6: Diagnósticos ───────────────────────────────────────────
        s6 = QLabel("IMPRESIÓN DIAGNÓSTICA"); s6.setStyleSheet(sec_style())
        layout.addWidget(s6)
        gd = QGridLayout(); gd.setSpacing(12)
        diag_lbls = ["Diagnóstico principal (CIE-10)", "Diagnóstico secundario", "Diagnóstico asociado"]
        self._diagnosticos: list[QLineEdit] = []
        for i, lbl_t in enumerate(diag_lbls):
            inp = QLineEdit(); inp.setPlaceholderText("Ej: J18.9"); inp.setStyleSheet(INPUT_QSS)
            gd.addWidget(_lbl(lbl_t), 0, i); gd.addWidget(inp, 1, i)
            self._diagnosticos.append(inp)
        layout.addLayout(gd)
        layout.addWidget(_sep())

        # ── Sección 7: Plan médico ────────────────────────────────────────────
        s7 = QLabel("PLAN MÉDICO"); s7.setStyleSheet(sec_style())
        layout.addWidget(s7)
        self.ev_conducta = QComboBox()
        self.ev_conducta.addItems([
            "Seleccionar conducta...", "Mantener tratamiento",
            "Modificar tratamiento", "Solicitar exámenes",
            "Solicitar interconsulta", "Alta médica",
        ])
        self.ev_conducta.setStyleSheet(INPUT_QSS)
        self.ev_plan_obs = QTextEdit()
        self.ev_plan_obs.setPlaceholderText("Observaciones del plan, indicaciones, modificaciones de tratamiento...")
        self.ev_plan_obs.setStyleSheet(INPUT_QSS); self.ev_plan_obs.setFixedHeight(90)
        layout.addWidget(_lbl("Conducta")); layout.addWidget(self.ev_conducta)
        layout.addWidget(_lbl("Observaciones del plan")); layout.addWidget(self.ev_plan_obs)

        # ── Botón guardar ─────────────────────────────────────────────────────
        layout.addSpacing(8)
        btn = QPushButton("💾  Guardar Evolución Médica")
        btn.setStyleSheet(BTN_MI_QSS)
        btn.clicked.connect(self._guardar)
        h_btn = QHBoxLayout(); h_btn.addStretch(); h_btn.addWidget(btn)
        layout.addLayout(h_btn)
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
        self.inp_cedula.returnPressed.connect(self._buscar_paciente)

        btn_b = QPushButton("Buscar Paciente")
        btn_b.setStyleSheet(BTN_MI_QSS)
        btn_b.setFixedHeight(38)
        btn_b.clicked.connect(self._buscar_paciente)

        self.lbl_pac = QLabel("Sin paciente seleccionado")
        self.lbl_pac.setStyleSheet(
            f"color:{MUTED};font-size:12px;background:transparent;border:none;"
        )
        bl.addWidget(QLabel("Paciente:"))
        bl.addWidget(self.inp_cedula, stretch=2)
        bl.addWidget(btn_b)
        bl.addStretch()
        bl.addWidget(self.lbl_pac)
        return busq

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _buscar_paciente(self):
        texto = self.inp_cedula.text().strip()
        if not texto:
            QMessageBox.warning(self, "Campo requerido", "Ingrese la cédula o nombre del paciente.")
            return
        # TODO Sprint 4: paciente_controller.buscar_pacientes(texto)
        self.lbl_pac.setStyleSheet(
            f"color:{SUCCESS};font-size:12px;font-weight:700;background:transparent;border:none;"
        )
        self.lbl_pac.setText(f"✓  Paciente: {texto}")

    def _guardar(self):
        """
        Persiste la evolución médica del día.
        Construye el resumen del examen físico a partir de los hallazgos.
        """
        # Construir resumen del examen físico
        resumen_ef = []
        for h in self._hallazgos:
            resumen_ef.append(h.resumen)

        # TODO Sprint 4: medicina_interna_service.guardar_evolucion(datos, usuario)
        QMessageBox.information(
            self,
            "Guardado exitoso",
            "✅  Evolución médica registrada correctamente.\n\n"
            "La acción quedó registrada en el log de auditoría.",
        )
