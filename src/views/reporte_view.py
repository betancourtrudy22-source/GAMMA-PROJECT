"""
Proyecto GAMMA - Vista M4: Generación de Reportes
Reportes estadísticos y gráficas usando matplotlib embebido en PyQt6.
Métrica: Sin errores estadísticos. Generación < 10s para 100 registros.
"""

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QSizePolicy,
    QScrollArea
)
from PyQt6.QtCore import Qt
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from src.controllers.reporte_controller import reporte_controller


ESTILOS = """
    QFrame#card {
        background: #FFFFFF; border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    QPushButton#btn_actualizar {
        background-color: #0D3B66; color: white; border: none;
        border-radius: 8px; font-size: 14px; font-weight: bold;
        padding: 10px 24px;
    }
    QPushButton#btn_actualizar:hover { background-color: #1565C0; }
"""


class TarjetaMetrica(QFrame):
    """Tarjeta visual para mostrar una métrica del sistema."""

    def __init__(self, titulo: str, valor: str, color: str = "#0D3B66") -> None:
        super().__init__()
        self.setObjectName("card")
        self.setFixedHeight(100)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_val = QLabel(valor)
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_val.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")

        lbl_tit = QLabel(titulo)
        lbl_tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tit.setStyleSheet("font-size: 12px; color: #718096; font-weight: 600;")

        layout.addWidget(lbl_val)
        layout.addWidget(lbl_tit)

        self.lbl_val = lbl_val

    def actualizar(self, valor: str) -> None:
        """Actualiza el valor mostrado en la tarjeta."""
        self.lbl_val.setText(valor)


class ReporteView(QWidget):
    """Vista M4: Dashboard de reportes estadísticos."""

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
        lbl_titulo = QLabel("M4 — Reportes y Estadísticas")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #0D3B66;")
        btn_actualizar = QPushButton("Actualizar Datos")
        btn_actualizar.setObjectName("btn_actualizar")
        btn_actualizar.clicked.connect(self._cargar_datos)
        enc_row.addWidget(lbl_titulo)
        enc_row.addStretch()
        enc_row.addWidget(btn_actualizar)
        layout.addLayout(enc_row)

        # Tarjetas de métricas
        grid_metricas = QGridLayout()
        grid_metricas.setSpacing(16)

        self.card_pacientes = TarjetaMetrica("Total Pacientes", "—", "#0D3B66")
        self.card_visitas = TarjetaMetrica("Total Visitas", "—", "#276749")
        self.card_activas = TarjetaMetrica("Visitas Activas", "—", "#D69E2E")
        self.card_mes = TarjetaMetrica("Mes Actual", datetime.now().strftime("%B"), "#553C9A")

        grid_metricas.addWidget(self.card_pacientes, 0, 0)
        grid_metricas.addWidget(self.card_visitas, 0, 1)
        grid_metricas.addWidget(self.card_activas, 0, 2)
        grid_metricas.addWidget(self.card_mes, 0, 3)
        layout.addLayout(grid_metricas)

        # Área de gráficas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        graf_widget = QWidget()
        graf_layout = QHBoxLayout(graf_widget)
        graf_layout.setSpacing(16)

        # Gráfica 1: Visitas por mes
        frame1 = QFrame()
        frame1.setObjectName("card")
        layout1 = QVBoxLayout(frame1)
        lbl1 = QLabel("Visitas por Mes (Año Actual)")
        lbl1.setStyleSheet("font-weight: bold; color: #0D3B66; padding: 8px;")
        layout1.addWidget(lbl1)

        if MATPLOTLIB_AVAILABLE:
            self.fig_visitas = Figure(figsize=(6, 4), dpi=90)
            self.canvas_visitas = FigureCanvas(self.fig_visitas)
            self.canvas_visitas.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            layout1.addWidget(self.canvas_visitas)
        else:
            layout1.addWidget(QLabel("matplotlib no disponible"))

        # Gráfica 2: Distribución por género
        frame2 = QFrame()
        frame2.setObjectName("card")
        layout2 = QVBoxLayout(frame2)
        lbl2 = QLabel("Distribución por Género")
        lbl2.setStyleSheet("font-weight: bold; color: #0D3B66; padding: 8px;")
        layout2.addWidget(lbl2)

        if MATPLOTLIB_AVAILABLE:
            self.fig_genero = Figure(figsize=(4, 4), dpi=90)
            self.canvas_genero = FigureCanvas(self.fig_genero)
            layout2.addWidget(self.canvas_genero)
        else:
            layout2.addWidget(QLabel("matplotlib no disponible"))

        graf_layout.addWidget(frame1, stretch=2)
        graf_layout.addWidget(frame2, stretch=1)

        scroll.setWidget(graf_widget)
        layout.addWidget(scroll)

        # Cargar datos al iniciar
        self._cargar_datos()

    def _cargar_datos(self) -> None:
        """Carga y muestra los datos estadísticos."""
        stats = reporte_controller.obtener_estadisticas_generales()
        if stats:
            self.card_pacientes.actualizar(str(stats["total_pacientes"]))
            self.card_visitas.actualizar(str(stats["total_visitas"]))
            self.card_activas.actualizar(str(stats["visitas_activas"]))

        if MATPLOTLIB_AVAILABLE:
            self._graficar_visitas_mes()
            self._graficar_genero()

    def _graficar_visitas_mes(self) -> None:
        """Genera la gráfica de barras de visitas por mes."""
        datos = reporte_controller.obtener_visitas_por_mes()
        self.fig_visitas.clear()
        ax = self.fig_visitas.add_subplot(111)

        if datos:
            meses = [d["mes"] for d in datos]
            cantidades = [d["cantidad"] for d in datos]
            bars = ax.bar(meses, cantidades, color="#0D3B66", alpha=0.85)
            ax.bar_label(bars, fmt="%d", padding=3, fontsize=9)
        else:
            ax.text(
                0.5, 0.5, "Sin datos disponibles",
                ha="center", va="center", transform=ax.transAxes,
                color="#718096"
            )

        ax.set_facecolor("#F7FAFC")
        self.fig_visitas.patch.set_facecolor("#FFFFFF")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="both", labelsize=9)
        ax.set_ylabel("Visitas", fontsize=10)
        self.fig_visitas.tight_layout()
        self.canvas_visitas.draw()

    def _graficar_genero(self) -> None:
        """Genera el gráfico de pastel de distribución por género."""
        datos = reporte_controller.obtener_distribucion_genero()
        self.fig_genero.clear()
        ax = self.fig_genero.add_subplot(111)

        if datos:
            labels = list(datos.keys())
            values = list(datos.values())
            colores = ["#0D3B66", "#4ECDC4", "#F6AD55"][:len(labels)]
            ax.pie(
                values, labels=labels, autopct="%1.1f%%",
                colors=colores, startangle=90,
                textprops={"fontsize": 10}
            )
        else:
            ax.text(
                0.5, 0.5, "Sin datos",
                ha="center", va="center", transform=ax.transAxes,
                color="#718096"
            )

        self.fig_genero.patch.set_facecolor("#FFFFFF")
        self.fig_genero.tight_layout()
        self.canvas_genero.draw()
