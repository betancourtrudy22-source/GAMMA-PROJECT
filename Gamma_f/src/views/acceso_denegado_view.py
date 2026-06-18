"""Proyecto GAMMA - Vista de Acceso Denegado"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from src.views._theme import NAVY,TEAL,DANGER,BG,WHITE,BORDER,MUTED
from src.views._common import WIDGET_BG

class AccesoDenegadoView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(WIDGET_BG)
        layout=QVBoxLayout(self); layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card=QFrame(); card.setFixedSize(480,280)
        card.setStyleSheet(f"QFrame{{background-color:{WHITE};border-radius:14px;border:1px solid {BORDER};}}")
        cl=QVBoxLayout(card); cl.setAlignment(Qt.AlignmentFlag.AlignCenter); cl.setSpacing(14); cl.setContentsMargins(40,32,40,32)
        ico=QLabel("🔒"); ico.setAlignment(Qt.AlignmentFlag.AlignCenter); ico.setStyleSheet("font-size:48px;background:transparent;border:none;")
        tit=QLabel("Acceso Denegado"); tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tit.setStyleSheet(f"font-size:22px;font-weight:800;color:{DANGER};background:transparent;border:none;")
        desc=QLabel("No tiene permisos para acceder a este módulo.\nContacte al administrador si cree que esto es un error.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter); desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size:13px;color:{MUTED};background:transparent;border:none;")
        norma=QLabel("ISO 27799 · Ley 81 · Mínimo Privilegio")
        norma.setAlignment(Qt.AlignmentFlag.AlignCenter)
        norma.setStyleSheet(f"font-size:11px;color:{TEAL};font-weight:700;letter-spacing:1px;background:transparent;border:none;")
        cl.addWidget(ico); cl.addWidget(tit); cl.addWidget(desc); cl.addWidget(norma)
        layout.addWidget(card)
