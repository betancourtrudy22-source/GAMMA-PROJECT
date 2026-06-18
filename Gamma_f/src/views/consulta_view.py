"""
Proyecto GAMMA - Vista M3: Consulta de Expedientes
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QFrame, QTableWidget, QTableWidgetItem, QSplitter,
    QTextBrowser, QHeaderView, QStackedWidget
)
from PyQt6.QtCore import Qt
from src.controllers.paciente_controller import paciente_controller
from src.models.models import UserRole
from src.controllers.auth_controller import auth_controller
from src.views._theme import NAVY, TEAL, SUCCESS, DANGER, BG, WHITE, BORDER, TEXT, MUTED
from src.views._widgets import BannerWidget
from src.views._styles import btn_secondary, btn_buscar
from src.views._common import (
    TABLA_QSS, INPUT_QSS, WIDGET_BG,
    card_style, busq_style, titulo_style, sec_style
)


class ConsultaView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(WIDGET_BG)
        self._es_recepcion = (auth_controller.current_user.rol == UserRole.RECEPCION)
        self._setup_ui()

    def _setup_ui(self):
        # Layout principal SIN scroll — igual que recepción
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(10)

        # ── Encabezado ────────────────────────────────────────────────────────
        enc = QHBoxLayout()
        t = QLabel("Consulta de Expedientes"); t.setStyleSheet(titulo_style())
        enc.addWidget(t); enc.addStretch()
        layout.addLayout(enc)



        # ── Barra de búsqueda ─────────────────────────────────────────────────
        busq = QFrame(); busq.setStyleSheet(busq_style())
        bl = QHBoxLayout(busq); bl.setContentsMargins(16, 12, 16, 12); bl.setSpacing(10)
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("Buscar por cédula, nombre o apellido...")
        self.inp_buscar.setStyleSheet(INPUT_QSS)
        self.inp_buscar.returnPressed.connect(self._buscar)
        btn_b = btn_buscar("Buscar"); btn_b.clicked.connect(self._buscar)
        btn_t = btn_secondary("Ver Todos"); btn_t.clicked.connect(self._todos)
        bl.addWidget(self.inp_buscar); bl.addWidget(btn_b); bl.addWidget(btn_t)
        layout.addWidget(busq)

        # ── Splitter: tabla | detalle ─────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tabla
        self.tabla = QTableWidget()
        if self._es_recepcion:
            self.tabla.setColumnCount(5)
            self.tabla.setHorizontalHeaderLabels(
                ["ID", "Cédula", "Nombre Completo", "Teléfono", "Última Visita"]
            )
        else:
            self.tabla.setColumnCount(5)
            self.tabla.setHorizontalHeaderLabels(
                ["ID", "Cédula", "Nombre Completo", "Edad", "Visitas"]
            )
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setShowGrid(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet(TABLA_QSS)
        self.tabla.itemSelectionChanged.connect(self._detalle)
        splitter.addWidget(self.tabla)

        # Panel derecho
        der = QWidget(); der.setStyleSheet("background:transparent;")
        dl = QVBoxLayout(der); dl.setContentsMargins(0, 0, 0, 0); dl.setSpacing(8)

        lbl_sec = QLabel(
            "INFORMACIÓN DEL PACIENTE" if self._es_recepcion else "DETALLE DEL EXPEDIENTE"
        )
        lbl_sec.setStyleSheet(sec_style())
        dl.addWidget(lbl_sec)

        # Stack: 0 = placeholder, 1 = expediente
        self.stack_det = QStackedWidget()
        self.stack_det.setStyleSheet("background:transparent;")

        # Placeholder
        ph = QFrame()
        ph.setStyleSheet(f"QFrame{{background-color:{WHITE};border-radius:14px;border:1px solid {BORDER};}}")
        phl = QVBoxLayout(ph); phl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico = QLabel("🔍"); ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("font-size:40px;background:transparent;border:none;")
        lbl_ph = QLabel("Busque y seleccione\nun paciente para ver su información")
        lbl_ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ph.setWordWrap(True)
        lbl_ph.setStyleSheet(f"color:{MUTED};font-size:14px;background:transparent;border:none;")
        phl.addWidget(ico); phl.addSpacing(10); phl.addWidget(lbl_ph)
        self.stack_det.addWidget(ph)

        # Expediente
        self.txt_det = QTextBrowser()
        self.txt_det.setStyleSheet(
            f"QTextBrowser{{background-color:{WHITE};border:1px solid {BORDER};"
            f"border-radius:14px;padding:20px;font-size:13px;color:{TEXT};}}"
        )
        self.stack_det.addWidget(self.txt_det)
        self.stack_det.setCurrentIndex(0)

        dl.addWidget(self.stack_det)
        splitter.addWidget(der)
        splitter.setSizes([420, 600])

        # El splitter ocupa todo el espacio restante
        layout.addWidget(splitter, stretch=1)

    # ── Búsqueda ──────────────────────────────────────────────────────────────

    def _buscar(self):
        t = self.inp_buscar.text().strip()
        if t: self._poblar(paciente_controller.buscar_pacientes(t))

    def _todos(self):
        self._poblar(paciente_controller.obtener_todos_pacientes())

    def _poblar(self, pacientes):
        self.tabla.setRowCount(0)
        self.tabla.setRowCount(len(pacientes))
        self.stack_det.setCurrentIndex(0)

        for i, p in enumerate(pacientes):
            if self._es_recepcion:
                ultima = (p.visitas[-1].fecha_ingreso.strftime("%d/%m/%Y")
                          if p.visitas else "Sin visitas")
                self.tabla.setItem(i, 0, QTableWidgetItem(str(p.id)))
                self.tabla.setItem(i, 1, QTableWidgetItem(p.cedula))
                self.tabla.setItem(i, 2, QTableWidgetItem(p.nombre_completo))
                self.tabla.setItem(i, 3, QTableWidgetItem(p.telefono or "—"))
                self.tabla.setItem(i, 4, QTableWidgetItem(ultima))
            else:
                self.tabla.setItem(i, 0, QTableWidgetItem(str(p.id)))
                self.tabla.setItem(i, 1, QTableWidgetItem(p.cedula))
                self.tabla.setItem(i, 2, QTableWidgetItem(p.nombre_completo))
                self.tabla.setItem(i, 3, QTableWidgetItem(str(p.edad)))
                self.tabla.setItem(i, 4, QTableWidgetItem(str(len(p.visitas))))
            self.tabla.item(i, 0).setData(Qt.ItemDataRole.UserRole, p)

    def _detalle(self):
        if not self.tabla.selectedItems():
            self.stack_det.setCurrentIndex(0); return
        p = self.tabla.item(self.tabla.currentRow(), 0).data(Qt.ItemDataRole.UserRole)
        if not p:
            self.stack_det.setCurrentIndex(0); return
        html = self._html_recepcion(p) if self._es_recepcion else self._html_completo(p)
        self.txt_det.setHtml(html)
        self.stack_det.setCurrentIndex(1)

    def _html_recepcion(self, p) -> str:
        ultima = "Sin visitas registradas"
        proxima = "No registrada"
        if p.visitas:
            v = p.visitas[-1]
            ultima = f"{v.fecha_ingreso.strftime('%d/%m/%Y %H:%M')} — {v.motivo_consulta[:80]}"
        return f"""
        <html><body style='font-family:Segoe UI,Arial;color:{TEXT};font-size:13px;padding:4px;'>
            <h2 style='color:{NAVY};border-bottom:2px solid {TEAL};padding-bottom:8px;margin-bottom:14px;'>
                {p.nombre_completo}</h2>
            <div style='background:#F7FAFC;border-radius:8px;padding:14px;margin-bottom:14px;'>
                <table width='100%' cellspacing='0' cellpadding='6'>
                    <tr>
                        <td><b style='color:{MUTED};font-size:11px;'>CÉDULA</b><br/>
                            <span style='font-size:15px;font-weight:700;color:{NAVY};'>{p.cedula}</span></td>
                        <td><b style='color:{MUTED};font-size:11px;'>GÉNERO</b><br/>
                            {p.genero.value if p.genero else '—'}</td>
                        <td><b style='color:{MUTED};font-size:11px;'>NACIONALIDAD</b><br/>
                            {p.nacionalidad or '—'}</td>
                    </tr>
                </table>
            </div>
            <h3 style='color:{NAVY};font-size:12px;font-weight:700;letter-spacing:1px;
                border-bottom:1px solid {BORDER};padding-bottom:6px;margin-bottom:10px;'>📞 CONTACTOS</h3>
            <table width='100%' cellspacing='0' cellpadding='6'
                   style='background:#F7FAFC;border-radius:8px;margin-bottom:14px;'>
                <tr><td width='40%'><b>Teléfono:</b></td><td>{p.telefono or '—'}</td></tr>
                <tr><td><b>Dirección:</b></td><td>{p.direccion or '—'}</td></tr>
                <tr><td><b>Contacto emergencia:</b></td><td>{p.contacto_emergencia or '—'}</td></tr>
                <tr><td><b>Tel. emergencia:</b></td><td>{p.telefono_emergencia or '—'}</td></tr>
            </table>
            <h3 style='color:{NAVY};font-size:12px;font-weight:700;letter-spacing:1px;
                border-bottom:1px solid {BORDER};padding-bottom:6px;margin-bottom:10px;'>🏥 ÚLTIMA VISITA</h3>
            <div style='background:#F0FFF4;border-left:3px solid {SUCCESS};padding:10px 14px;border-radius:4px;margin-bottom:10px;'>
                {ultima}</div>
            <div style='background:#EBF8FF;border-left:3px solid {TEAL};padding:10px 14px;border-radius:4px;'>
                <b>Próxima cita:</b> {proxima}</div>
        </body></html>"""

    def _html_completo(self, p) -> str:
        ts  = p.tipo_sangre.value if p.tipo_sangre else "No especificado"
        gen = p.genero.value if p.genero else "—"
        vh  = ""
        for v in p.visitas[:5]:
            color = SUCCESS if "ACTIVA" in str(v.estado) else MUTED
            vh += f"""
            <div style='background:#F7FAFC;border-left:3px solid {NAVY};
                        padding:10px 14px;margin-bottom:8px;border-radius:6px;'>
                <b style='color:{NAVY};'>Visita #{v.id}</b>
                <span style='color:{color};font-size:11px;margin-left:10px;font-weight:600;'>
                    {v.estado.value if hasattr(v.estado,'value') else v.estado}</span><br/>
                <span style='color:{MUTED};font-size:11px;'>
                    {v.fecha_ingreso.strftime('%d/%m/%Y %H:%M')}</span><br/>
                <b>Motivo:</b> {v.motivo_consulta[:120]}
                {f"<br/><b>Diagnóstico:</b> {v.diagnostico_preliminar}" if v.diagnostico_preliminar else ""}
            </div>"""
        return f"""
        <html><body style='font-family:Segoe UI,Arial;color:{TEXT};font-size:13px;padding:4px;'>
            <h2 style='color:{NAVY};border-bottom:2px solid {TEAL};padding-bottom:8px;margin-bottom:12px;'>
                {p.nombre_completo}</h2>
            <div style='background:#F7FAFC;border-radius:8px;padding:14px;margin-bottom:12px;'>
                <table width='100%' cellspacing='0' cellpadding='5'>
                    <tr>
                        <td><b>Cédula:</b> {p.cedula}</td>
                        <td><b>Edad:</b> {p.edad} años</td>
                        <td><b>Género:</b> {gen}</td>
                        <td><b>Tipo Sangre:</b>
                            <span style='background:#E6F4FF;color:{NAVY};padding:1px 8px;
                                border-radius:4px;font-weight:700;'>{ts}</span></td>
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
        </body></html>"""
