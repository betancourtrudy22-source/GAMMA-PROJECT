"""
Proyecto GAMMA — Widgets reutilizables v2
BannerWidget con paintEvent correcto para PyQt6 Windows.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush
from src.views._theme import *


class BannerWidget(QWidget):
    """
    Banner con gradiente real usando paintEvent.
    Funciona correctamente en PyQt6 Windows.
    """

    def __init__(self, icono: str, titulo: str, subtitulo: str,
                 color_inicio: str = NAVY, color_fin: str = NAVY_MID,
                 parent=None):
        super().__init__(parent)
        self._c1 = QColor(color_inicio)
        self._c2 = QColor(color_fin)
        self.setFixedHeight(100)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(28, 0, 28, 0)
        layout.setSpacing(18)

        # Icono
        lbl_ico = QLabel(icono)
        lbl_ico.setFixedSize(52, 52)
        lbl_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ico.setStyleSheet(
            "font-size: 36px; background: transparent; border: none;"
        )

        # Textos
        col = QVBoxLayout()
        col.setSpacing(6)
        col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet(
            "color: white; font-size: 17px; font-weight: 800; "
            "background: transparent; border: none; letter-spacing: -0.3px;"
        )

        lbl_s = QLabel(subtitulo)
        lbl_s.setStyleSheet(
            "color: rgba(255,255,255,0.65); font-size: 10px; "
            "font-weight: 700; letter-spacing: 1.5px; "
            "background: transparent; border: none;"
        )

        col.addWidget(lbl_t)
        col.addWidget(lbl_s)

        layout.addWidget(lbl_ico)
        layout.addLayout(col)
        layout.addStretch()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        grad = QLinearGradient(0, 0, rect.width(), 0)
        grad.setColorAt(0.0, self._c1)
        grad.setColorAt(1.0, self._c2)
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 14, 14)
        painter.end()


class KpiCard(QFrame):
    """Tarjeta KPI con borde superior de color."""

    def __init__(self, icono: str, valor: str, titulo: str,
                 color: str = NAVY, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(190, 110)
        self._aplicar_estilo()

        fl = QVBoxLayout(self)
        fl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.setSpacing(4)
        fl.setContentsMargins(12, 12, 12, 12)

        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.setSpacing(8)

        lbl_i = QLabel(icono)
        lbl_i.setStyleSheet(
            "font-size: 26px; background: transparent; border: none;"
        )

        self._lbl_v = QLabel(valor)
        self._aplicar_valor_estilo()

        row.addWidget(lbl_i)
        row.addWidget(self._lbl_v)

        lbl_t = QLabel(titulo.upper())
        lbl_t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_t.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {MUTED}; "
            "letter-spacing: 0.8px; background: transparent; border: none;"
        )

        fl.addLayout(row)
        fl.addWidget(lbl_t)

    def _aplicar_estilo(self):
        self.setStyleSheet(
            f"QFrame {{ background-color: {WHITE}; border-radius: 14px; "
            f"border: 1px solid {BORDER}; border-top: 3px solid {self._color}; }}"
        )

    def _aplicar_valor_estilo(self):
        self._lbl_v.setStyleSheet(
            f"font-size: 28px; font-weight: 800; color: {self._color}; "
            "background: transparent; border: none;"
        )

    def set_valor(self, valor: str):
        self._lbl_v.setText(valor)
        self._aplicar_valor_estilo()
