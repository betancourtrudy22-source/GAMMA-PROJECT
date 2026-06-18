"""
Proyecto GAMMA - Vista de Recepción / Admisiones
Registro de datos de identificación del paciente.
ISO 27799 / Ley 81 - Mínimo privilegio.
"""
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QFrame, QScrollArea,
    QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QDate
from src.models.models import Gender
from src.controllers.paciente_controller import paciente_controller
from src.views._theme import NAVY, TEAL, BG, WHITE, BORDER, TEXT, MUTED, SUCCESS, DANGER
from src.views._widgets import BannerWidget
from src.views._styles import btn_primary, btn_secondary
from src.views._common import (
    INPUT_QSS, WIDGET_BG, SCROLL_QSS, CONT_BG,
    card_style, titulo_style, desc_style, sec_style, campo_style, setup_calendar_popup
)


class RecepcionView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(WIDGET_BG)
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _lbl(self, t): l = QLabel(t.upper()); l.setStyleSheet(campo_style()); return l
    def _inp(self, ph): i = QLineEdit(); i.setPlaceholderText(ph); i.setStyleSheet(INPUT_QSS); return i
    def _cmb(self): c = QComboBox(); c.setStyleSheet(INPUT_QSS); return c

    def _setup_ui(self):
        from src.controllers.auth_controller import auth_controller
        usuario = auth_controller.current_user

        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet(SCROLL_QSS)
        outer.addWidget(scroll)

        cont = QWidget(); cont.setStyleSheet(CONT_BG)
        layout = QVBoxLayout(cont); layout.setContentsMargins(32, 28, 32, 28); layout.setSpacing(20)
        scroll.setWidget(cont)

        # ── Encabezado ────────────────────────────────────────────────────────
        enc = QHBoxLayout(); col = QVBoxLayout(); col.setSpacing(2)
        t = QLabel("Panel de Recepción"); t.setStyleSheet(titulo_style())
        col.addWidget(t)
        enc.addLayout(col); enc.addStretch()
        self.lbl_hora = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.lbl_hora.setStyleSheet(
            f"font-size:22px;font-weight:800;color:{NAVY};background:transparent;border:none;"
        )
        enc.addWidget(self.lbl_hora)
        layout.addLayout(enc)

        # ── Banner ────────────────────────────────────────────────────────────
        nombre = usuario.nombre_completo.split()[0]
        layout.addWidget(BannerWidget(
            "🏥", "Recepción y Admisiones",
            "",
            NAVY, "#1A4F8A"
        ))

        # ── Formulario de registro ────────────────────────────────────────────
        card = QFrame(); card.setStyleSheet(card_style())
        cl = QVBoxLayout(card); cl.setContentsMargins(28, 22, 28, 24); cl.setSpacing(16)

        lbl_sec = QLabel("REGISTRO DE NUEVO PACIENTE")
        lbl_sec.setStyleSheet(
            f"font-size:11px;font-weight:700;color:{MUTED};letter-spacing:1px;"
            f"padding-bottom:8px;border-bottom:2px solid {TEAL};background:transparent;"
        )
        cl.addWidget(lbl_sec)

        g = QGridLayout(); g.setSpacing(14)
        g.setColumnStretch(0, 1); g.setColumnStretch(1, 1); g.setColumnStretch(2, 1)

        self.inp_ced = self._inp("Ej. 8-123-456")
        self.inp_nom = self._inp("Primer nombre")
        self.inp_ape = self._inp("Primer apellido")
        self.inp_fec = QDateEdit()
        self.inp_fec.setDisplayFormat("dd/MM/yyyy")
        self.inp_fec.setDate(QDate(1990, 1, 1))
        self.inp_fec.setCalendarPopup(True)
        self.inp_fec.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.inp_fec)
        self.cmb_gen = self._cmb()
        for gn in Gender: self.cmb_gen.addItem(gn.value, gn)
        self.inp_nac = self._inp("Nacionalidad")
        self.inp_tel = self._inp("6000-0000")
        self.inp_dir = self._inp("Dirección completa")
        self.inp_ce  = self._inp("Nombre del contacto")
        self.inp_te  = self._inp("Teléfono de emergencia")

        g.addWidget(self._lbl("Cédula / ID *"),       0, 0); g.addWidget(self.inp_ced, 1, 0)
        g.addWidget(self._lbl("Nombre *"),            0, 1); g.addWidget(self.inp_nom, 1, 1)
        g.addWidget(self._lbl("Apellido *"),          0, 2); g.addWidget(self.inp_ape, 1, 2)
        g.addWidget(self._lbl("Fecha Nac. *"),        2, 0); g.addWidget(self.inp_fec, 3, 0)
        g.addWidget(self._lbl("Género *"),            2, 1); g.addWidget(self.cmb_gen, 3, 1)
        g.addWidget(self._lbl("Nacionalidad"),        2, 2); g.addWidget(self.inp_nac, 3, 2)
        g.addWidget(self._lbl("Teléfono"),            4, 0); g.addWidget(self.inp_tel, 5, 0)
        g.addWidget(self._lbl("Dirección"),           4, 1); g.addWidget(self.inp_dir, 5, 1)
        g.addWidget(self._lbl("Contacto Emergencia"), 4, 2); g.addWidget(self.inp_ce,  5, 2)
        g.addWidget(self._lbl("Tel. Emergencia"),     6, 0); g.addWidget(self.inp_te,  7, 0)
        cl.addLayout(g)

        br = QHBoxLayout(); br.addStretch()
        btn_l = btn_secondary("Limpiar"); btn_l.clicked.connect(self._limpiar)
        self.btn_reg = btn_primary("✔  Registrar Paciente")
        self.btn_reg.clicked.connect(self._registrar)
        br.addWidget(btn_l); br.addSpacing(12); br.addWidget(self.btn_reg)
        cl.addLayout(br)

        layout.addWidget(card)
        layout.addStretch()

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _tick(self):
        self.lbl_hora.setText(datetime.now().strftime("%H:%M:%S"))

    def _registrar(self):
        fq = self.inp_fec.date()
        datos = {
            "cedula":              self.inp_ced.text(),
            "nombre":              self.inp_nom.text(),
            "apellido":            self.inp_ape.text(),
            "fecha_nacimiento":    date(fq.year(), fq.month(), fq.day()),
            "genero":              self.cmb_gen.currentData(),
            "nacionalidad":        self.inp_nac.text(),
            "telefono":            self.inp_tel.text(),
            "direccion":           self.inp_dir.text(),
            "contacto_emergencia": self.inp_ce.text(),
            "telefono_emergencia": self.inp_te.text(),
        }
        self.btn_reg.setEnabled(False)
        ok, msg, _ = paciente_controller.registrar_paciente(datos)
        self.btn_reg.setEnabled(True)
        if ok:
            QMessageBox.information(self, "✅ Registrado", msg)
            self._limpiar()
        else:
            QMessageBox.warning(self, "⚠ Error", msg)

    def _limpiar(self):
        for w in self.findChildren(QLineEdit): w.clear()
        self.cmb_gen.setCurrentIndex(0)
        self.inp_fec.setDate(QDate(1990, 1, 1))
        self.inp_ced.setFocus()
