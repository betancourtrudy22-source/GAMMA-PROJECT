"""
Proyecto GAMMA — Variables QSS comunes reutilizables
Importar en cada vista para consistencia visual.
"""
from src.views._styles import (
    NAVY, TEAL, BG, WHITE, BORDER, TEXT, MUTED, DANGER, SUCCESS,
    BTN_PRIMARY, BTN_SECONDARY, BTN_BUSCAR, BTN_DANGER, BTN_SUCCESS, BTN_BLUE
)

WIDGET_BG  = f"QWidget{{background-color:{BG};color:{TEXT};font-family:'Segoe UI',Arial;font-size:13px;}}"
SCROLL_QSS = "QScrollArea{background:transparent;border:none;}"
CONT_BG    = f"QWidget{{background-color:{BG};}}"
FRAME_BG   = f"QFrame{{background:transparent;border:none;}}"

TABLA_QSS = f"""
    QTableWidget{{background-color:{WHITE};border:1px solid {BORDER};
        border-radius:10px;color:{TEXT};gridline-color:transparent;
        selection-background-color:#E0F7F5;selection-color:{NAVY};
        alternate-background-color:#F8FAFD;outline:none;}}
    QTableWidget::item{{padding:10px 14px;color:{TEXT};
        border-bottom:1px solid #F0F4F8;background-color:transparent;}}
    QTableWidget::item:selected{{background-color:#E0F7F5;color:{NAVY};}}
    QHeaderView::section{{background-color:{NAVY};color:white;
        font-weight:700;font-size:12px;padding:12px 14px;border:none;}}
    QHeaderView{{background-color:{NAVY};}}
"""

INPUT_QSS = f"""
    QLineEdit,QTextEdit,QComboBox,QDateEdit,QDoubleSpinBox,QSpinBox{{
        background-color:{WHITE};border:1.5px solid {BORDER};
        border-radius:8px;padding:6px 12px;
        font-size:13px;color:{TEXT};min-height:36px;}}
    QLineEdit:focus,QTextEdit:focus,QComboBox:focus,
    QDateEdit:focus,QDoubleSpinBox:focus,QSpinBox:focus{{border-color:{NAVY};}}
    QLineEdit:hover,QComboBox:hover{{border-color:#A8BDD4;}}
    QLineEdit[error="true"],QComboBox[error="true"],QDateEdit[error="true"],QTextEdit[error="true"]{{
        border:1.5px solid {DANGER};background-color:#FFF5F5;}}
    QLineEdit[valid="true"],QComboBox[valid="true"],QDateEdit[valid="true"],QTextEdit[valid="true"]{{
        border:1.5px solid {SUCCESS};background-color:#F0FFF4;}}
    QTextEdit{{min-height:60px;}}
    QComboBox QAbstractItemView{{background-color:{WHITE};color:{TEXT};
        selection-background-color:#E0F7F5;selection-color:{NAVY};}}
    QDoubleSpinBox::up-button,QDoubleSpinBox::down-button,
    QSpinBox::up-button,QSpinBox::down-button{{width:20px;border:none;background:transparent;}}
    
    /* QCalendarWidget fixes */
    QCalendarWidget QWidget{{
        background-color:{WHITE};
        color:{TEXT};
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar{{
        background-color:{NAVY};
        min-height:38px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton{{
        color:{WHITE};
        background-color:transparent;
        font-size:12px;
        font-weight:700;
        min-height:24px;
        min-width:60px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton:hover{{
        background-color:rgba(255,255,255,0.15);
        border-radius:4px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QSpinBox{{
        background-color:transparent;
        color:{WHITE};
        border:none;
        font-size:13px;
        font-weight:700;
        min-height:24px;
        min-width:55px;
        padding:0px;
    }}
    QCalendarWidget QWidget#qt_calendar_navigationbar QSpinBox::up-button,
    QCalendarWidget QWidget#qt_calendar_navigationbar QSpinBox::down-button{{
        width:14px;
        height:10px;
        background-color:rgba(255,255,255,0.2);
        border-radius:3px;
    }}
    QCalendarWidget QWidget#qt_calendar_yearbutton{{
        color:{WHITE};
        background-color:transparent;
        font-size:13px;
        font-weight:700;
        min-width:55px;
    }}
    QCalendarWidget QAbstractItemView:enabled{{
        color:{TEXT};
        background-color:{WHITE};
        selection-background-color:#E0F7F5;
        selection-color:{NAVY};
    }}
"""

def card_style(): return f"QFrame{{background-color:{WHITE};border-radius:14px;border:1px solid {BORDER};}}"
def card_accent_style(): return f"QFrame{{background-color:{WHITE};border-radius:14px;border:1px solid {BORDER};border-top:3px solid {TEAL};}}"
def busq_style(): return f"QFrame{{background-color:{WHITE};border-radius:12px;border:1px solid {BORDER};}}"
def titulo_style(): return f"font-size:24px;font-weight:800;color:{NAVY};background:transparent;"
def desc_style(): return f"font-size:12px;color:{MUTED};background:transparent;"
def sec_style(): return f"font-size:11px;font-weight:700;color:{MUTED};letter-spacing:1px;padding-bottom:6px;border-bottom:2px solid {TEAL};background:transparent;"
def campo_style(): return f"color:#7A92A8;font-size:11px;font-weight:700;letter-spacing:0.5px;background:transparent;border:none;"
def lbl_style(): return f"color:{TEXT};background:transparent;border:none;"
def muted_style(): return f"color:{MUTED};background:transparent;border:none;"


def setup_calendar_popup(date_widget):
    """
    Configura el QCalendarWidget emergente de un QDateEdit / QDateTimeEdit
    para que muestre correctamente el mes Y el año en la barra de navegación.

    Llamar esta función DESPUÉS de setCalendarPopup(True).
    """
    from PyQt6.QtWidgets import QCalendarWidget as _QCal
    cal = date_widget.calendarWidget()
    if cal is None:
        return
    cal.setNavigationBarVisible(True)
    cal.setVerticalHeaderFormat(_QCal.VerticalHeaderFormat.NoVerticalHeader)
    cal.setHorizontalHeaderFormat(_QCal.HorizontalHeaderFormat.ShortDayNames)
    # Forzar el año visible mediante QSS adicional sobre el widget del calendario
    cal.setStyleSheet(
        f"""
        QCalendarWidget QWidget#qt_calendar_navigationbar {{
            background-color: {NAVY};
            min-height: 42px;
        }}
        QCalendarWidget QToolButton {{
            color: {WHITE};
            background-color: transparent;
            font-size: 13px;
            font-weight: 700;
            min-width: 60px;
            min-height: 28px;
            border-radius: 5px;
        }}
        QCalendarWidget QToolButton:hover {{
            background-color: rgba(255,255,255,0.18);
        }}
        QCalendarWidget QSpinBox {{
            color: {WHITE};
            background-color: transparent;
            border: none;
            font-size: 13px;
            font-weight: 700;
            min-width: 58px;
        }}
        QCalendarWidget QSpinBox::up-button,
        QCalendarWidget QSpinBox::down-button {{
            width: 14px;
            background-color: rgba(255,255,255,0.15);
            border-radius: 3px;
        }}
        QCalendarWidget QAbstractItemView:enabled {{
            color: {NAVY};
            background-color: white;
            selection-background-color: #E0F7F5;
            selection-color: {NAVY};
        }}
        """
    )
