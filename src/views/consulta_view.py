"""
Proyecto GAMMA - Vista M3: Consulta de Expedientes
Acceso rápido y seguro a los expedientes de pacientes.
Métrica: Respuesta < 3s en tablet.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QSplitter, QTextBrowser, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from src.controllers.paciente_controller import paciente_controller


ESTILOS = """
    QLineEdit {
        background: #FFFFFF; border: 1.5px solid #E2E8F0;
        border-radius: 6px; padding: 6px 12px; font-size: 13px;
        color: #2D3748; min-height: 34px;
    }
    QLineEdit:focus { border-color: #0D3B66; }
    QPushButton#btn_buscar {
        background-color: #0D3B66; color: white; border: none;
        border-radius: 6px; font-size: 13px; padding: 8px 20px;
    }
    QPushButton#btn_buscar:hover { background-color: #1565C0; }
    QPushButton#btn_todos {
        background-color: #EDF2F7; color: #4A5568; border: none;
        border-radius: 6px; font-size: 13px; padding: 8px 16px;
    }
    QPushButton#btn_todos:hover { background-color: #E2E8F0; }
    QTableWidget {
        background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 8px; font-size: 13px; gridline-color: #EDF2F7;
        selection-background-color: #EBF4FF;
    }
    QTableWidget::item { padding: 8px; color: #2D3748; }
    QHeaderView::section {
        background-color: #0D3B66; color: white; font-weight: bold;
        font-size: 12px; padding: 8px; border: none;
    }
    QTextBrowser {
        background: #FFFFFF; border: 1px solid #E2E8F0;
        border-radius: 8px; font-size: 13px; color: #2D3748; padding: 16px;
    }
"""


class ConsultaView(QWidget):
    """Vista M3: Consulta y visualización de expedientes médicos."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self.setStyleSheet(ESTILOS)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)

        # Encabezado
        enc_row = QHBoxLayout()
        lbl_titulo = QLabel("M3 — Consulta de Expedientes")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #0D3B66;")
        enc_row.addWidget(lbl_titulo)
        enc_row.addStretch()
        layout.addLayout(enc_row)

        # Barra de búsqueda
        busq_frame = QFrame()
        busq_frame.setStyleSheet(
            "QFrame { background: #FFFFFF; border-radius: 10px; border: 1px solid #E2E8F0; }"
        )
        busq_layout = QHBoxLayout(busq_frame)
        busq_layout.setContentsMargins(16, 10, 16, 10)

        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("Buscar por cédula, nombre o apellido...")
        self.inp_buscar.returnPressed.connect(self._buscar)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setObjectName("btn_buscar")
        btn_buscar.clicked.connect(self._buscar)

        btn_todos = QPushButton("Ver Todos")
        btn_todos.setObjectName("btn_todos")
        btn_todos.clicked.connect(self._cargar_todos)

        busq_layout.addWidget(self.inp_buscar)
        busq_layout.addWidget(btn_buscar)
        busq_layout.addWidget(btn_todos)
        layout.addWidget(busq_frame)

        # Splitter: tabla + detalle
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tabla de resultados
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Cédula", "Nombre Completo", "Edad", "Visitas"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet(
            ESTILOS + "QTableWidget { alternate-background-color: #F7FAFC; }"
        )
        self.tabla.itemSelectionChanged.connect(self._mostrar_detalle)

        # Panel de detalle del expediente
        detalle_frame = QFrame()
        detalle_layout = QVBoxLayout(detalle_frame)
        detalle_layout.setContentsMargins(0, 0, 0, 0)

        lbl_detalle = QLabel("Detalle del Expediente")
        lbl_detalle.setStyleSheet(
            "font-weight: bold; color: #0D3B66; font-size: 14px; padding: 4px;"
        )
        detalle_layout.addWidget(lbl_detalle)

        self.txt_detalle = QTextBrowser()
        self.txt_detalle.setPlaceholderText(
            "Seleccione un paciente para ver su expediente completo."
        )
        detalle_layout.addWidget(self.txt_detalle)

        splitter.addWidget(self.tabla)
        splitter.addWidget(detalle_frame)
        splitter.setSizes([420, 600])

        layout.addWidget(splitter)

    def _buscar(self) -> None:
        termino = self.inp_buscar.text().strip()
        if not termino:
            return
        pacientes = paciente_controller.buscar_pacientes(termino)
        self._poblar_tabla(pacientes)

    def _cargar_todos(self) -> None:
        pacientes = paciente_controller.obtener_todos_pacientes()
        self._poblar_tabla(pacientes)

    def _poblar_tabla(self, pacientes: list) -> None:
        """Llena la tabla con la lista de pacientes."""
        self.tabla.setRowCount(0)
        self.tabla.setRowCount(len(pacientes))
        for fila, p in enumerate(pacientes):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(p.id)))
            self.tabla.setItem(fila, 1, QTableWidgetItem(p.cedula))
            self.tabla.setItem(fila, 2, QTableWidgetItem(p.nombre_completo))
            self.tabla.setItem(fila, 3, QTableWidgetItem(str(p.edad)))
            self.tabla.setItem(
                fila, 4, QTableWidgetItem(str(len(p.visitas)))
            )
            # Guardar el paciente en el item para recuperarlo
            self.tabla.item(fila, 0).setData(
                Qt.ItemDataRole.UserRole, p
            )

    def _mostrar_detalle(self) -> None:
        """Muestra el expediente completo del paciente seleccionado."""
        filas = self.tabla.selectedItems()
        if not filas:
            return

        fila = self.tabla.currentRow()
        paciente = self.tabla.item(fila, 0).data(Qt.ItemDataRole.UserRole)
        if paciente is None:
            return

        html = self._generar_html_expediente(paciente)
        self.txt_detalle.setHtml(html)

    def _generar_html_expediente(self, paciente) -> str:
        """Genera el HTML del expediente médico para visualización."""
        tipo_sangre = (
            paciente.tipo_sangre.value if paciente.tipo_sangre else "No especificado"
        )
        genero = paciente.genero.value if paciente.genero else "—"

        visitas_html = ""
        for v in paciente.visitas[:5]:  # Últimas 5 visitas
            estado_color = "#276749" if str(v.estado) == "VisitStatus.ACTIVA" else "#718096"
            visitas_html += f"""
            <div style='background:#F7FAFC; border-left:3px solid #0D3B66;
                        padding:10px; margin-bottom:8px; border-radius:4px;'>
                <b style='color:#0D3B66;'>Visita #{v.id}</b>
                <span style='color:{estado_color}; font-size:11px; margin-left:10px;'>
                    {v.estado.value if hasattr(v.estado, "value") else v.estado}
                </span><br/>
                <span style='color:#718096; font-size:11px;'>
                    {v.fecha_ingreso.strftime('%d/%m/%Y %H:%M')}
                </span><br/>
                <b>Motivo:</b> {v.motivo_consulta[:120]}<br/>
                {f"<b>Diagnóstico:</b> {v.diagnostico_final}" if v.diagnostico_final else ""}
            </div>"""

        return f"""
        <html><body style='font-family: Segoe UI, Arial; color: #2D3748; font-size: 13px;'>
            <h2 style='color:#0D3B66; border-bottom:2px solid #4ECDC4; padding-bottom:6px;'>
                {paciente.nombre_completo}
            </h2>
            <table width='100%' cellspacing='6'>
                <tr>
                    <td><b>Cédula:</b> {paciente.cedula}</td>
                    <td><b>Edad:</b> {paciente.edad} años</td>
                    <td><b>Género:</b> {genero}</td>
                </tr>
                <tr>
                    <td><b>Nacimiento:</b>
                        {paciente.fecha_nacimiento.strftime('%d/%m/%Y')}</td>
                    <td><b>Tipo Sangre:</b> {tipo_sangre}</td>
                    <td><b>Teléfono:</b> {paciente.telefono or '—'}</td>
                </tr>
            </table>
            <hr style='border:none; border-top:1px solid #E2E8F0; margin:10px 0;'/>
            <p><b>Alergias:</b> {paciente.alergias or 'Ninguna registrada'}</p>
            <p><b>Enfermedades Crónicas:</b>
                {paciente.enfermedades_cronicas or 'Ninguna registrada'}</p>
            <p><b>Medicamentos:</b>
                {paciente.medicamentos_actuales or 'Ninguno registrado'}</p>
            <hr style='border:none; border-top:1px solid #E2E8F0; margin:10px 0;'/>
            <h3 style='color:#0D3B66;'>Historial de Visitas ({len(paciente.visitas)})</h3>
            {visitas_html if visitas_html else
             "<p style='color:#718096;'>Sin visitas registradas.</p>"}
        </body></html>"""
