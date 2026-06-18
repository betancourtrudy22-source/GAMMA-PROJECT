"""Proyecto GAMMA - Vista M1: Registro de Pacientes"""
from datetime import date
from PyQt6.QtWidgets import (
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,
    QComboBox,QDateEdit,QTextEdit,QFrame,QScrollArea,QGridLayout,QMessageBox
)
from PyQt6.QtCore import QDate
from src.models.models import BloodType,Gender
from src.controllers.paciente_controller import paciente_controller
from src.views._theme import NAVY,TEAL,BG,WHITE,BORDER,TEXT,MUTED
from src.views._widgets import BannerWidget
from src.views._styles import btn_primary, btn_secondary
from src.views._common import INPUT_QSS,WIDGET_BG,SCROLL_QSS,CONT_BG,card_style,titulo_style,desc_style,sec_style,campo_style,setup_calendar_popup

class PacienteView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(WIDGET_BG); self._setup_ui()

    def _lbl(self,t): l=QLabel(t.upper()); l.setStyleSheet(campo_style()); return l
    def _sec(self,t): l=QLabel(t.upper()); l.setStyleSheet(sec_style()); return l
    def _ta(self,ph,h=70): t=QTextEdit(); t.setPlaceholderText(ph); t.setFixedHeight(h); t.setStyleSheet(INPUT_QSS); return t
    def _card(self): f=QFrame(); f.setStyleSheet(card_style()); return f
    def _inp(self,ph): i=QLineEdit(); i.setPlaceholderText(ph); i.setStyleSheet(INPUT_QSS); return i
    def _cmb(self): c=QComboBox(); c.setStyleSheet(INPUT_QSS); return c

    def _setup_ui(self):
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet(SCROLL_QSS)
        outer.addWidget(scroll)
        cont=QWidget(); cont.setStyleSheet(CONT_BG)
        layout=QVBoxLayout(cont); layout.setContentsMargins(32,28,32,28); layout.setSpacing(20)
        scroll.setWidget(cont)

        enc=QHBoxLayout(); col=QVBoxLayout(); col.setSpacing(2)
        t=QLabel("Registro de Pacientes"); t.setStyleSheet(titulo_style())
        col.addWidget(t); enc.addLayout(col); enc.addStretch()
        layout.addLayout(enc)

        layout.addWidget(BannerWidget("👤","Nuevo Registro de Paciente",
                                      "",
                                      NAVY,"#1A4F8A"))

        s1=self._card(); sl1=QVBoxLayout(s1); sl1.setContentsMargins(22,18,22,20); sl1.setSpacing(14)
        sl1.addWidget(self._sec("Datos de Identificación"))
        g1=QGridLayout(); g1.setSpacing(12)
        g1.setColumnStretch(0,1); g1.setColumnStretch(1,1); g1.setColumnStretch(2,1)
        self.inp_ced=self._inp("Ej. 8-123-456")
        self.inp_nom=self._inp("Primer nombre")
        self.inp_ape=self._inp("Primer apellido")
        self.inp_fec=QDateEdit(); self.inp_fec.setDisplayFormat("dd/MM/yyyy"); self.inp_fec.setDate(QDate(1990,1,1)); self.inp_fec.setCalendarPopup(True); self.inp_fec.setStyleSheet(INPUT_QSS)
        setup_calendar_popup(self.inp_fec)
        self.cmb_gen=self._cmb()
        for g in Gender: self.cmb_gen.addItem(g.value,g)
        self.inp_nac=self._inp("Nacionalidad")
        self.inp_tel=self._inp("6000-0000")
        self.inp_ce=self._inp("Nombre del contacto")
        self.inp_te=self._inp("6000-0001")
        self.inp_dir=self._ta("Dirección completa",65)
        g1.addWidget(self._lbl("Cédula / ID *"),0,0); g1.addWidget(self.inp_ced,1,0)
        g1.addWidget(self._lbl("Nombre *"),0,1); g1.addWidget(self.inp_nom,1,1)
        g1.addWidget(self._lbl("Apellido *"),0,2); g1.addWidget(self.inp_ape,1,2)
        g1.addWidget(self._lbl("Fecha Nac. *"),2,0); g1.addWidget(self.inp_fec,3,0)
        g1.addWidget(self._lbl("Género *"),2,1); g1.addWidget(self.cmb_gen,3,1)
        g1.addWidget(self._lbl("Nacionalidad"),2,2); g1.addWidget(self.inp_nac,3,2)
        g1.addWidget(self._lbl("Teléfono"),4,0); g1.addWidget(self.inp_tel,5,0)
        g1.addWidget(self._lbl("Contacto Emergencia"),4,1); g1.addWidget(self.inp_ce,5,1)
        g1.addWidget(self._lbl("Tel. Emergencia"),4,2); g1.addWidget(self.inp_te,5,2)
        g1.addWidget(self._lbl("Dirección"),6,0); g1.addWidget(self.inp_dir,7,0,1,3)
        sl1.addLayout(g1); layout.addWidget(s1)

        s2=self._card(); sl2=QVBoxLayout(s2); sl2.setContentsMargins(22,18,22,20); sl2.setSpacing(14)
        sl2.addWidget(self._sec("Datos Médicos Iniciales"))
        g2=QGridLayout(); g2.setSpacing(12); g2.setColumnStretch(0,1); g2.setColumnStretch(1,1)
        self.cmb_san=self._cmb(); self.cmb_san.addItem("— No especificado —",None)
        for bt in BloodType: self.cmb_san.addItem(bt.value,bt)
        self.inp_ale=self._ta("Liste alergias conocidas"); self.inp_ecr=self._ta("Enfermedades crónicas")
        self.inp_med=self._ta("Medicamentos actuales"); self.inp_ant=self._ta("Antecedentes familiares")
        self.inp_vac=self._ta("Vacunas aplicadas"); self.inp_cir=self._ta("Cirugías previas")
        g2.addWidget(self._lbl("Tipo de Sangre"),0,0); g2.addWidget(self.cmb_san,1,0)
        g2.addWidget(self._lbl("Alergias"),2,0); g2.addWidget(self.inp_ale,3,0)
        g2.addWidget(self._lbl("Enfermedades Crónicas"),2,1); g2.addWidget(self.inp_ecr,3,1)
        g2.addWidget(self._lbl("Medicamentos Actuales"),4,0); g2.addWidget(self.inp_med,5,0)
        g2.addWidget(self._lbl("Antecedentes Familiares"),4,1); g2.addWidget(self.inp_ant,5,1)
        g2.addWidget(self._lbl("Vacunas Aplicadas"),6,0); g2.addWidget(self.inp_vac,7,0)
        g2.addWidget(self._lbl("Cirugías Previas"),6,1); g2.addWidget(self.inp_cir,7,1)
        sl2.addLayout(g2); layout.addWidget(s2)

        # Conectar validaciones en tiempo real
        self.inp_ced.textChanged.connect(self._validar_cedula_realtime)
        self.inp_nom.textChanged.connect(lambda t: self._validar_y_marcar(self.inp_nom, len(t.strip()) > 0))
        self.inp_ape.textChanged.connect(lambda t: self._validar_y_marcar(self.inp_ape, len(t.strip()) > 0))
        self.inp_tel.textChanged.connect(self._validar_telefono_realtime)

        br=QHBoxLayout(); br.addStretch()
        btn_l=btn_secondary("Limpiar"); btn_l.clicked.connect(self._limpiar)
        self.btn_g=btn_primary("✔  Registrar Paciente"); self.btn_g.clicked.connect(self._guardar)
        br.addWidget(btn_l); br.addSpacing(10); br.addWidget(self.btn_g)
        layout.addLayout(br); layout.addSpacing(10)

    def _validar_cedula_realtime(self, texto):
        import re
        patron = re.compile(r'^(?:[1-9]|1[0-2]|PE|E|N|PI|SB|AV)-\d+-\d+$', re.IGNORECASE)
        es_valido = bool(patron.match(texto.strip()))
        self._validar_y_marcar(self.inp_ced, es_valido)

    def _validar_telefono_realtime(self, texto):
        import re
        t = texto.strip()
        if not t:
            self._reset_marcado(self.inp_tel)
            return
        patron = re.compile(r'^\+?\d{3,4}-?\d{4}$|^\d{7,8}$')
        es_valido = bool(patron.match(t))
        self._validar_y_marcar(self.inp_tel, es_valido)

    def _validar_y_marcar(self, widget, condicion: bool):
        widget.setProperty("error", "true" if not condicion else "false")
        widget.setProperty("valid", "true" if condicion else "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _reset_marcado(self, widget):
        widget.setProperty("error", "false")
        widget.setProperty("valid", "false")
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _guardar(self):
        import re
        valido = True
        
        # Validar cédula
        patron_ced = re.compile(r'^(?:[1-9]|1[0-2]|PE|E|N|PI|SB|AV)-\d+-\d+$', re.IGNORECASE)
        ced_ok = bool(patron_ced.match(self.inp_ced.text().strip()))
        self._validar_y_marcar(self.inp_ced, ced_ok)
        if not ced_ok: valido = False
        
        # Validar nombres
        nom_ok = len(self.inp_nom.text().strip()) > 0
        self._validar_y_marcar(self.inp_nom, nom_ok)
        if not nom_ok: valido = False
        
        # Validar apellidos
        ape_ok = len(self.inp_ape.text().strip()) > 0
        self._validar_y_marcar(self.inp_ape, ape_ok)
        if not ape_ok: valido = False
        
        # Validar teléfono si tiene texto
        tel_txt = self.inp_tel.text().strip()
        if tel_txt:
            patron_tel = re.compile(r'^\+?\d{3,4}-?\d{4}$|^\d{7,8}$')
            tel_ok = bool(patron_tel.match(tel_txt))
            self._validar_y_marcar(self.inp_tel, tel_ok)
            if not tel_ok: valido = False
            
        if not valido:
            QMessageBox.warning(self, "⚠ Validación", "Por favor corrija los campos marcados en rojo.")
            return

        fq=self.inp_fec.date()
        datos={"cedula":self.inp_ced.text(),"nombre":self.inp_nom.text(),"apellido":self.inp_ape.text(),
               "fecha_nacimiento":date(fq.year(),fq.month(),fq.day()),"genero":self.cmb_gen.currentData(),
               "nacionalidad":self.inp_nac.text(),"telefono":self.inp_tel.text(),
               "direccion":self.inp_dir.toPlainText(),"contacto_emergencia":self.inp_ce.text(),
               "telefono_emergencia":self.inp_te.text(),"tipo_sangre":self.cmb_san.currentData(),
               "alergias":self.inp_ale.toPlainText(),"enfermedades_cronicas":self.inp_ecr.toPlainText(),
               "medicamentos_actuales":self.inp_med.toPlainText(),"antecedentes_familiares":self.inp_ant.toPlainText(),
               "vacunas_aplicadas":self.inp_vac.toPlainText(),"cirugias_previas":self.inp_cir.toPlainText()}
        self.btn_g.setEnabled(False)
        ok,msg,_=paciente_controller.registrar_paciente(datos)
        self.btn_g.setEnabled(True)
        if ok: QMessageBox.information(self,"✅ Registrado",msg); self._limpiar()
        else: QMessageBox.warning(self,"⚠ Error",msg)

    def _limpiar(self):
        for w in self.findChildren(QLineEdit):
            w.clear()
            self._reset_marcado(w)
        for w in self.findChildren(QTextEdit):
            w.clear()
            self._reset_marcado(w)
        self.cmb_gen.setCurrentIndex(0); self.cmb_san.setCurrentIndex(0)
        self.inp_fec.setDate(QDate(1990,1,1)); self.inp_ced.setFocus()
