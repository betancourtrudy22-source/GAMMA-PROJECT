"""Proyecto GAMMA - Vista del Director Médico"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,QFrame,QSizePolicy,QScrollArea
)
from src.controllers.reporte_controller import reporte_controller
from src.views._theme import NAVY,TEAL,SUCCESS,AMBER,PURPLE,BG,WHITE,BORDER,TEXT,MUTED
from src.views._widgets import BannerWidget,KpiCard
from src.views._styles import btn_secondary
from src.views._common import WIDGET_BG,SCROLL_QSS,CONT_BG,titulo_style,desc_style,sec_style

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MPL=True
except ImportError:
    MPL=False

COLORS=[NAVY,TEAL,"#F6AD55","#805AD5","#E53E3E","#38A169"]

class DirectorView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(WIDGET_BG); self._setup_ui()

    def _setup_ui(self):
        from src.controllers.auth_controller import auth_controller
        usuario=auth_controller.current_user
        outer=QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet(SCROLL_QSS)
        outer.addWidget(scroll)
        cont=QWidget(); cont.setStyleSheet(CONT_BG)
        layout=QVBoxLayout(cont); layout.setContentsMargins(32,28,32,28); layout.setSpacing(20)
        scroll.setWidget(cont)

        enc=QHBoxLayout(); col=QVBoxLayout(); col.setSpacing(2)
        t=QLabel("Panel del Director"); t.setStyleSheet(titulo_style())
        col.addWidget(t); enc.addLayout(col); enc.addStretch()
        btn=btn_secondary("↻  Actualizar"); btn.clicked.connect(self._cargar); enc.addWidget(btn)
        layout.addLayout(enc)

        layout.addWidget(BannerWidget("📊",f"Panel Ejecutivo — {usuario.nombre_completo}",
                                      "",
                                      "#44337A","#6B46C1"))

        kpi_row=QHBoxLayout(); kpi_row.setSpacing(16)
        self.kpi_pac=KpiCard("👥","—","Total Pacientes",NAVY)
        self.kpi_vis=KpiCard("📋","—","Total Visitas",SUCCESS)
        self.kpi_act=KpiCard("⚡","—","Visitas Activas",AMBER)
        self.kpi_mes=KpiCard("📅",datetime.now().strftime("%b").upper(),"Mes Actual",PURPLE)
        for k in [self.kpi_pac,self.kpi_vis,self.kpi_act,self.kpi_mes]: kpi_row.addWidget(k)
        layout.addLayout(kpi_row)

        graf_row=QHBoxLayout(); graf_row.setSpacing(16)
        g1=QFrame(); g1.setStyleSheet(f"QFrame{{background-color:{WHITE};border-radius:14px;border:1px solid {BORDER};}}"); g1.setMinimumHeight(280)
        g1l=QVBoxLayout(g1); g1l.setContentsMargins(20,16,20,16); g1l.setSpacing(12)
        lbl_g1=QLabel("VISITAS POR MES — AÑO ACTUAL"); lbl_g1.setStyleSheet(sec_style()); g1l.addWidget(lbl_g1)
        if MPL:
            self.fig1=Figure(figsize=(5,3),dpi=90); self.cv1=FigureCanvas(self.fig1)
            self.cv1.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding); g1l.addWidget(self.cv1)
        else: g1l.addWidget(QLabel("Instale matplotlib."))

        g2=QFrame(); g2.setStyleSheet(f"QFrame{{background-color:{WHITE};border-radius:14px;border:1px solid {BORDER};}}"); g2.setMinimumHeight(280)
        g2l=QVBoxLayout(g2); g2l.setContentsMargins(20,16,20,16); g2l.setSpacing(12)
        lbl_g2=QLabel("DISTRIBUCIÓN POR GÉNERO"); lbl_g2.setStyleSheet(sec_style()); g2l.addWidget(lbl_g2)
        if MPL:
            self.fig2=Figure(figsize=(3.5,3),dpi=90); self.cv2=FigureCanvas(self.fig2)
            g2l.addWidget(self.cv2)
        else: g2l.addWidget(QLabel("Instale matplotlib."))

        graf_row.addWidget(g1,stretch=2); graf_row.addWidget(g2,stretch=1)
        layout.addLayout(graf_row)

        self._cargar()

    def _cargar(self):
        s=reporte_controller.obtener_estadisticas_generales()
        if s:
            self.kpi_pac.set_valor(str(s["total_pacientes"]))
            self.kpi_vis.set_valor(str(s["total_visitas"]))
            self.kpi_act.set_valor(str(s["visitas_activas"]))
        if MPL: self._g1(); self._g2()

    def _g1(self):
        datos=reporte_controller.obtener_visitas_por_mes()
        self.fig1.clear(); ax=self.fig1.add_subplot(111)
        if datos:
            bars=ax.bar([d["mes"] for d in datos],[d["cantidad"] for d in datos],color=NAVY,alpha=0.85,zorder=3)
            ax.bar_label(bars,fmt="%d",padding=4,fontsize=9,color=MUTED)
        else: ax.text(0.5,0.5,"Sin datos",ha="center",va="center",transform=ax.transAxes,color=MUTED,fontsize=12)
        ax.set_facecolor("#F7FAFC"); self.fig1.patch.set_facecolor(WHITE)
        for sp in ["top","right"]: ax.spines[sp].set_visible(False)
        ax.tick_params(labelsize=9,colors=MUTED); ax.yaxis.grid(True,color="#EDF2F7",zorder=0)
        self.fig1.tight_layout(pad=1.5); self.cv1.draw()

    def _g2(self):
        datos=reporte_controller.obtener_distribucion_genero()
        self.fig2.clear(); ax=self.fig2.add_subplot(111)
        if datos:
            lbls=list(datos.keys()); vals=list(datos.values())
            _,_,auts=ax.pie(vals,labels=lbls,autopct="%1.1f%%",colors=COLORS[:len(lbls)],
                            startangle=90,pctdistance=0.80,wedgeprops={"linewidth":2,"edgecolor":WHITE},
                            textprops={"fontsize":10,"color":TEXT})
            for a in auts: a.set_fontsize(9); a.set_color(WHITE)
        else: ax.text(0.5,0.5,"Sin datos",ha="center",va="center",transform=ax.transAxes,color=MUTED,fontsize=12)
        self.fig2.patch.set_facecolor(WHITE); self.fig2.tight_layout(pad=1.5); self.cv2.draw()
