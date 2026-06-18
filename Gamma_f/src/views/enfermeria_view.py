"""Proyecto GAMMA - Vista de Enfermería Asistencial"""
from PyQt6.QtWidgets import (
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QTextEdit,
    QFrame,QTableWidget,QTableWidgetItem,QHeaderView,QMessageBox,QSplitter
)
from PyQt6.QtCore import Qt
from src.controllers.paciente_controller import paciente_controller
from src.views._theme import NAVY,TEAL,SUCCESS,DANGER,BG,WHITE,BORDER,TEXT,MUTED,BLUE
from src.views._widgets import BannerWidget
from src.views._styles import btn_blue, btn_buscar
from src.views._common import TABLA_QSS,INPUT_QSS,WIDGET_BG,card_style,busq_style,titulo_style,desc_style,sec_style,campo_style

class EnfermeriaView(QWidget):
    def __init__(self):
        super().__init__(); self._pac=None
        self.setStyleSheet(WIDGET_BG); self._setup_ui()

    def _card(self): f=QFrame(); f.setStyleSheet(card_style()); return f

    def _setup_ui(self):
        layout=QVBoxLayout(self); layout.setContentsMargins(32,28,32,20); layout.setSpacing(18)

        enc=QHBoxLayout(); col=QVBoxLayout(); col.setSpacing(2)
        t=QLabel("Indicaciones y Notas de Enfermería"); t.setStyleSheet(titulo_style())
        col.addWidget(t); enc.addLayout(col); enc.addStretch()
        layout.addLayout(enc)

        layout.addWidget(BannerWidget("💉","Enfermería Asistencial",
                                      "",
                                      "#1E4A8A","#3182CE"))

        busq=QFrame(); busq.setStyleSheet(busq_style())
        bl=QHBoxLayout(busq); bl.setContentsMargins(16,12,16,12); bl.setSpacing(10)
        lbl_p=QLabel("Paciente:"); lbl_p.setStyleSheet(f"font-weight:700;color:{MUTED};background:transparent;border:none;")
        self.inp_buscar=QLineEdit(); self.inp_buscar.setPlaceholderText("Buscar por cédula o nombre..."); self.inp_buscar.setStyleSheet(INPUT_QSS)
        self.inp_buscar.returnPressed.connect(self._buscar)
        btn_b=btn_buscar("Buscar"); btn_b.clicked.connect(self._buscar)
        self.lbl_pac=QLabel("Ningún paciente seleccionado"); self.lbl_pac.setStyleSheet(f"color:{MUTED};font-size:12px;background:transparent;border:none;")
        bl.addWidget(lbl_p); bl.addWidget(self.inp_buscar); bl.addWidget(btn_b); bl.addSpacing(12); bl.addWidget(self.lbl_pac)
        layout.addWidget(busq)

        splitter=QSplitter(Qt.Orientation.Horizontal)
        left=self._card(); ll=QVBoxLayout(left); ll.setContentsMargins(16,14,16,16); ll.setSpacing(10)
        sec1=QLabel("INDICACIONES ACTIVAS"); sec1.setStyleSheet(sec_style()); ll.addWidget(sec1)
        self.tabla=QTableWidget(); self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID","Fecha","Área","Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False); self.tabla.setShowGrid(False)
        self.tabla.setAlternatingRowColors(True); self.tabla.setStyleSheet(TABLA_QSS)
        self.tabla.itemSelectionChanged.connect(self._detalle)
        ll.addWidget(self.tabla); splitter.addWidget(left)

        right=self._card(); rl=QVBoxLayout(right); rl.setContentsMargins(16,14,16,16); rl.setSpacing(12)
        sec2=QLabel("DETALLE DE INDICACIONES"); sec2.setStyleSheet(sec_style()); rl.addWidget(sec2)
        self.lbl_det=QLabel("Seleccione una visita para ver las indicaciones.")
        self.lbl_det.setWordWrap(True); self.lbl_det.setStyleSheet(f"color:{MUTED};font-size:13px;padding:4px;background:transparent;border:none;")
        rl.addWidget(self.lbl_det)
        sec3=QLabel("REGISTRAR NOTA DE ENFERMERÍA"); sec3.setStyleSheet(sec_style()); rl.addWidget(sec3)
        vr=QHBoxLayout()
        lv=QLabel("ID Visita:"); lv.setStyleSheet(f"font-size:11px;font-weight:700;color:{MUTED};background:transparent;border:none;")
        self.inp_vid=QLineEdit(); self.inp_vid.setPlaceholderText("ID"); self.inp_vid.setMaximumWidth(160); self.inp_vid.setStyleSheet(INPUT_QSS)
        vr.addWidget(lv); vr.addWidget(self.inp_vid); vr.addStretch()
        rl.addLayout(vr)
        self.inp_nota=QTextEdit()
        self.inp_nota.setPlaceholderText("Registre la nota:\n- Medicamento, dosis, vía, hora\n- Procedimientos\n- Evolución")
        self.inp_nota.setMinimumHeight(140); self.inp_nota.setStyleSheet(INPUT_QSS)
        rl.addWidget(self.inp_nota)
        br=QHBoxLayout(); br.addStretch()
        self.btn_nota=btn_blue("💾  Guardar Nota"); self.btn_nota.clicked.connect(self._guardar)
        br.addWidget(self.btn_nota); rl.addLayout(br)
        splitter.addWidget(right); splitter.setSizes([380,600])
        layout.addWidget(splitter)

    def _buscar(self):
        t=self.inp_buscar.text().strip()
        if not t: return
        res=paciente_controller.buscar_pacientes(t)
        if res:
            self._pac=res[0]
            self.lbl_pac.setText(f"✓  {self._pac.nombre_completo}  (ID: {self._pac.id})")
            self.lbl_pac.setStyleSheet(f"color:{SUCCESS};font-weight:bold;font-size:12px;background:transparent;border:none;")
            self._visitas()
        else:
            self._pac=None; self.lbl_pac.setText("Paciente no encontrado.")
            self.lbl_pac.setStyleSheet(f"color:{DANGER};font-size:12px;background:transparent;border:none;"); self.tabla.setRowCount(0)

    def _visitas(self):
        if not self._pac: return
        self.tabla.setRowCount(0); self.tabla.setRowCount(len(self._pac.visitas))
        for i,v in enumerate(self._pac.visitas):
            self.tabla.setItem(i,0,QTableWidgetItem(str(v.id)))
            self.tabla.setItem(i,1,QTableWidgetItem(v.fecha_ingreso.strftime("%d/%m/%Y")))
            self.tabla.setItem(i,2,QTableWidgetItem(v.area_especialidad or "General"))
            self.tabla.setItem(i,3,QTableWidgetItem(v.estado.value if hasattr(v.estado,"value") else str(v.estado)))
            self.tabla.item(i,0).setData(Qt.ItemDataRole.UserRole,v)

    def _detalle(self):
        if not self.tabla.selectedItems(): return
        v=self.tabla.item(self.tabla.currentRow(),0).data(Qt.ItemDataRole.UserRole)
        if not v: return
        self.inp_vid.setText(str(v.id))
        self.lbl_det.setText(f"<b>Visita #{v.id}</b> — {v.fecha_ingreso.strftime('%d/%m/%Y %H:%M')}<br/>"
                             f"<b>Motivo:</b> {v.motivo_consulta[:120]}<br/>"
                             f"<b>Plan:</b> {v.plan_tratamiento or 'Sin plan'}<br/>"
                             f"<b>Obs:</b> {v.observaciones or 'Sin observaciones'}")
        self.lbl_det.setTextFormat(Qt.TextFormat.RichText)

    def _guardar(self):
        vid=self.inp_vid.text().strip()
        if not vid.isdigit(): QMessageBox.warning(self,"Atención","ID de visita inválido."); return
        cont=self.inp_nota.toPlainText().strip()
        if not cont: QMessageBox.warning(self,"Atención","La nota no puede estar vacía."); return
        self.btn_nota.setEnabled(False)
        ok,msg=paciente_controller.agregar_nota(int(vid),cont)
        self.btn_nota.setEnabled(True)
        if ok: QMessageBox.information(self,"✅ Nota Guardada",msg); self.inp_nota.clear()
        else: QMessageBox.warning(self,"⚠ Error",msg)
