"""
Proyecto GAMMA — Estilos de botones y widgets
Funciones helper para aplicar estilos directamente a cada widget.
Soluciona el problema de herencia de QSS en PyQt6 Windows.
"""

from PyQt6.QtWidgets import QPushButton, QFrame, QLabel, QLineEdit, QTextEdit

# ── Colores ───────────────────────────────────────────────────────────────────
NAVY      = "#0A2540"
NAVY_MID  = "#123059"
NAVY_DARK = "#061829"
TEAL      = "#00B8A9"
BG        = "#F0F4F9"
WHITE     = "#FFFFFF"
BORDER    = "#D1DCE8"
TEXT      = "#1A2B3C"
MUTED     = "#64748B"
LABEL_C   = "#7A92A8"
DANGER    = "#C53030"
SUCCESS   = "#276749"
AMBER     = "#B45309"
PURPLE    = "#553C9A"
BLUE      = "#2B6CB0"

# ── Estilos de botón ──────────────────────────────────────────────────────────

BTN_PRIMARY = f"""
    QPushButton {{
        background-color: {NAVY};
        color: {WHITE};
        border: 2px solid {NAVY};
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0px 28px;
        min-height: 42px;
        min-width: 140px;
    }}
    QPushButton:hover {{
        background-color: {NAVY_MID};
        border-color: {NAVY_MID};
        color: {WHITE};
    }}
    QPushButton:pressed {{
        background-color: {NAVY_DARK};
        color: {WHITE};
    }}
    QPushButton:disabled {{
        background-color: #CBD5E0;
        border-color: #CBD5E0;
        color: #718096;
    }}
"""

BTN_SECONDARY = f"""
    QPushButton {{
        background-color: {WHITE};
        color: {NAVY};
        border: 1.5px solid {BORDER};
        border-radius: 9px;
        font-size: 13px;
        font-weight: 600;
        padding: 0px 20px;
        min-height: 42px;
        min-width: 100px;
    }}
    QPushButton:hover {{
        background-color: #EDF2F7;
        border-color: {NAVY};
        color: {NAVY};
    }}
    QPushButton:pressed {{
        background-color: #E2E8F0;
        color: {NAVY};
    }}
"""

BTN_TEAL = f"""
    QPushButton {{
        background-color: {TEAL};
        color: {WHITE};
        border: 2px solid {TEAL};
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0px 24px;
        min-height: 42px;
    }}
    QPushButton:hover {{
        background-color: #009E96;
        border-color: #009E96;
        color: {WHITE};
    }}
    QPushButton:disabled {{
        background-color: #CBD5E0;
        border-color: #CBD5E0;
        color: #718096;
    }}
"""

BTN_BUSCAR = f"""
    QPushButton {{
        background-color: {NAVY};
        color: {WHITE};
        border: 2px solid {NAVY};
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        padding: 0px 22px;
        min-height: 38px;
        min-width: 90px;
    }}
    QPushButton:hover {{
        background-color: {NAVY_MID};
        border-color: {NAVY_MID};
        color: {WHITE};
    }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background-color: {DANGER};
        color: {WHITE};
        border: 2px solid {DANGER};
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0px 22px;
        min-height: 40px;
        min-width: 100px;
    }}
    QPushButton:hover {{
        background-color: #9B2C2C;
        border-color: #9B2C2C;
        color: {WHITE};
    }}
    QPushButton:disabled {{
        background-color: #CBD5E0;
        border-color: #CBD5E0;
        color: #718096;
    }}
"""

BTN_SUCCESS = f"""
    QPushButton {{
        background-color: {SUCCESS};
        color: {WHITE};
        border: 2px solid {SUCCESS};
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0px 28px;
        min-height: 42px;
        min-width: 140px;
    }}
    QPushButton:hover {{
        background-color: #2F855A;
        border-color: #2F855A;
        color: {WHITE};
    }}
    QPushButton:disabled {{
        background-color: #CBD5E0;
        border-color: #CBD5E0;
        color: #718096;
    }}
"""

BTN_BLUE = f"""
    QPushButton {{
        background-color: {BLUE};
        color: {WHITE};
        border: 2px solid {BLUE};
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0px 24px;
        min-height: 42px;
        min-width: 120px;
    }}
    QPushButton:hover {{
        background-color: #3182CE;
        border-color: #3182CE;
        color: {WHITE};
    }}
    QPushButton:disabled {{
        background-color: #CBD5E0;
        border-color: #CBD5E0;
        color: #718096;
    }}
"""

# ── Estilos de card ───────────────────────────────────────────────────────────

CARD = f"""
    QFrame {{
        background-color: {WHITE};
        border-radius: 14px;
        border: 1px solid {BORDER};
    }}
"""

CARD_ACCENT = f"""
    QFrame {{
        background-color: {WHITE};
        border-radius: 14px;
        border: 1px solid {BORDER};
        border-top: 3px solid {TEAL};
    }}
"""

BUSQ_BAR = f"""
    QFrame {{
        background-color: {WHITE};
        border-radius: 12px;
        border: 1px solid {BORDER};
    }}
"""

# ── Funciones helper ──────────────────────────────────────────────────────────

def btn_primary(texto: str, cursor=True) -> QPushButton:
    """Crea un botón primario azul marino listo para usar."""
    from PyQt6.QtCore import Qt
    btn = QPushButton(texto)
    btn.setStyleSheet(BTN_PRIMARY)
    if cursor:
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def btn_secondary(texto: str, cursor=True) -> QPushButton:
    """Crea un botón secundario blanco con borde."""
    from PyQt6.QtCore import Qt
    btn = QPushButton(texto)
    btn.setStyleSheet(BTN_SECONDARY)
    if cursor:
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def btn_teal(texto: str, cursor=True) -> QPushButton:
    """Crea un botón verde teal."""
    from PyQt6.QtCore import Qt
    btn = QPushButton(texto)
    btn.setStyleSheet(BTN_TEAL)
    if cursor:
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def btn_buscar(texto: str = "🔍  Buscar", cursor=True) -> QPushButton:
    """Crea un botón de búsqueda."""
    from PyQt6.QtCore import Qt
    btn = QPushButton(texto)
    btn.setStyleSheet(BTN_BUSCAR)
    if cursor:
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def btn_danger(texto: str, cursor=True) -> QPushButton:
    """Crea un botón de peligro rojo."""
    from PyQt6.QtCore import Qt
    btn = QPushButton(texto)
    btn.setStyleSheet(BTN_DANGER)
    if cursor:
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def btn_success(texto: str, cursor=True) -> QPushButton:
    """Crea un botón verde de éxito."""
    from PyQt6.QtCore import Qt
    btn = QPushButton(texto)
    btn.setStyleSheet(BTN_SUCCESS)
    if cursor:
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def btn_blue(texto: str, cursor=True) -> QPushButton:
    """Crea un botón azul."""
    from PyQt6.QtCore import Qt
    btn = QPushButton(texto)
    btn.setStyleSheet(BTN_BLUE)
    if cursor:
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def card() -> QFrame:
    """Crea un QFrame con estilo de tarjeta blanca."""
    f = QFrame()
    f.setStyleSheet(CARD)
    return f

def card_accent() -> QFrame:
    """Crea un QFrame con borde superior teal."""
    f = QFrame()
    f.setStyleSheet(CARD_ACCENT)
    return f

def busq_bar() -> QFrame:
    """Crea un QFrame para barra de búsqueda."""
    f = QFrame()
    f.setStyleSheet(BUSQ_BAR)
    return f

def lbl_campo(texto: str) -> QLabel:
    """Crea un label de campo de formulario."""
    l = QLabel(texto.upper())
    l.setStyleSheet(f"color: {LABEL_C}; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; background: transparent; border: none;")
    return l

def lbl_sec(texto: str) -> QLabel:
    """Crea un label de sección."""
    l = QLabel(texto.upper())
    l.setStyleSheet(f"color: {MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1px; padding-bottom: 6px; border-bottom: 2px solid {TEAL}; background: transparent;")
    return l
