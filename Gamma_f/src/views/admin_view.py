"""
Proyecto GAMMA - Vista del Administrador
Gestión de usuarios del sistema.
ISO 27001 / Ley 81 - Control de acceso.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QGridLayout, QSplitter
)
from PyQt6.QtCore import Qt
from src.models.models import UserRole, Usuario
from src.models.database import db_manager
from src.controllers.auth_controller import AuthController
from src.views._theme import ROL_ETIQUETAS, NAVY, TEAL, WHITE, BORDER, TEXT, MUTED, SUCCESS
from src.views._widgets import BannerWidget
from src.views._styles import btn_primary, btn_secondary, btn_danger
from src.views._common import (
    TABLA_QSS, INPUT_QSS, WIDGET_BG,
    titulo_style, sec_style, campo_style
)

ROL_OPCIONES = {
    "Administrador":         UserRole.ADMIN,
    "Médico":                UserRole.MEDICO,
    "Enfermero Triage":      UserRole.ENF_TRIAGE,
    "Enfermero Asistencial": UserRole.ENF_ASISTENCIAL,
    "Director Médico":       UserRole.DIRECTOR,
    "Recepción":             UserRole.RECEPCION,
    "Medicina Interna":      UserRole.MEDICINA_INTERNA,
}


class AdminView(QWidget):
    def __init__(self):
        super().__init__()
        self._todos = []
        self.setStyleSheet(WIDGET_BG)
        self._setup_ui()

    def _lbl(self, t): l = QLabel(t.upper()); l.setStyleSheet(campo_style()); return l
    def _sec(self, t): l = QLabel(t.upper()); l.setStyleSheet(sec_style()); return l
    def _inp(self, ph): i = QLineEdit(); i.setPlaceholderText(ph); i.setStyleSheet(INPUT_QSS); return i

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(12)

        # ── Encabezado ────────────────────────────────────────────────────────
        enc = QHBoxLayout()
        t = QLabel("Gestión de Usuarios"); t.setStyleSheet(titulo_style())
        enc.addWidget(t); enc.addStretch()
        btn_ref = btn_secondary("↻  Actualizar"); btn_ref.clicked.connect(self._cargar)
        enc.addWidget(btn_ref)
        layout.addLayout(enc)

        # ── Banner ────────────────────────────────────────────────────────────
        layout.addWidget(BannerWidget("⚙️", "Gestión de Usuarios del Sistema", "", NAVY, "#1A4F8A"))

        # ── Splitter: tabla | formulario ──────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Panel izquierdo — tabla
        left = QFrame()
        left.setStyleSheet(f"QFrame{{background-color:{WHITE};border-radius:14px;border:1px solid {BORDER};}}")
        ll = QVBoxLayout(left); ll.setContentsMargins(16, 16, 16, 16); ll.setSpacing(12)
        ll.addWidget(self._sec("Usuarios del Sistema"))

        self.inp_filtro = self._inp("Filtrar por usuario o nombre...")
        self.inp_filtro.textChanged.connect(self._filtrar)
        ll.addWidget(self.inp_filtro)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre", "Rol", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setShowGrid(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet(TABLA_QSS)
        ll.addWidget(self.tabla)

        acc = QHBoxLayout(); acc.setSpacing(10)
        btn_tog = btn_secondary("⏸  Activar / Inactivar"); btn_tog.clicked.connect(self._toggle)
        btn_del = btn_danger("🗑  Eliminar"); btn_del.clicked.connect(self._eliminar)
        acc.addWidget(btn_tog); acc.addWidget(btn_del); acc.addStretch()
        ll.addLayout(acc)
        splitter.addWidget(left)

        # Panel derecho — formulario
        right = QFrame()
        right.setStyleSheet(
            f"QFrame{{background-color:{WHITE};border-radius:14px;"
            f"border:1px solid {BORDER};border-top:3px solid {TEAL};}}"
        )
        rl = QVBoxLayout(right); rl.setContentsMargins(22, 20, 22, 20); rl.setSpacing(14)
        rl.addWidget(self._sec("Crear Nuevo Usuario"))

        g = QGridLayout(); g.setSpacing(12)
        g.setColumnStretch(0, 1); g.setColumnStretch(1, 1)

        self.inp_usr  = self._inp("ej. dr.rodriguez")
        self.inp_nom  = self._inp("Nombre completo")
        self.inp_mail = self._inp("correo@hospital.gob.pa")
        self.inp_pwd  = self._inp("Mínimo 8 caracteres")
        self.inp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.cmb_rol  = QComboBox(); self.cmb_rol.setStyleSheet(INPUT_QSS)
        for etq in ROL_OPCIONES: self.cmb_rol.addItem(etq)

        g.addWidget(self._lbl("Usuario *"),         0, 0); g.addWidget(self.inp_usr,  1, 0)
        g.addWidget(self._lbl("Nombre Completo *"), 0, 1); g.addWidget(self.inp_nom,  1, 1)
        g.addWidget(self._lbl("Email"),             2, 0); g.addWidget(self.inp_mail, 3, 0)
        g.addWidget(self._lbl("Contraseña *"),      2, 1); g.addWidget(self.inp_pwd,  3, 1)
        g.addWidget(self._lbl("Rol *"),             4, 0); g.addWidget(self.cmb_rol,  5, 0)
        rl.addLayout(g)
        rl.addStretch()

        br = QHBoxLayout(); br.setSpacing(10)
        btn_lim = btn_secondary("Limpiar"); btn_lim.clicked.connect(self._limpiar)
        self.btn_crear = btn_primary("✔  Crear Usuario"); self.btn_crear.clicked.connect(self._crear)
        br.addWidget(btn_lim); br.addStretch(); br.addWidget(self.btn_crear)
        rl.addLayout(br)

        splitter.addWidget(right)
        splitter.setSizes([520, 440])
        layout.addWidget(splitter, stretch=1)

        self._cargar()

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _cargar(self):
        session = db_manager.get_session()
        try:
            self._todos = session.query(Usuario).order_by(Usuario.nombre_completo).all()
            self._poblar(self._todos)
        finally:
            session.close()

    def _poblar(self, usuarios):
        self.tabla.setRowCount(0)
        self.tabla.setRowCount(len(usuarios))
        for i, u in enumerate(usuarios):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(u.id)))
            self.tabla.setItem(i, 1, QTableWidgetItem(u.nombre_usuario))
            self.tabla.setItem(i, 2, QTableWidgetItem(u.nombre_completo))
            self.tabla.setItem(i, 3, QTableWidgetItem(ROL_ETIQUETAS.get(u.rol, u.rol.value)))
            self.tabla.setItem(i, 4, QTableWidgetItem("✅ Activo" if u.activo else "⛔ Inactivo"))
            self.tabla.item(i, 0).setData(Qt.ItemDataRole.UserRole, u)

    def _filtrar(self, t):
        t = t.lower().strip()
        f = [u for u in self._todos
             if t in u.nombre_usuario.lower() or t in u.nombre_completo.lower()] if t else self._todos
        self._poblar(f)

    def _get_sel(self):
        f = self.tabla.currentRow()
        if f < 0:
            QMessageBox.information(self, "Atención", "Seleccione un usuario."); return None
        return self.tabla.item(f, 0).data(Qt.ItemDataRole.UserRole)

    def _toggle(self):
        u = self._get_sel()
        if not u: return
        if u.nombre_usuario == "admin":
            QMessageBox.warning(self, "No permitido", "No se puede inactivar al admin principal."); return
        session = db_manager.get_session()
        try:
            usr = session.get(Usuario, u.id)
            usr.activo = not usr.activo
            session.commit()
            QMessageBox.information(self, "Listo", f"Usuario {'activado' if usr.activo else 'inactivado'}.")
            self._cargar()
        except Exception as e:
            session.rollback(); QMessageBox.warning(self, "Error", str(e))
        finally:
            session.close()

    def _eliminar(self):
        u = self._get_sel()
        if not u: return
        if u.nombre_usuario == "admin":
            QMessageBox.warning(self, "No permitido", "No se puede eliminar al admin principal."); return
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar a '{u.nombre_usuario}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) \
                != QMessageBox.StandardButton.Yes: return
        session = db_manager.get_session()
        try:
            session.delete(session.get(Usuario, u.id))
            session.commit()
            QMessageBox.information(self, "Eliminado", "Usuario eliminado.")
            self._cargar()
        except Exception as e:
            session.rollback(); QMessageBox.warning(self, "Error", str(e))
        finally:
            session.close()

    def _crear(self):
        nom   = self.inp_usr.text().strip()
        nom_c = self.inp_nom.text().strip()
        mail  = self.inp_mail.text().strip()
        pwd   = self.inp_pwd.text()
        rol   = ROL_OPCIONES[self.cmb_rol.currentText()]

        if not nom or not nom_c or not pwd:
            QMessageBox.warning(self, "Incompleto", "Usuario, Nombre y Contraseña son obligatorios."); return
        if len(pwd) < 8:
            QMessageBox.warning(self, "Débil", "La contraseña debe tener al menos 8 caracteres."); return

        session = db_manager.get_session()
        try:
            if session.query(Usuario).filter(Usuario.nombre_usuario == nom).first():
                QMessageBox.warning(self, "Duplicado", f"El usuario '{nom}' ya existe."); return
            session.add(Usuario(
                nombre_usuario=nom, nombre_completo=nom_c,
                email=mail or None,
                password_hash=AuthController.hash_password(pwd),
                rol=rol, activo=True
            ))
            session.commit()
            QMessageBox.information(self, "Creado", f"✅ Usuario '{nom}' creado.")
            self._limpiar(); self._cargar()
        except Exception as e:
            session.rollback(); QMessageBox.warning(self, "Error", str(e))
        finally:
            session.close()

    def _limpiar(self):
        self.inp_usr.clear(); self.inp_nom.clear()
        self.inp_mail.clear(); self.inp_pwd.clear()
        self.cmb_rol.setCurrentIndex(0)
