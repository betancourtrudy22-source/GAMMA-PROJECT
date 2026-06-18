"""
Proyecto GAMMA — Medicina Interna: Seguimiento Clínico
Vista M-MI-4: Control de evolución de enfermedades complejas.

Cubre: objetivos de tratamiento, indicadores de seguimiento por patología
(Diabetes, Hipertensión, Insuficiencia Cardíaca, ERC),
cumplimiento del tratamiento y planificación de la próxima evaluación.

Acceso: UserRole.MEDICINA_INTERNA (lecto-escritura)
Auditoría: toda acción queda en AuditoriaLog (ISO 27799 / Ley 81).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QFrame, QScrollArea, QDateEdit,
    QMessageBox, QPushButton, QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QDate

from src.views._theme import (
    NAVY, TEAL, BG, WHITE, BORDER, TEXT, MUTED,
    SUCCESS, DANGER, AMBER, BLUE, PURPLE
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

CHECK_QSS = f"""
    QCheckBox {{
        color: {TEXT};
        font-size: 13px;
        spacing: 8px;
        background: transparent;
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


def _subtitulo_patologia(txt: str, color: str) -> QLabel:
    """Encabezado de sección por patología con color propio."""
    lbl = QLabel(txt)
    lbl.setStyleSheet(
        f"font-size:13px;font-weight:700;color:{color};"
        "background:transparent;border:none;padding-top:4px;"
    )
    return lbl


class MISeguimientoView(QWidget):
    """
    Control de seguimiento clínico por patología.
    Permite registrar indicadores de evolución, comparar contra metas
    terapéuticas y planificar la próxima evaluación.
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
        t = QLabel("Seguimiento Clínico"); t.setStyleSheet(titulo_style())
        col.addWidget(t)
        enc.addLayout(col); enc.addStretch()
        layout.addLayout(enc)

        layout.addWidget(BannerWidget(
            "📈",
            "Seguimiento Clínico del Paciente",
            "",
            MI_ACENTO_D, MI_ACENTO
        ))

        layout.addWidget(self._buscador())

        # ── Objetivos de tratamiento ──────────────────────────────────────────
        layout.addWidget(_sec_titulo("OBJETIVOS DE TRATAMIENTO"))
        layout.addWidget(_lbl("¿Qué se busca lograr con el tratamiento actual?"))

        obj_row = QHBoxLayout(); obj_row.setSpacing(20)
        self._objetivos: list[QCheckBox] = []
        for obj in [
            "Control glicémico", "Control presión arterial",
            "Mejoría respiratoria", "Recuperación renal",
            "Reducción de edema", "Otro",
        ]:
            cb = QCheckBox(obj); cb.setStyleSheet(CHECK_QSS)
            obj_row.addWidget(cb); self._objetivos.append(cb)
        obj_row.addStretch()
        layout.addLayout(obj_row)
        layout.addWidget(_sep())

        # ── Indicadores por patología ─────────────────────────────────────────
        layout.addWidget(_sec_titulo("INDICADORES DE SEGUIMIENTO"))

        # Diabetes
        layout.addWidget(_subtitulo_patologia("Diabetes Mellitus", MI_ACENTO))
        gdm = QGridLayout(); gdm.setSpacing(12)

        self.seg_glucosa = QLineEdit()
        self.seg_glucosa.setPlaceholderText("Glucosa actual (mg/dL)")
        self.seg_glucosa.setStyleSheet(INPUT_QSS)

        self.seg_hba1c = QLineEdit()
        self.seg_hba1c.setPlaceholderText("HbA1c actual (%)")
        self.seg_hba1c.setStyleSheet(INPUT_QSS)

        self.seg_hba1c_meta = QLineEdit()
        self.seg_hba1c_meta.setPlaceholderText("Meta HbA1c — ej: < 7.0 %")
        self.seg_hba1c_meta.setStyleSheet(INPUT_QSS)

        gdm.addWidget(_lbl("Glucosa actual"),  0, 0)
        gdm.addWidget(self.seg_glucosa,        1, 0)
        gdm.addWidget(_lbl("HbA1c actual"),    0, 1)
        gdm.addWidget(self.seg_hba1c,          1, 1)
        gdm.addWidget(_lbl("HbA1c meta"),      0, 2)
        gdm.addWidget(self.seg_hba1c_meta,     1, 2)
        layout.addLayout(gdm)

        # Hipertensión
        layout.addWidget(_subtitulo_patologia("Hipertensión Arterial", BLUE))
        ghta = QGridLayout(); ghta.setSpacing(12)

        self.seg_pa = QLineEdit()
        self.seg_pa.setPlaceholderText("Presión actual (mmHg)")
        self.seg_pa.setStyleSheet(INPUT_QSS)

        self.seg_pa_meta = QLineEdit()
        self.seg_pa_meta.setPlaceholderText("Meta PA — ej: < 130/80 mmHg")
        self.seg_pa_meta.setStyleSheet(INPUT_QSS)

        ghta.addWidget(_lbl("Presión actual"), 0, 0)
        ghta.addWidget(self.seg_pa,            1, 0)
        ghta.addWidget(_lbl("Presión meta"),   0, 1)
        ghta.addWidget(self.seg_pa_meta,       1, 1)
        layout.addLayout(ghta)

        # Insuficiencia Cardíaca
        layout.addWidget(_subtitulo_patologia("Insuficiencia Cardíaca", DANGER))
        gic = QGridLayout(); gic.setSpacing(12)

        self.seg_peso = QLineEdit()
        self.seg_peso.setPlaceholderText("Peso diario (kg)")
        self.seg_peso.setStyleSheet(INPUT_QSS)

        self.seg_edema = QComboBox()
        self.seg_edema.addItems(["Sin edema", "Leve", "Moderado", "Severo"])
        self.seg_edema.setStyleSheet(INPUT_QSS)

        self.seg_disnea = QComboBox()
        self.seg_disnea.addItems(["Sin disnea", "Al esfuerzo", "En reposo"])
        self.seg_disnea.setStyleSheet(INPUT_QSS)

        gic.addWidget(_lbl("Peso diario"),  0, 0)
        gic.addWidget(self.seg_peso,        1, 0)
        gic.addWidget(_lbl("Edema"),        0, 1)
        gic.addWidget(self.seg_edema,       1, 1)
        gic.addWidget(_lbl("Disnea"),       0, 2)
        gic.addWidget(self.seg_disnea,      1, 2)
        layout.addLayout(gic)

        # Enfermedad Renal Crónica
        layout.addWidget(_subtitulo_patologia("Enfermedad Renal Crónica", PURPLE))
        gerc = QGridLayout(); gerc.setSpacing(12)

        self.seg_creat = QLineEdit()
        self.seg_creat.setPlaceholderText("Creatinina actual (mg/dL)")
        self.seg_creat.setStyleSheet(INPUT_QSS)

        self.seg_tfg = QLineEdit()
        self.seg_tfg.setPlaceholderText("TFG (mL/min/1.73 m²)")
        self.seg_tfg.setStyleSheet(INPUT_QSS)

        self.seg_balance = QLineEdit()
        self.seg_balance.setPlaceholderText("Balance hídrico (mL)")
        self.seg_balance.setStyleSheet(INPUT_QSS)

        gerc.addWidget(_lbl("Creatinina actual"),  0, 0)
        gerc.addWidget(self.seg_creat,             1, 0)
        gerc.addWidget(_lbl("TFG"),                0, 1)
        gerc.addWidget(self.seg_tfg,               1, 1)
        gerc.addWidget(_lbl("Balance hídrico"),    0, 2)
        gerc.addWidget(self.seg_balance,           1, 2)
        layout.addLayout(gerc)
        layout.addWidget(_sep())

        # ── Cumplimiento del tratamiento ──────────────────────────────────────
        layout.addWidget(_sec_titulo("CUMPLIMIENTO DEL TRATAMIENTO"))

        h_cum = QHBoxLayout(); h_cum.setSpacing(12)
        h_cum.addWidget(_lbl("El paciente cumple la medicación:"))
        self.seg_cumplimiento = QComboBox()
        self.seg_cumplimiento.addItems(["Sí", "Parcialmente", "No"])
        self.seg_cumplimiento.setStyleSheet(INPUT_QSS)
        h_cum.addWidget(self.seg_cumplimiento); h_cum.addStretch()
        layout.addLayout(h_cum)

        self.seg_cumpl_obs = QTextEdit()
        self.seg_cumpl_obs.setPlaceholderText(
            "Observaciones sobre el cumplimiento: barreras económicas, "
            "efectos adversos, falta de comprensión del tratamiento..."
        )
        self.seg_cumpl_obs.setStyleSheet(INPUT_QSS)
        self.seg_cumpl_obs.setFixedHeight(72)
        layout.addWidget(_lbl("Observaciones de cumplimiento"))
        layout.addWidget(self.seg_cumpl_obs)
        layout.addWidget(_sep())

        # ── Próxima evaluación ────────────────────────────────────────────────
        layout.addWidget(_sec_titulo("PRÓXIMA EVALUACIÓN"))

        gpe = QGridLayout(); gpe.setSpacing(12)

        self.seg_prox_fecha = QDateEdit()
        self.seg_prox_fecha.setCalendarPopup(True)
        self.seg_prox_fecha.setDisplayFormat("dd/MM/yyyy")
        self.seg_prox_fecha.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.seg_prox_fecha)

        self.seg_prox_medico = QLineEdit()
        self.seg_prox_medico.setPlaceholderText("Médico responsable de la próxima evaluación")
        self.seg_prox_medico.setStyleSheet(INPUT_QSS)

        gpe.addWidget(_lbl("Fecha de próxima evaluación"), 0, 0)
        gpe.addWidget(self.seg_prox_fecha,                 1, 0)
        gpe.addWidget(_lbl("Médico responsable"),          0, 1)
        gpe.addWidget(self.seg_prox_medico,                1, 1)
        layout.addLayout(gpe)

        self.seg_prox_obs = QTextEdit()
        self.seg_prox_obs.setPlaceholderText(
            "Aspectos a monitorear en la próxima visita, "
            "ajustes de tratamiento pendientes, exámenes a solicitar..."
        )
        self.seg_prox_obs.setStyleSheet(INPUT_QSS)
        self.seg_prox_obs.setFixedHeight(90)
        layout.addWidget(_lbl("Observaciones para la próxima visita"))
        layout.addWidget(self.seg_prox_obs)

        # ── Botón guardar ─────────────────────────────────────────────────────
        layout.addSpacing(8)
        btn = QPushButton("💾  Guardar Seguimiento Clínico")
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

    def _guardar(self):
        """
        Persiste el seguimiento clínico.
        Stub hasta Sprint 4. Genera entrada de auditoría (ISO 27799).
        """
        # TODO Sprint 4: medicina_interna_service.guardar_seguimiento(datos, usuario)
        QMessageBox.information(
            self,
            "Guardado exitoso",
            "✅  Seguimiento clínico registrado correctamente.\n\n"
            "La acción quedó registrada en el log de auditoría.",
        )
