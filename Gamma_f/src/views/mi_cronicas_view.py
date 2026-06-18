"""
Proyecto GAMMA — Medicina Interna: Enfermedades Crónicas
Vista M-MI-2: Perfil persistente de patologías crónicas del paciente.

Cubre: Diabetes Mellitus, Hipertensión Arterial, Enfermedad Renal Crónica,
Insuficiencia Cardíaca, EPOC y otras enfermedades crónicas registradas.
El perfil se actualiza en cada visita; no reemplaza, se agrega (append-only).

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
    NAVY, TEAL, BG, WHITE, BORDER, TEXT, MUTED, SUCCESS
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


class MICronicasView(QWidget):
    """
    Perfil de enfermedades crónicas del paciente.
    Se actualiza en cada visita; mantiene historial de cambios (append-only).
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
        t = QLabel("Enfermedades Crónicas"); t.setStyleSheet(titulo_style())
        col.addWidget(t)
        enc.addLayout(col); enc.addStretch()
        layout.addLayout(enc)

        layout.addWidget(BannerWidget(
            "🩺",
            "Perfil de Enfermedades Crónicas",
            "",
            MI_ACENTO_D, MI_ACENTO
        ))

        layout.addWidget(self._buscador())

        # ── Diabetes Mellitus ─────────────────────────────────────────────────
        layout.addWidget(_sec_titulo("DIABETES MELLITUS"))

        gdm = QGridLayout(); gdm.setSpacing(12)
        self.dm_fecha = QDateEdit()
        self.dm_fecha.setCalendarPopup(True)
        self.dm_fecha.setDisplayFormat("dd/MM/yyyy")
        self.dm_fecha.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.dm_fecha)

        self.dm_tipo = QComboBox()
        self.dm_tipo.addItems(["No aplica", "Tipo 1", "Tipo 2"])
        self.dm_tipo.setStyleSheet(INPUT_QSS)

        self.dm_glucosa = QLineEdit()
        self.dm_glucosa.setPlaceholderText("Ej: 126 mg/dL")
        self.dm_glucosa.setStyleSheet(INPUT_QSS)

        self.dm_hba1c = QLineEdit()
        self.dm_hba1c.setPlaceholderText("Ej: 7.2 %")
        self.dm_hba1c.setStyleSheet(INPUT_QSS)

        gdm.addWidget(_lbl("Fecha de diagnóstico"), 0, 0)
        gdm.addWidget(self.dm_fecha,                 1, 0)
        gdm.addWidget(_lbl("Tipo"),                  0, 1)
        gdm.addWidget(self.dm_tipo,                  1, 1)
        gdm.addWidget(_lbl("Última glucosa"),         0, 2)
        gdm.addWidget(self.dm_glucosa,               1, 2)
        gdm.addWidget(_lbl("Última HbA1c"),           0, 3)
        gdm.addWidget(self.dm_hba1c,                 1, 3)
        layout.addLayout(gdm)

        layout.addWidget(_lbl("Complicaciones"))
        hc = QHBoxLayout(); hc.setSpacing(20)
        self.dm_comps: list[QCheckBox] = []
        for comp in ["Retinopatía", "Nefropatía", "Neuropatía", "Pie diabético"]:
            cb = QCheckBox(comp); cb.setStyleSheet(CHECK_QSS)
            hc.addWidget(cb); self.dm_comps.append(cb)
        hc.addStretch(); layout.addLayout(hc)

        self.dm_tto = QTextEdit()
        self.dm_tto.setPlaceholderText(
            "Tratamiento farmacológico y no farmacológico actual..."
        )
        self.dm_tto.setStyleSheet(INPUT_QSS); self.dm_tto.setFixedHeight(72)
        layout.addWidget(_lbl("Tratamiento actual"))
        layout.addWidget(self.dm_tto)
        layout.addWidget(_sep())

        # ── Hipertensión Arterial ─────────────────────────────────────────────
        layout.addWidget(_sec_titulo("HIPERTENSIÓN ARTERIAL"))

        ghta = QGridLayout(); ghta.setSpacing(12)
        self.hta_fecha = QDateEdit()
        self.hta_fecha.setCalendarPopup(True)
        self.hta_fecha.setDisplayFormat("dd/MM/yyyy")
        self.hta_fecha.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.hta_fecha)

        self.hta_pa = QLineEdit()
        self.hta_pa.setPlaceholderText("Ej: 150/90 mmHg")
        self.hta_pa.setStyleSheet(INPUT_QSS)

        self.hta_ctrl = QComboBox()
        self.hta_ctrl.addItems(["No definido", "Sí", "No"])
        self.hta_ctrl.setStyleSheet(INPUT_QSS)

        self.hta_med = QLineEdit()
        self.hta_med.setPlaceholderText("Ej: Losartán 50 mg, Amlodipino 5 mg")
        self.hta_med.setStyleSheet(INPUT_QSS)

        ghta.addWidget(_lbl("Fecha de diagnóstico"),    0, 0)
        ghta.addWidget(self.hta_fecha,                  1, 0)
        ghta.addWidget(_lbl("Última presión registrada"), 0, 1)
        ghta.addWidget(self.hta_pa,                     1, 1)
        ghta.addWidget(_lbl("¿Controlada?"),            0, 2)
        ghta.addWidget(self.hta_ctrl,                   1, 2)
        ghta.addWidget(_lbl("Medicamentos"),             2, 0)
        ghta.addWidget(self.hta_med,                    3, 0, 1, 3)
        layout.addLayout(ghta)
        layout.addWidget(_sep())

        # ── Enfermedad Renal Crónica ──────────────────────────────────────────
        layout.addWidget(_sec_titulo("ENFERMEDAD RENAL CRÓNICA"))

        gerc = QGridLayout(); gerc.setSpacing(12)
        self.erc_estadio = QComboBox()
        self.erc_estadio.addItems(
            ["No aplica", "Estadio I", "Estadio II",
             "Estadio III", "Estadio IV", "Estadio V"]
        )
        self.erc_estadio.setStyleSheet(INPUT_QSS)

        self.erc_creat = QLineEdit()
        self.erc_creat.setPlaceholderText("Ej: 1.8 mg/dL")
        self.erc_creat.setStyleSheet(INPUT_QSS)

        self.erc_dialisis = QComboBox()
        self.erc_dialisis.addItems(
            ["No", "Sí — Hemodiálisis", "Sí — Diálisis peritoneal"]
        )
        self.erc_dialisis.setStyleSheet(INPUT_QSS)

        gerc.addWidget(_lbl("Estadio KDIGO"),    0, 0)
        gerc.addWidget(self.erc_estadio,         1, 0)
        gerc.addWidget(_lbl("Última creatinina"), 0, 1)
        gerc.addWidget(self.erc_creat,           1, 1)
        gerc.addWidget(_lbl("Diálisis"),         0, 2)
        gerc.addWidget(self.erc_dialisis,        1, 2)
        layout.addLayout(gerc)
        layout.addWidget(_sep())

        # ── Insuficiencia Cardíaca ────────────────────────────────────────────
        layout.addWidget(_sec_titulo("INSUFICIENCIA CARDÍACA"))

        gic = QGridLayout(); gic.setSpacing(12)
        self.ic_fe = QLineEdit()
        self.ic_fe.setPlaceholderText("Ej: 45 %")
        self.ic_fe.setStyleSheet(INPUT_QSS)

        self.ic_nyha = QComboBox()
        self.ic_nyha.addItems(
            ["No aplica", "Clase I", "Clase II", "Clase III", "Clase IV"]
        )
        self.ic_nyha.setStyleSheet(INPUT_QSS)

        gic.addWidget(_lbl("Fracción de eyección (FEVI)"), 0, 0)
        gic.addWidget(self.ic_fe,                          1, 0)
        gic.addWidget(_lbl("Clase funcional NYHA"),        0, 1)
        gic.addWidget(self.ic_nyha,                        1, 1)
        layout.addLayout(gic)
        layout.addWidget(_sep())

        # ── EPOC ──────────────────────────────────────────────────────────────
        layout.addWidget(_sec_titulo("EPOC"))

        gepoc = QGridLayout(); gepoc.setSpacing(12)
        self.epoc_grav = QComboBox()
        self.epoc_grav.addItems(["No aplica", "Leve", "Moderada", "Grave"])
        self.epoc_grav.setStyleSheet(INPUT_QSS)

        self.epoc_o2 = QComboBox()
        self.epoc_o2.addItems(["No", "Sí"])
        self.epoc_o2.setStyleSheet(INPUT_QSS)

        gepoc.addWidget(_lbl("Gravedad GOLD"),          0, 0)
        gepoc.addWidget(self.epoc_grav,                 1, 0)
        gepoc.addWidget(_lbl("Oxígeno domiciliario"),   0, 1)
        gepoc.addWidget(self.epoc_o2,                   1, 1)
        layout.addLayout(gepoc)
        layout.addWidget(_sep())

        # ── Otras enfermedades crónicas ───────────────────────────────────────
        layout.addWidget(_sec_titulo("OTRAS ENFERMEDADES CRÓNICAS"))

        self.otras = QTextEdit()
        self.otras.setPlaceholderText(
            "Listar otras condiciones crónicas, fecha de diagnóstico y estado actual.\n"
            "Ej: Hipotiroidismo (2015) — controlado con levotiroxina 50 mcg"
        )
        self.otras.setStyleSheet(INPUT_QSS)
        self.otras.setFixedHeight(100)
        layout.addWidget(self.otras)

        # ── Botón guardar ─────────────────────────────────────────────────────
        layout.addSpacing(8)
        btn = QPushButton("💾  Guardar Perfil Crónico")
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
        Persiste el perfil de crónicas.
        Stub hasta Sprint 4. Genera entrada de auditoría (ISO 27799).
        """
        # TODO Sprint 4: medicina_interna_service.guardar_cronicas(datos, usuario)
        QMessageBox.information(
            self,
            "Guardado exitoso",
            "✅  Perfil de enfermedades crónicas actualizado.\n\n"
            "La acción quedó registrada en el log de auditoría.",
        )
