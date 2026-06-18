"""
Proyecto GAMMA — Tema visual v4
QSS que funciona correctamente en PyQt6 Windows.
"""

NAVY       = "#0A2540"
NAVY_DARK  = "#061829"
NAVY_MID   = "#123059"
TEAL       = "#00B8A9"
TEAL_LIGHT = "#E0F7F5"
BG         = "#F0F4F9"
WHITE      = "#FFFFFF"
BORDER     = "#D1DCE8"
TEXT       = "#1A2B3C"
MUTED      = "#64748B"
LABEL      = "#7A92A8"
DANGER     = "#C53030"
SUCCESS    = "#276749"
AMBER      = "#B45309"
PURPLE     = "#553C9A"
BLUE       = "#2B6CB0"
LOGOUT_CLR = "#FC8181"

from src.models.models import UserRole

ROL_ETIQUETAS = {
    UserRole.ADMIN:            "Administrador",
    UserRole.MEDICO:           "Médico",
    UserRole.ENF_TRIAGE:       "Enfermero / Triage",
    UserRole.ENF_ASISTENCIAL:  "Enfermero / Asistencial",
    UserRole.DIRECTOR:         "Director Médico",
    UserRole.RECEPCION:        "Recepción / Admisiones",
    UserRole.MEDICINA_INTERNA: "Medicina Interna",
}

ROL_COLORES = {
    UserRole.ADMIN:            TEAL,
    UserRole.MEDICO:           TEAL,
    UserRole.ENF_TRIAGE:       "#48BB78",
    UserRole.ENF_ASISTENCIAL:  "#63B3ED",
    UserRole.DIRECTOR:         "#B794F4",
    UserRole.RECEPCION:        "#F6AD55",
    UserRole.MEDICINA_INTERNA: "#E8856A",   # Naranja clínico — identidad Medicina Interna
}

ROL_ICONOS = {
    UserRole.ADMIN:            "⚙️",
    UserRole.MEDICO:           "🩺",
    UserRole.ENF_TRIAGE:       "🚑",
    UserRole.ENF_ASISTENCIAL:  "💉",
    UserRole.DIRECTOR:         "📊",
    UserRole.RECEPCION:        "🏥",
    UserRole.MEDICINA_INTERNA: "🫀",        # Corazón anatómico — Medicina Interna
}

QSS_BASE = f"""
    QWidget {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
        color: {TEXT};
        background-color: {BG};
    }}
    QScrollArea {{
        background-color: transparent;
        border: none;
    }}
    QScrollBar:vertical {{
        background-color: {BG};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background-color: #CBD5E0;
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background-color: {BG};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: #CBD5E0;
        border-radius: 4px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ── Labels principales ── */
    QLabel {{
        color: {TEXT};
        background-color: transparent;
        border: none;
    }}
    QLabel#mod_titulo {{
        font-size: 24px;
        font-weight: 800;
        color: {NAVY};
        background-color: transparent;
    }}
    QLabel#mod_desc {{
        font-size: 12px;
        color: {MUTED};
        background-color: transparent;
    }}
    QLabel#sec_titulo {{
        font-size: 11px;
        font-weight: 700;
        color: {MUTED};
        letter-spacing: 1px;
        padding-bottom: 8px;
        border-bottom: 2px solid {TEAL};
        background-color: transparent;
    }}
    QLabel#lbl_campo {{
        color: {LABEL};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        background-color: transparent;
    }}

    /* ── Inputs ── */
    QLineEdit {{
        background-color: {WHITE};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: {TEXT};
        min-height: 36px;
        selection-background-color: {TEAL};
    }}
    QLineEdit:focus {{
        border-color: {NAVY};
        background-color: {WHITE};
        color: {TEXT};
    }}
    QLineEdit:hover {{
        border-color: #A8BDD4;
    }}
    QLineEdit[error="true"] {{
        border: 1.5px solid {DANGER};
        background-color: #FFF5F5;
    }}
    QLineEdit[valid="true"] {{
        border: 1.5px solid {SUCCESS};
        background-color: #F0FFF4;
    }}
    QComboBox[error="true"] {{
        border: 1.5px solid {DANGER};
        background-color: #FFF5F5;
    }}
    QDateEdit[error="true"] {{
        border: 1.5px solid {DANGER};
        background-color: #FFF5F5;
    }}
    QTextEdit {{
        background-color: {WHITE};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: {TEXT};
        selection-background-color: {TEAL};
    }}
    QTextEdit:focus {{
        border-color: {NAVY};
        color: {TEXT};
    }}
    QComboBox {{
        background-color: {WHITE};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: {TEXT};
        min-height: 36px;
    }}
    QComboBox:focus {{
        border-color: {NAVY};
        color: {TEXT};
    }}
    QComboBox:hover {{
        border-color: #A8BDD4;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        color: {TEXT};
        selection-background-color: {TEAL_LIGHT};
        selection-color: {NAVY};
        outline: none;
    }}
    QDateEdit {{
        background-color: {WHITE};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: {TEXT};
        min-height: 36px;
    }}
    QDateEdit:focus {{ border-color: {NAVY}; }}
    QDoubleSpinBox, QSpinBox {{
        background-color: {WHITE};
        border: 1.5px solid {BORDER};
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: {TEXT};
        min-height: 36px;
    }}
    QDoubleSpinBox:focus, QSpinBox:focus {{ border-color: {NAVY}; }}

    /* ── Tabla ── */
    QTableWidget {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 10px;
        gridline-color: transparent;
        selection-background-color: {TEAL_LIGHT};
        selection-color: {TEXT};
        alternate-background-color: #F8FAFD;
        color: {TEXT};
        outline: none;
    }}
    QTableWidget::item {{
        padding: 10px 14px;
        border-bottom: 1px solid #F0F4F8;
        color: {TEXT};
        background-color: transparent;
    }}
    QTableWidget::item:selected {{
        background-color: {TEAL_LIGHT};
        color: {NAVY};
    }}
    QHeaderView::section {{
        background-color: {NAVY};
        color: {WHITE};
        font-weight: 700;
        font-size: 12px;
        padding: 12px 14px;
        border: none;
    }}
    QHeaderView {{
        background-color: {NAVY};
    }}

    /* ── TextBrowser ── */
    QTextBrowser {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 16px;
        font-size: 13px;
        color: {TEXT};
    }}

    /* ── Splitter ── */
    QSplitter::handle {{
        background-color: {BORDER};
        width: 1px;
        height: 1px;
    }}

    /* ── Botones ── */
    QPushButton#btn_primary {{
        background-color: {NAVY};
        color: {WHITE};
        border: none;
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0 28px;
        min-height: 42px;
    }}
    QPushButton#btn_primary:hover {{ background-color: {NAVY_MID}; }}
    QPushButton#btn_primary:pressed {{ background-color: {NAVY_DARK}; }}
    QPushButton#btn_primary:disabled {{ background-color: #B0BEC5; color: #78909C; }}

    QPushButton#btn_teal {{
        background-color: {TEAL};
        color: {WHITE};
        border: none;
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0 24px;
        min-height: 42px;
    }}
    QPushButton#btn_teal:hover {{ background-color: #009E96; }}

    QPushButton#btn_secondary {{
        background-color: {WHITE};
        color: {MUTED};
        border: 1.5px solid {BORDER};
        border-radius: 9px;
        font-size: 13px;
        font-weight: 600;
        padding: 0 20px;
        min-height: 42px;
    }}
    QPushButton#btn_secondary:hover {{
        background-color: #EDF2F7;
        border-color: #A8BDD4;
        color: {TEXT};
    }}

    QPushButton#btn_buscar {{
        background-color: {NAVY};
        color: {WHITE};
        border: none;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        padding: 0 22px;
        min-height: 38px;
    }}
    QPushButton#btn_buscar:hover {{ background-color: {NAVY_MID}; }}

    QPushButton#btn_danger {{
        background-color: {DANGER};
        color: {WHITE};
        border: none;
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0 22px;
        min-height: 40px;
    }}
    QPushButton#btn_danger:hover {{ background-color: #9B2C2C; }}

    QPushButton#btn_triage {{
        background-color: {SUCCESS};
        color: {WHITE};
        border: none;
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0 28px;
        min-height: 42px;
    }}
    QPushButton#btn_triage:hover {{ background-color: #2F855A; }}
    QPushButton#btn_triage:disabled {{ background-color: #B0BEC5; color: #78909C; }}

    QPushButton#btn_enf {{
        background-color: {BLUE};
        color: {WHITE};
        border: none;
        border-radius: 9px;
        font-size: 13px;
        font-weight: 700;
        padding: 0 24px;
        min-height: 42px;
    }}
    QPushButton#btn_enf:hover {{ background-color: #3182CE; }}
    QPushButton#btn_enf:disabled {{ background-color: #B0BEC5; color: #78909C; }}

    /* ── MessageBox ── */
    QMessageBox {{
        background-color: {WHITE};
        color: {TEXT};
    }}
    QMessageBox QLabel {{
        color: {TEXT};
        background-color: transparent;
    }}

    /* ── QCalendarWidget ── */
    QCalendarWidget QWidget {{
        background-color: {WHITE};
        color: {TEXT};
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {NAVY};
        min-height: 38px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton {{
        color: {WHITE};
        background-color: transparent;
        font-size: 12px;
        font-weight: 700;
        min-height: 24px;
        min-width: 60px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton:hover {{
        background-color: rgba(255,255,255,0.15);
        border-radius: 4px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QSpinBox {{
        background-color: transparent;
        color: {WHITE};
        border: none;
        font-size: 12px;
        font-weight: 700;
        min-height: 24px;
        min-width: 70px;
        padding: 0px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QSpinBox::up-button,
    QCalendarWidget QWidget#qt_calendar_navigationbar QSpinBox::down-button {{
        width: 0px;
        height: 0px;
    }}
    QCalendarWidget QWidget#qt_calendar_yearbutton {{
        color: {WHITE};
        background-color: transparent;
    }}
"""
