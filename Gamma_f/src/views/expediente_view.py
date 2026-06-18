"""
Proyecto GAMMA - Vista del Médico: Evaluación Clínica + Expediente + Citas
Limpio y directo. ISO 27799 / Ley 81.
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QFrame, QGridLayout, QMessageBox, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateTimeEdit,
    QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QDateTime
from src.controllers.paciente_controller import paciente_controller
from src.controllers.cita_controller import cita_controller
from src.models.models import CitaStatus
from src.views._theme import NAVY, TEAL, SUCCESS, DANGER, BG, WHITE, BORDER, TEXT, MUTED
from src.views._widgets import BannerWidget
from src.views._styles import btn_primary, btn_teal, btn_buscar, btn_secondary, btn_danger
from src.views._common import (
    INPUT_QSS, WIDGET_BG, TABLA_QSS, SCROLL_QSS,
    setup_calendar_popup,
    card_style, titulo_style, sec_style, campo_style, setup_calendar_popup
)

TAB_QSS = f"""
    QTabWidget::pane {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 0px 10px 10px 10px;
    }}
    QTabBar::tab {{
        background-color: #EDF2F7;
        color: {MUTED};
        border: 1px solid {BORDER};
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {WHITE};
        color: {NAVY};
        border-top: 3px solid {TEAL};
        font-weight: 700;
    }}
    QTabBar::tab:hover {{
        background-color: #E2E8F0;
        color: {NAVY};
    }}
"""


class ExpedienteView(QWidget):
    def __init__(self):
        super().__init__()
        self._pac = None
        self._visita_sel = None
        self.setStyleSheet(WIDGET_BG)
        self._setup_ui()

    def _lbl(self, t): l = QLabel(t.upper()); l.setStyleSheet(campo_style()); return l
    def _sec(self, t): l = QLabel(t.upper()); l.setStyleSheet(sec_style()); return l
    def _ta(self, ph, h=70): t = QTextEdit(); t.setPlaceholderText(ph); t.setFixedHeight(h); t.setStyleSheet(INPUT_QSS); return t
    def _card(self): f = QFrame(); f.setStyleSheet(card_style()); return f

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(12)

        # ── Encabezado ────────────────────────────────────────────────────────
        enc = QHBoxLayout()
        t = QLabel("Evaluación Clínica"); t.setStyleSheet(titulo_style())
        enc.addWidget(t); enc.addStretch()
        layout.addLayout(enc)

        # ── Banner ────────────────────────────────────────────────────────────
        layout.addWidget(BannerWidget("🩺", "Evaluación Clínica — Médico", "", "#276749", "#38A169"))

        # ── Búsqueda ─────────────────────────────────────────────────────────
        busq = QFrame()
        busq.setStyleSheet(f"QFrame{{background-color:{WHITE};border-radius:12px;border:1px solid {BORDER};}}")
        bl = QHBoxLayout(busq); bl.setContentsMargins(16, 12, 16, 12); bl.setSpacing(10)
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("Buscar paciente por cédula o nombre...")
        self.inp_buscar.setStyleSheet(INPUT_QSS)
        self.inp_buscar.returnPressed.connect(self._buscar)
        btn_b = btn_buscar("Buscar"); btn_b.clicked.connect(self._buscar)
        bl.addWidget(self.inp_buscar); bl.addWidget(btn_b)
        layout.addWidget(busq)

        # ── Info paciente (visible solo al encontrar) ─────────────────────────
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

        # ── Splitter: panel izq (visitas) | tabs der ──────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Panel izquierdo: visitas del triage
        left = self._card()
        ll = QVBoxLayout(left); ll.setContentsMargins(16, 14, 16, 16); ll.setSpacing(10)
        ll.addWidget(self._sec("Visitas"))

        self.tabla_visitas = QTableWidget()
        self.tabla_visitas.setColumnCount(3)
        self.tabla_visitas.setHorizontalHeaderLabels(["ID", "Fecha", "Estado"])
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_visitas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_visitas.verticalHeader().setVisible(False)
        self.tabla_visitas.setShowGrid(False)
        self.tabla_visitas.setAlternatingRowColors(True)
        self.tabla_visitas.setStyleSheet(TABLA_QSS)
        self.tabla_visitas.itemSelectionChanged.connect(self._seleccionar_visita)
        ll.addWidget(self.tabla_visitas)

        ll.addWidget(self._sec("Datos del Triage"))
        self.txt_triage = QLabel("Seleccione una visita.")
        self.txt_triage.setWordWrap(True)
        self.txt_triage.setStyleSheet(
            f"color:{MUTED};font-size:12px;background:#F8FAFD;"
            f"border-radius:8px;padding:10px;border:1px solid {BORDER};"
        )
        ll.addWidget(self.txt_triage)
        splitter.addWidget(left)

        # Panel derecho: tabs
        right = QWidget(); right.setStyleSheet(f"background:{BG};")
        rl = QVBoxLayout(right); rl.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget(); tabs.setStyleSheet(TAB_QSS)

        # ── TAB 1: Evaluación Clínica ─────────────────────────────────────────
        tab_eval = QWidget(); tab_eval.setStyleSheet(f"background:{WHITE};")
        tel = QVBoxLayout(tab_eval); tel.setContentsMargins(20, 16, 20, 16); tel.setSpacing(14)

        gc = QGridLayout(); gc.setSpacing(12)
        gc.setColumnStretch(0, 1); gc.setColumnStretch(1, 1)
        self.inp_dia = self._ta("Diagnóstico preliminar...")
        self.inp_dia.textChanged.connect(lambda: (
            self.inp_dia.setProperty("error", "false"),
            self.inp_dia.style().unpolish(self.inp_dia),
            self.inp_dia.style().polish(self.inp_dia)
        ))
        self.inp_tra = self._ta("Plan de tratamiento...")
        self.inp_obs = self._ta("Observaciones clínicas...", 60)
        self.inp_nota_rapida = self._ta("Nota médica adicional...", 75)

        gc.addWidget(self._lbl("Diagnóstico Preliminar"), 0, 0); gc.addWidget(self.inp_dia, 1, 0)
        gc.addWidget(self._lbl("Plan de Tratamiento"),    0, 1); gc.addWidget(self.inp_tra, 1, 1)
        gc.addWidget(self._lbl("Observaciones"),          2, 0, 1, 2); gc.addWidget(self.inp_obs, 3, 0, 1, 2)
        tel.addLayout(gc)

        br_eval = QHBoxLayout(); br_eval.setSpacing(10); br_eval.addStretch()
        self.btn_nota = btn_teal("➕  Agregar Nota"); self.btn_nota.clicked.connect(self._agregar_nota)
        self.btn_eval = btn_primary("✔  Guardar Evaluación"); self.btn_eval.clicked.connect(self._guardar_evaluacion)
        br_eval.addWidget(self.btn_nota); br_eval.addWidget(self.btn_eval)
        tel.addLayout(br_eval)

        tel.addWidget(self._sec("Nota Durante Consulta"))
        tel.addWidget(self.inp_nota_rapida)
        tabs.addTab(tab_eval, "📋  Evaluación Clínica")

        # ── TAB 2: Expediente Completo ────────────────────────────────────────
        tab_exp = QWidget(); tab_exp.setStyleSheet(f"background:{WHITE};")
        texpl = QVBoxLayout(tab_exp); texpl.setContentsMargins(20, 16, 20, 16)
        self.txt_expediente = QTextEdit()
        self.txt_expediente.setReadOnly(True)
        self.txt_expediente.setStyleSheet(
            f"QTextEdit{{background:{WHITE};border:none;font-size:13px;color:{TEXT};}}"
        )
        self.txt_expediente.setPlaceholderText("Seleccione un paciente para ver su expediente.")
        texpl.addWidget(self.txt_expediente)
        tabs.addTab(tab_exp, "📂  Expediente Completo")

        # ── TAB 3: Citas Médicas ──────────────────────────────────────────────
        tab_citas = QWidget(); tab_citas.setStyleSheet(f"background:{WHITE};")
        tab_citas_outer = QVBoxLayout(tab_citas); tab_citas_outer.setContentsMargins(0, 0, 0, 0)

        scroll_citas = QScrollArea()
        scroll_citas.setWidgetResizable(True)
        scroll_citas.setFrameShape(QFrame.Shape.NoFrame)
        scroll_citas.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        tab_citas_outer.addWidget(scroll_citas)

        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background:{WHITE};")
        tcl = QVBoxLayout(scroll_content); tcl.setContentsMargins(20, 16, 20, 16); tcl.setSpacing(14)
        scroll_citas.setWidget(scroll_content)

        form_cita = QFrame()
        form_cita.setStyleSheet(f"QFrame{{background:#F8FAFD;border-radius:12px;border:1px solid {BORDER};}}")
        fcl = QVBoxLayout(form_cita); fcl.setContentsMargins(18, 16, 18, 16); fcl.setSpacing(12)
        fcl.addWidget(self._sec("Programar Nueva Cita"))

        gc2 = QGridLayout(); gc2.setSpacing(12)
        gc2.setColumnStretch(0, 1); gc2.setColumnStretch(1, 1)
        self.inp_fecha_cita = QDateTimeEdit()
        self.inp_fecha_cita.setDisplayFormat("dd/MM/yyyy  HH:mm")
        self.inp_fecha_cita.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.inp_fecha_cita.setCalendarPopup(True)
        self.inp_fecha_cita.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.inp_fecha_cita)
        setup_calendar_popup(self.inp_fecha_cita)
        self.inp_area_cita   = QLineEdit(); self.inp_area_cita.setPlaceholderText("Ej. Medicina General"); self.inp_area_cita.setStyleSheet(INPUT_QSS)
        self.inp_motivo_cita = self._ta("Motivo de la cita...", 42)
        self.inp_notas_cita  = self._ta("Notas adicionales...", 42)

        gc2.addWidget(self._lbl("Fecha y Hora *"),     0, 0); gc2.addWidget(self.inp_fecha_cita,  1, 0)
        gc2.addWidget(self._lbl("Área"),               0, 1); gc2.addWidget(self.inp_area_cita,   1, 1)
        gc2.addWidget(self._lbl("Motivo"),             2, 0, 1, 2); gc2.addWidget(self.inp_motivo_cita, 3, 0, 1, 2)
        gc2.addWidget(self._lbl("Notas"),              4, 0, 1, 2); gc2.addWidget(self.inp_notas_cita,  5, 0, 1, 2)
        fcl.addLayout(gc2)

        br_cita = QHBoxLayout(); br_cita.addStretch()
        self.btn_cita = btn_primary("📅  Programar Cita"); self.btn_cita.clicked.connect(self._programar_cita)
        br_cita.addWidget(self.btn_cita); fcl.addLayout(br_cita)
        tcl.addWidget(form_cita)

        tcl.addWidget(self._sec("Citas del Paciente"))
        self.tabla_citas = QTableWidget(); self.tabla_citas.setColumnCount(5)
        self.tabla_citas.setHorizontalHeaderLabels(["ID", "Fecha y Hora", "Área", "Motivo", "Estado"])
        self.tabla_citas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_citas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_citas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_citas.verticalHeader().setVisible(False)
        self.tabla_citas.setShowGrid(False)
        self.tabla_citas.setAlternatingRowColors(True)
        self.tabla_citas.setStyleSheet(TABLA_QSS)
        self.tabla_citas.setMinimumHeight(160)
        tcl.addWidget(self.tabla_citas)

        acc = QHBoxLayout(); acc.setSpacing(10)
        btn_conf = btn_teal("✅  Confirmar");  btn_conf.clicked.connect(lambda: self._cambiar_estado_cita(CitaStatus.CONFIRMADA))
        btn_comp = btn_secondary("✔  Completar"); btn_comp.clicked.connect(lambda: self._cambiar_estado_cita(CitaStatus.COMPLETADA))
        btn_canc = btn_danger("✖  Cancelar");  btn_canc.clicked.connect(lambda: self._cambiar_estado_cita(CitaStatus.CANCELADA))
        acc.addWidget(btn_conf); acc.addWidget(btn_comp); acc.addWidget(btn_canc); acc.addStretch()
        tcl.addLayout(acc)
        tabs.addTab(tab_citas, "📅  Citas Médicas")

        rl.addWidget(tabs)
        splitter.addWidget(right)
        splitter.setSizes([340, 680])

        layout.addWidget(splitter, stretch=1)

    # ── Búsqueda ──────────────────────────────────────────────────────────────

    def _buscar(self):
        t = self.inp_buscar.text().strip()
        if not t: return
        res = paciente_controller.buscar_pacientes(t)
        if res:
            self._pac = res[0]
            self.lbl_info.setText(
                f"👤  {self._pac.nombre_completo}  |  "
                f"Edad: {self._pac.edad} años  |  "
                f"Cédula: {self._pac.cedula}  |  "
                f"Tipo Sangre: {self._pac.tipo_sangre.value if self._pac.tipo_sangre else '—'}"
            )
            self.info_pac.setVisible(True)
            self._cargar_visitas()
            self._cargar_expediente()
            self._cargar_citas()
        else:
            self._pac = None
            self.info_pac.setVisible(False)
            self.tabla_visitas.setRowCount(0)
            QMessageBox.warning(self, "No encontrado", "Paciente no encontrado.")

    # ── Visitas ───────────────────────────────────────────────────────────────

    def _cargar_visitas(self):
        if not self._pac: return
        self.tabla_visitas.setRowCount(0)
        self.tabla_visitas.setRowCount(len(self._pac.visitas))
        for i, v in enumerate(self._pac.visitas):
            self.tabla_visitas.setItem(i, 0, QTableWidgetItem(str(v.id)))
            self.tabla_visitas.setItem(i, 1, QTableWidgetItem(v.fecha_ingreso.strftime("%d/%m/%Y %H:%M")))
            self.tabla_visitas.setItem(i, 2, QTableWidgetItem(v.estado.value if hasattr(v.estado, "value") else str(v.estado)))
            self.tabla_visitas.item(i, 0).setData(Qt.ItemDataRole.UserRole, v)

    def _seleccionar_visita(self):
        if not self.tabla_visitas.selectedItems(): return
        v = self.tabla_visitas.item(self.tabla_visitas.currentRow(), 0).data(Qt.ItemDataRole.UserRole)
        if not v: return
        self._visita_sel = v
        info = (
            f"<b>Visita #{v.id}</b> — {v.fecha_ingreso.strftime('%d/%m/%Y %H:%M')}<br/>"
            f"<b>Presión:</b> {v.presion_arterial or '—'}  "
            f"<b>Temp:</b> {v.temperatura or '—'}°C  "
            f"<b>Sat O₂:</b> {v.saturacion_oxigeno or '—'}%  "
            f"<b>FC:</b> {v.frecuencia_cardiaca or '—'} bpm<br/>"
            f"<b>Peso:</b> {v.peso_kg or '—'} kg  <b>Talla:</b> {v.talla_cm or '—'} cm<br/>"
            f"<b>Obs:</b> {(v.observaciones or '—')[:180]}"
        )
        self.txt_triage.setText(info)
        self.txt_triage.setTextFormat(Qt.TextFormat.RichText)
        self.txt_triage.setStyleSheet(
            f"color:{TEXT};font-size:12px;background:#F8FAFD;"
            f"border-radius:8px;padding:10px;border:1px solid {BORDER};"
        )
        if v.diagnostico_preliminar: self.inp_dia.setPlainText(v.diagnostico_preliminar)
        if v.plan_tratamiento:       self.inp_tra.setPlainText(v.plan_tratamiento)
        if v.observaciones:          self.inp_obs.setPlainText(v.observaciones)

    # ── Expediente ────────────────────────────────────────────────────────────

    def _cargar_expediente(self):
        if not self._pac: return
        p = self._pac
        ts  = p.tipo_sangre.value if p.tipo_sangre else "No especificado"
        gen = p.genero.value if p.genero else "—"
        vh  = ""
        for v in p.visitas:
            color = SUCCESS if "ACTIVA" in str(v.estado) else MUTED
            vh += f"""
            <div style='background:#F7FAFC;border-left:3px solid {NAVY};
                        padding:10px 14px;margin-bottom:8px;border-radius:6px;'>
                <b style='color:{NAVY};'>Visita #{v.id}</b>
                <span style='color:{color};font-size:11px;margin-left:10px;font-weight:600;'>
                {v.estado.value if hasattr(v.estado,'value') else v.estado}</span><br/>
                <span style='color:{MUTED};font-size:11px;'>
                {v.fecha_ingreso.strftime('%d/%m/%Y %H:%M')}</span><br/>
                <b>Motivo:</b> {v.motivo_consulta[:150]}<br/>
                {'<b>Diagnóstico:</b> ' + v.diagnostico_preliminar if v.diagnostico_preliminar else ''}
                {'<br/><b>Tratamiento:</b> ' + v.plan_tratamiento if v.plan_tratamiento else ''}
            </div>"""
        self.txt_expediente.setHtml(f"""
        <html><body style='font-family:Segoe UI,Arial;color:{TEXT};font-size:13px;padding:4px;'>
            <h2 style='color:{NAVY};border-bottom:2px solid {TEAL};padding-bottom:8px;margin-bottom:12px;'>
                {p.nombre_completo}</h2>
            <div style='background:#F7FAFC;border-radius:8px;padding:14px;margin-bottom:12px;'>
                <table width='100%' cellspacing='0' cellpadding='5'>
                    <tr>
                        <td><b>Cédula:</b> {p.cedula}</td>
                        <td><b>Edad:</b> {p.edad} años</td>
                        <td><b>Género:</b> {gen}</td>
                        <td><b>Tipo Sangre:</b> <span style='background:#E6F4FF;color:{NAVY};
                            padding:1px 8px;border-radius:4px;font-weight:700;'>{ts}</span></td>
                    </tr>
                    <tr>
                        <td><b>Nacimiento:</b> {p.fecha_nacimiento.strftime('%d/%m/%Y')}</td>
                        <td><b>Teléfono:</b> {p.telefono or '—'}</td>
                        <td colspan='2'><b>Dirección:</b> {p.direccion or '—'}</td>
                    </tr>
                </table>
            </div>
            <div style='background:#FFF8F0;border-left:3px solid #F6AD55;
                        padding:8px 12px;border-radius:4px;margin-bottom:8px;'>
                <b>Alergias:</b> {p.alergias or 'Ninguna registrada'}</div>
            <p style='margin:4px 0;'><b>Enf. crónicas:</b> {p.enfermedades_cronicas or 'Ninguna'}</p>
            <p style='margin:4px 0 12px;'><b>Medicamentos:</b> {p.medicamentos_actuales or 'Ninguno'}</p>
            <h3 style='color:{NAVY};font-size:12px;font-weight:700;letter-spacing:1px;
                border-bottom:1px solid {BORDER};padding-bottom:6px;margin-bottom:8px;'>
                📋 HISTORIAL DE VISITAS ({len(p.visitas)})</h3>
            {vh or f"<p style='color:{MUTED};'>Sin visitas registradas.</p>"}
        </body></html>""")

    # ── Evaluación ────────────────────────────────────────────────────────────

    def _guardar_evaluacion(self):
        if not self._visita_sel:
            QMessageBox.warning(self, "Atención", "Seleccione una visita del panel izquierdo."); return
        diag = self.inp_dia.toPlainText().strip()
        if not diag:
            self.inp_dia.setProperty("error", "true")
            self.inp_dia.style().unpolish(self.inp_dia)
            self.inp_dia.style().polish(self.inp_dia)
            QMessageBox.warning(self, "Atención", "El diagnóstico es obligatorio."); return
        
        self.inp_dia.setProperty("error", "false")
        self.inp_dia.style().unpolish(self.inp_dia)
        self.inp_dia.style().polish(self.inp_dia)

        tra = self.inp_tra.toPlainText().strip()
        obs = self.inp_obs.toPlainText().strip()

        self.btn_eval.setEnabled(False)
        ok, msg = paciente_controller.guardar_evaluacion_clinica(self._visita_sel.id, diag, tra, obs)
        self.btn_eval.setEnabled(True)

        if ok:
            QMessageBox.information(self, "✅ Guardado", msg)
            self.inp_dia.clear()
            self.inp_tra.clear()
            self.inp_obs.clear()
            self._buscar()
        else:
            QMessageBox.warning(self, "⚠ Error", msg)

    def _agregar_nota(self):
        if not self._visita_sel:
            QMessageBox.warning(self, "Atención", "Seleccione una visita primero."); return
        cont = self.inp_nota_rapida.toPlainText().strip()
        if not cont:
            QMessageBox.warning(self, "Atención", "Escriba el contenido de la nota."); return
        ok, msg = paciente_controller.agregar_nota(self._visita_sel.id, cont)
        if ok:
            QMessageBox.information(self, "✅ Nota Guardada", msg)
            self.inp_nota_rapida.clear()
        else:
            QMessageBox.warning(self, "⚠ Error", msg)

    # ── Citas ─────────────────────────────────────────────────────────────────

    def _programar_cita(self):
        if not self._pac:
            QMessageBox.warning(self, "Atención", "Primero busque un paciente."); return
        fecha = self.inp_fecha_cita.dateTime().toPyDateTime()
        if fecha <= datetime.now():
            QMessageBox.warning(self, "Fecha inválida", "La fecha debe ser futura."); return
        datos = {
            "fecha_cita":        fecha,
            "area_especialidad": self.inp_area_cita.text().strip(),
            "motivo":            self.inp_motivo_cita.toPlainText().strip(),
            "notas":             self.inp_notas_cita.toPlainText().strip(),
            "visita_id":         self._visita_sel.id if self._visita_sel else None,
        }
        ok, msg, _ = cita_controller.crear_cita(self._pac.id, datos)
        if ok:
            QMessageBox.information(self, "✅ Cita Programada", msg)
            self.inp_motivo_cita.clear(); self.inp_notas_cita.clear(); self.inp_area_cita.clear()
            self._cargar_citas()
        else:
            QMessageBox.warning(self, "⚠ Error", msg)

    def _cargar_citas(self):
        if not self._pac: return
        citas = cita_controller.obtener_citas_paciente(self._pac.id)
        self.tabla_citas.setRowCount(0); self.tabla_citas.setRowCount(len(citas))
        for i, c in enumerate(citas):
            estado_val = c.estado.value if hasattr(c.estado, "value") else str(c.estado)
            self.tabla_citas.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.tabla_citas.setItem(i, 1, QTableWidgetItem(c.fecha_cita.strftime("%d/%m/%Y  %H:%M")))
            self.tabla_citas.setItem(i, 2, QTableWidgetItem(c.area_especialidad or "General"))
            self.tabla_citas.setItem(i, 3, QTableWidgetItem((c.motivo or "—")[:60]))
            self.tabla_citas.setItem(i, 4, QTableWidgetItem(estado_val))
            self.tabla_citas.item(i, 0).setData(Qt.ItemDataRole.UserRole, c)

    def _cambiar_estado_cita(self, nuevo_estado: CitaStatus):
        fila = self.tabla_citas.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Atención", "Seleccione una cita."); return
        cita = self.tabla_citas.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        if not cita: return
        ok, msg = cita_controller.cambiar_estado(cita.id, nuevo_estado)
        if ok:
            QMessageBox.information(self, "✅ Actualizado", msg); self._cargar_citas()
        else:
            QMessageBox.warning(self, "⚠ Error", msg)
