"""
Proyecto GAMMA - Vista de Triage
Solo signos vitales. Limpio y directo.
ISO 27799 / Ley 81 - Mínimo privilegio.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QFrame, QScrollArea, QGridLayout, QMessageBox,
    QDoubleSpinBox, QSpinBox
)
from PyQt6.QtCore import Qt
from src.controllers.paciente_controller import paciente_controller
from src.views._theme import NAVY, TEAL, SUCCESS, DANGER, BG, WHITE, BORDER, TEXT, MUTED
from src.views._widgets import BannerWidget
from src.views._styles import btn_success, btn_buscar
from src.views._common import (
    INPUT_QSS, WIDGET_BG, SCROLL_QSS, CONT_BG,
    card_style, titulo_style, sec_style, campo_style
)


class TriageView(QWidget):
    def __init__(self):
        super().__init__()
        self._pac = None
        self.setStyleSheet(WIDGET_BG)
        self._setup_ui()

    def _lbl(self, t): l = QLabel(t.upper()); l.setStyleSheet(campo_style()); return l
    def _card(self): f = QFrame(); f.setStyleSheet(card_style()); return f

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(12)

        # ── Encabezado ────────────────────────────────────────────────────────
        enc = QHBoxLayout()
        t = QLabel("Triage — Signos Vitales"); t.setStyleSheet(titulo_style())
        enc.addWidget(t); enc.addStretch()
        layout.addLayout(enc)

        # ── Banner ────────────────────────────────────────────────────────────
        layout.addWidget(BannerWidget("🚑", "Triage — Signos Vitales", "", "#276749", "#48BB78"))

        # ── Búsqueda ─────────────────────────────────────────────────────────
        busq = QFrame()
        busq.setStyleSheet(
            f"QFrame{{background-color:{WHITE};border-radius:12px;border:1px solid {BORDER};}}"
        )
        bl = QHBoxLayout(busq); bl.setContentsMargins(16, 12, 16, 12); bl.setSpacing(10)
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("Buscar paciente por cédula o nombre...")
        self.inp_buscar.setStyleSheet(INPUT_QSS)
        self.inp_buscar.returnPressed.connect(self._buscar)
        btn_b = btn_buscar("Buscar"); btn_b.clicked.connect(self._buscar)
        bl.addWidget(self.inp_buscar); bl.addWidget(btn_b)
        layout.addWidget(busq)

        # ── Info paciente (solo visible al encontrar) ─────────────────────────
        self.info_pac = QFrame()
        self.info_pac.setStyleSheet(
            f"QFrame{{background-color:#F0FFF4;border-radius:10px;border:1px solid #9AE6B4;}}"
        )
        self.info_pac.setVisible(False)
        il = QHBoxLayout(self.info_pac); il.setContentsMargins(16, 10, 16, 10)
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet(
            f"color:{SUCCESS};font-size:13px;font-weight:600;background:transparent;border:none;"
        )
        il.addWidget(self.lbl_info)
        layout.addWidget(self.info_pac)

        # ── Signos Vitales ────────────────────────────────────────────────────
        sv = self._card()
        svl = QVBoxLayout(sv); svl.setContentsMargins(22, 18, 22, 20); svl.setSpacing(14)

        lbl_sec = QLabel("SIGNOS VITALES")
        lbl_sec.setStyleSheet(
            f"font-size:11px;font-weight:700;color:{MUTED};letter-spacing:1px;"
            f"padding-bottom:8px;border-bottom:2px solid {TEAL};background:transparent;"
        )
        svl.addWidget(lbl_sec)

        gv = QGridLayout(); gv.setSpacing(12)
        for i in range(4): gv.setColumnStretch(i, 1)

        self.inp_pre = QLineEdit(); self.inp_pre.setPlaceholderText("120/80 mmHg"); self.inp_pre.setStyleSheet(INPUT_QSS)
        self.inp_tmp = QDoubleSpinBox(); self.inp_tmp.setRange(30, 45); self.inp_tmp.setValue(36.5); self.inp_tmp.setSuffix(" °C"); self.inp_tmp.setStyleSheet(INPUT_QSS)
        self.inp_sat = QDoubleSpinBox(); self.inp_sat.setRange(50, 100); self.inp_sat.setValue(98); self.inp_sat.setSuffix(" %"); self.inp_sat.setStyleSheet(INPUT_QSS)
        self.inp_fc  = QSpinBox(); self.inp_fc.setRange(30, 250); self.inp_fc.setValue(72); self.inp_fc.setSuffix(" bpm"); self.inp_fc.setStyleSheet(INPUT_QSS)
        self.inp_fr  = QSpinBox(); self.inp_fr.setRange(5, 60); self.inp_fr.setValue(16); self.inp_fr.setSuffix(" rpm"); self.inp_fr.setStyleSheet(INPUT_QSS)
        self.inp_pes = QDoubleSpinBox(); self.inp_pes.setRange(1, 300); self.inp_pes.setValue(70); self.inp_pes.setSuffix(" kg"); self.inp_pes.setStyleSheet(INPUT_QSS)
        self.inp_tal = QDoubleSpinBox(); self.inp_tal.setRange(30, 250); self.inp_tal.setValue(170); self.inp_tal.setSuffix(" cm"); self.inp_tal.setStyleSheet(INPUT_QSS)
        self.inp_glu = QLineEdit(); self.inp_glu.setPlaceholderText("mg/dL (opcional)"); self.inp_glu.setStyleSheet(INPUT_QSS)

        gv.addWidget(self._lbl("Presión Arterial"),   0, 0); gv.addWidget(self.inp_pre, 1, 0)
        gv.addWidget(self._lbl("Temperatura"),        0, 1); gv.addWidget(self.inp_tmp, 1, 1)
        gv.addWidget(self._lbl("Saturación O₂"),      0, 2); gv.addWidget(self.inp_sat, 1, 2)
        gv.addWidget(self._lbl("Frec. Cardíaca"),     0, 3); gv.addWidget(self.inp_fc,  1, 3)
        gv.addWidget(self._lbl("Frec. Respiratoria"), 2, 0); gv.addWidget(self.inp_fr,  3, 0)
        gv.addWidget(self._lbl("Peso"),               2, 1); gv.addWidget(self.inp_pes, 3, 1)
        gv.addWidget(self._lbl("Talla"),              2, 2); gv.addWidget(self.inp_tal, 3, 2)
        gv.addWidget(self._lbl("Glucemia"),           2, 3); gv.addWidget(self.inp_glu, 3, 3)
        svl.addLayout(gv)

        br = QHBoxLayout(); br.addStretch()
        self.btn_g = btn_success("✔  Registrar Signos Vitales")
        self.btn_g.clicked.connect(self._guardar)
        br.addWidget(self.btn_g)
        svl.addLayout(br)

        layout.addWidget(sv)
        layout.addStretch()

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _buscar(self):
        t = self.inp_buscar.text().strip()
        if not t: return
        res = paciente_controller.buscar_pacientes(t)
        if res:
            self._pac = res[0]
            self.lbl_info.setText(
                f"👤  {self._pac.nombre_completo}  |  "
                f"Edad: {self._pac.edad} años  |  "
                f"Cédula: {self._pac.cedula}"
            )
            self.info_pac.setVisible(True)
        else:
            self._pac = None
            self.info_pac.setVisible(False)
            QMessageBox.warning(self, "No encontrado", "Paciente no encontrado.")

    def _guardar(self):
        if not self._pac:
            QMessageBox.warning(self, "Atención", "Primero busque el paciente.")
            return
        datos = {
            "motivo_consulta":     f"Triage - Registro de signos vitales. Paciente: {self._pac.nombre_completo}",
            "area_especialidad":   "",
            "presion_arterial":    self.inp_pre.text() or None,
            "temperatura":         self.inp_tmp.value(),
            "saturacion_oxigeno":  self.inp_sat.value(),
            "frecuencia_cardiaca": self.inp_fc.value(),
            "peso_kg":             self.inp_pes.value(),
            "talla_cm":            self.inp_tal.value(),
            "observaciones": (
                f"FR: {self.inp_fr.value()} rpm"
                + (f" | Glucemia: {self.inp_glu.text()} mg/dL" if self.inp_glu.text().strip() else "")
            ),
        }
        self.btn_g.setEnabled(False)
        ok, msg, v = paciente_controller.registrar_visita(self._pac.id, datos)
        self.btn_g.setEnabled(True)
        if ok:
            QMessageBox.information(self, "✅ Registrado", f"{msg}\nID visita: {v.id}")
            self._limpiar()
        else:
            QMessageBox.warning(self, "⚠ Error", msg)

    def _limpiar(self):
        self.inp_pre.clear(); self.inp_glu.clear()
        self.inp_tmp.setValue(36.5); self.inp_sat.setValue(98)
        self.inp_fc.setValue(72); self.inp_fr.setValue(16)
        self.inp_pes.setValue(70); self.inp_tal.setValue(170)
        self._pac = None; self.inp_buscar.clear()
        self.info_pac.setVisible(False)
