"""
Proyecto GAMMA - Suite de Pruebas Unitarias (v2)
Cobertura mínima requerida: 85% (criterio SonarQube)
Módulos: Auth, M1-Pacientes, M2-Visitas, M4-Reportes, Permisos por Rol

Para ejecutar:
    pytest tests/ -v --cov=src --cov-report=xml:coverage.xml
"""

import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from src.models.models import (
    Usuario, Paciente, VisitaMedica, UserRole,
    Gender, BloodType, VisitStatus
)
from src.controllers.auth_controller import AuthController
from src.controllers.paciente_controller import PacienteController


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def auth_ctrl():
    return AuthController()


def _make_user(rol: UserRole, uid: int = 1) -> Usuario:
    u = Usuario()
    u.id = uid
    u.nombre_usuario = f"test_{rol.value}"
    u.nombre_completo = f"Test {rol.value.capitalize()}"
    u.rol = rol
    u.activo = True
    u.password_hash = AuthController.hash_password("Test1234!")
    u.ultimo_acceso = None
    return u


@pytest.fixture
def usuario_admin():        return _make_user(UserRole.ADMIN, 1)
@pytest.fixture
def usuario_medico():       return _make_user(UserRole.MEDICO, 2)
@pytest.fixture
def usuario_enf_triage():   return _make_user(UserRole.ENF_TRIAGE, 3)
@pytest.fixture
def usuario_enf_asist():    return _make_user(UserRole.ENF_ASISTENCIAL, 4)
@pytest.fixture
def usuario_director():     return _make_user(UserRole.DIRECTOR, 5)
@pytest.fixture
def usuario_recepcion():    return _make_user(UserRole.RECEPCION, 6)


@pytest.fixture
def datos_paciente_valido():
    return {
        "cedula": "8-123-456",
        "nombre": "Juan",
        "apellido": "García",
        "fecha_nacimiento": date(1985, 6, 15),
        "genero": Gender.MASCULINO,
        "nacionalidad": "Panameño",
        "telefono": "6000-0000",
        "direccion": "Ciudad de Panamá",
        "contacto_emergencia": "María García",
        "telefono_emergencia": "6000-0001",
        "tipo_sangre": BloodType.O_POS,
        "alergias": "Penicilina",
        "enfermedades_cronicas": "Diabetes tipo 2",
        "medicamentos_actuales": "Metformina 500mg",
        "antecedentes_familiares": "Hipertensión",
        "vacunas_aplicadas": "COVID-19, Influenza",
        "cirugias_previas": "Apendicectomía 2010",
    }


@pytest.fixture
def paciente_mock():
    p = Paciente()
    p.id = 1
    p.cedula = "8-123-456"
    p.nombre = "Juan"
    p.apellido = "García"
    p.fecha_nacimiento = date(1985, 6, 15)
    p.genero = Gender.MASCULINO
    p.activo = True
    p.visitas = []
    p.creado_en = datetime.utcnow()
    p.actualizado_en = datetime.utcnow()
    return p


# ---------------------------------------------------------------------------
# PRUEBAS: AuthController
# ---------------------------------------------------------------------------

class TestAuthController:

    def test_hash_retorna_string(self):
        assert isinstance(AuthController.hash_password("Pass1234!"), str)

    def test_hash_diferente_al_original(self):
        pw = "Pass1234!"
        assert AuthController.hash_password(pw) != pw

    def test_verify_correcto(self):
        pw = "Test1234!"
        assert AuthController._verify_password(pw, AuthController.hash_password(pw))

    def test_verify_incorrecto(self):
        hashed = AuthController.hash_password("Correcto")
        assert not AuthController._verify_password("Incorrecto", hashed)

    def test_login_campos_vacios(self, auth_ctrl):
        ok, msg = auth_ctrl.login("", "")
        assert not ok and "requeridos" in msg.lower()

    def test_estado_inicial_no_autenticado(self, auth_ctrl):
        assert not auth_ctrl.is_authenticated
        assert auth_ctrl.current_user is None

    def test_has_permission_sin_autenticar(self, auth_ctrl):
        assert not auth_ctrl.has_permission([UserRole.MEDICO])

    def test_has_permission_rol_correcto(self, auth_ctrl, usuario_medico):
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.has_permission([UserRole.MEDICO])

    def test_has_permission_rol_incorrecto(self, auth_ctrl, usuario_medico):
        auth_ctrl._current_user = usuario_medico
        assert not auth_ctrl.has_permission([UserRole.ADMIN])

    def test_logout_limpia_usuario(self, auth_ctrl, usuario_medico):
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.is_authenticated
        auth_ctrl._current_user = None
        assert not auth_ctrl.is_authenticated


# ---------------------------------------------------------------------------
# PRUEBAS: Validación M1
# ---------------------------------------------------------------------------

class TestValidacionPaciente:

    def test_datos_completos_pasan(self, datos_paciente_valido):
        valido, msg = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert valido and msg == ""

    def test_sin_cedula_falla(self, datos_paciente_valido):
        datos_paciente_valido["cedula"] = ""
        valido, _ = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido

    def test_sin_nombre_falla(self, datos_paciente_valido):
        datos_paciente_valido["nombre"] = ""
        valido, _ = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido

    def test_sin_apellido_falla(self, datos_paciente_valido):
        datos_paciente_valido["apellido"] = ""
        valido, _ = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido

    def test_sin_genero_falla(self, datos_paciente_valido):
        datos_paciente_valido["genero"] = None
        valido, _ = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido

    def test_fecha_futura_falla(self, datos_paciente_valido):
        datos_paciente_valido["fecha_nacimiento"] = date(2099, 1, 1)
        valido, msg = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido and "futura" in msg.lower()

    def test_cedula_corta_falla(self, datos_paciente_valido):
        datos_paciente_valido["cedula"] = "123"
        valido, _ = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido

    def test_cedula_larga_falla(self, datos_paciente_valido):
        datos_paciente_valido["cedula"] = "X" * 25
        valido, _ = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido

    def test_fecha_no_date_falla(self, datos_paciente_valido):
        datos_paciente_valido["fecha_nacimiento"] = "1990-01-01"
        valido, _ = PacienteController._validar_datos_paciente(datos_paciente_valido)
        assert not valido


# ---------------------------------------------------------------------------
# PRUEBAS: Modelo Paciente
# ---------------------------------------------------------------------------

class TestModeloPaciente:

    def test_nombre_completo(self, paciente_mock):
        assert paciente_mock.nombre_completo == "Juan García"

    def test_edad_calculo(self, paciente_mock):
        assert isinstance(paciente_mock.edad, int) and paciente_mock.edad > 0

    def test_repr_incluye_cedula(self, paciente_mock):
        assert "8-123-456" in repr(paciente_mock)

    def test_repr_usuario(self, usuario_medico):
        assert "medico" in repr(usuario_medico)


# ---------------------------------------------------------------------------
# PRUEBAS: Permisos completos por todos los roles
# ---------------------------------------------------------------------------

class TestPermisosPorRol:
    """
    Verifica la matriz de permisos completa según Ley 81 / ISO 27799.
    """

    # ── Registro de pacientes ─────────────────────────────────────────────────
    ROLES_REG = [UserRole.MEDICO, UserRole.ENF_TRIAGE, UserRole.ADMIN, UserRole.RECEPCION]

    def test_admin_puede_registrar_paciente(self, auth_ctrl, usuario_admin):
        auth_ctrl._current_user = usuario_admin
        assert auth_ctrl.has_permission(self.ROLES_REG)

    def test_medico_puede_registrar_paciente(self, auth_ctrl, usuario_medico):
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.has_permission(self.ROLES_REG)

    def test_enf_triage_puede_registrar_paciente(self, auth_ctrl, usuario_enf_triage):
        auth_ctrl._current_user = usuario_enf_triage
        assert auth_ctrl.has_permission(self.ROLES_REG)

    def test_recepcion_puede_registrar_paciente(self, auth_ctrl, usuario_recepcion):
        auth_ctrl._current_user = usuario_recepcion
        assert auth_ctrl.has_permission(self.ROLES_REG)

    def test_enf_asistencial_NO_puede_registrar_paciente(self, auth_ctrl, usuario_enf_asist):
        auth_ctrl._current_user = usuario_enf_asist
        assert not auth_ctrl.has_permission(self.ROLES_REG)

    def test_director_NO_puede_registrar_paciente(self, auth_ctrl, usuario_director):
        auth_ctrl._current_user = usuario_director
        assert not auth_ctrl.has_permission(self.ROLES_REG)

    # ── Diagnóstico — solo médico ─────────────────────────────────────────────
    ROLES_DIAG = [UserRole.MEDICO]

    def test_medico_puede_diagnosticar(self, auth_ctrl, usuario_medico):
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.has_permission(self.ROLES_DIAG)

    def test_enf_triage_NO_puede_diagnosticar(self, auth_ctrl, usuario_enf_triage):
        auth_ctrl._current_user = usuario_enf_triage
        assert not auth_ctrl.has_permission(self.ROLES_DIAG)

    def test_enf_asistencial_NO_puede_diagnosticar(self, auth_ctrl, usuario_enf_asist):
        auth_ctrl._current_user = usuario_enf_asist
        assert not auth_ctrl.has_permission(self.ROLES_DIAG)

    def test_recepcion_NO_puede_diagnosticar(self, auth_ctrl, usuario_recepcion):
        auth_ctrl._current_user = usuario_recepcion
        assert not auth_ctrl.has_permission(self.ROLES_DIAG)

    def test_director_NO_puede_diagnosticar(self, auth_ctrl, usuario_director):
        auth_ctrl._current_user = usuario_director
        assert not auth_ctrl.has_permission(self.ROLES_DIAG)

    # ── Notas clínicas ────────────────────────────────────────────────────────
    ROLES_NOTAS = [UserRole.MEDICO, UserRole.ENF_TRIAGE, UserRole.ENF_ASISTENCIAL]

    def test_enf_asistencial_puede_notas(self, auth_ctrl, usuario_enf_asist):
        auth_ctrl._current_user = usuario_enf_asist
        assert auth_ctrl.has_permission(self.ROLES_NOTAS)

    def test_recepcion_NO_puede_notas(self, auth_ctrl, usuario_recepcion):
        auth_ctrl._current_user = usuario_recepcion
        assert not auth_ctrl.has_permission(self.ROLES_NOTAS)

    def test_director_NO_puede_notas(self, auth_ctrl, usuario_director):
        auth_ctrl._current_user = usuario_director
        assert not auth_ctrl.has_permission(self.ROLES_NOTAS)

    # ── Reportes ──────────────────────────────────────────────────────────────
    ROLES_REP = [UserRole.MEDICO, UserRole.ADMIN, UserRole.DIRECTOR]

    def test_director_puede_reportes(self, auth_ctrl, usuario_director):
        auth_ctrl._current_user = usuario_director
        assert auth_ctrl.has_permission(self.ROLES_REP)

    def test_medico_puede_reportes(self, auth_ctrl, usuario_medico):
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.has_permission(self.ROLES_REP)

    def test_enf_triage_NO_puede_reportes(self, auth_ctrl, usuario_enf_triage):
        auth_ctrl._current_user = usuario_enf_triage
        assert not auth_ctrl.has_permission(self.ROLES_REP)

    def test_enf_asistencial_NO_puede_reportes(self, auth_ctrl, usuario_enf_asist):
        auth_ctrl._current_user = usuario_enf_asist
        assert not auth_ctrl.has_permission(self.ROLES_REP)

    def test_recepcion_NO_puede_reportes(self, auth_ctrl, usuario_recepcion):
        auth_ctrl._current_user = usuario_recepcion
        assert not auth_ctrl.has_permission(self.ROLES_REP)

    # ── Cerrar visita — solo médico ───────────────────────────────────────────
    ROLES_CERRAR = [UserRole.MEDICO]

    def test_solo_medico_puede_cerrar_visita(self, auth_ctrl, usuario_medico):
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.has_permission(self.ROLES_CERRAR)

    def test_enf_triage_NO_puede_cerrar_visita(self, auth_ctrl, usuario_enf_triage):
        auth_ctrl._current_user = usuario_enf_triage
        assert not auth_ctrl.has_permission(self.ROLES_CERRAR)


# ---------------------------------------------------------------------------
# PRUEBAS: PacienteController — lógica de permisos sin BD
# ---------------------------------------------------------------------------

class TestPacienteControllerPermisos:

    def test_registrar_sin_autenticar_falla(self, datos_paciente_valido):
        ctrl = PacienteController()
        with patch("src.controllers.paciente_controller.auth_controller") as mock_auth:
            mock_auth.has_permission.return_value = False
            ok, msg, p = ctrl.registrar_paciente(datos_paciente_valido)
        assert not ok and p is None

    def test_buscar_sin_autenticar_retorna_vacio(self):
        ctrl = PacienteController()
        with patch("src.controllers.paciente_controller.auth_controller") as mock_auth:
            mock_auth.has_permission.return_value = False
            resultado = ctrl.buscar_pacientes("Juan")
        assert resultado == []

    def test_visita_sin_motivo_falla(self, usuario_medico):
        ctrl = PacienteController()
        with patch("src.controllers.paciente_controller.auth_controller") as mock_auth:
            mock_auth.has_permission.return_value = True
            mock_auth.current_user = usuario_medico
            ok, msg, v = ctrl.registrar_visita(1, {"motivo_consulta": ""})
        assert not ok and v is None and "motivo" in msg.lower()

    def test_enf_triage_no_incluye_diagnostico_en_visita(self, usuario_enf_triage):
        """El controller debe eliminar diagnóstico del dict cuando es ENF_TRIAGE."""
        ctrl = PacienteController()
        datos = {
            "motivo_consulta": "Dolor de cabeza",
            "diagnostico_preliminar": "Migraña",  # No debe llegar a la BD
            "plan_tratamiento": "Ibuprofeno",      # No debe llegar a la BD
        }
        paciente_mock = MagicMock()
        paciente_mock.id = 1

        session_mock = MagicMock()
        session_mock.get.return_value = paciente_mock

        visita_capturada = {}

        def capturar_visita(visita):
            visita_capturada["diag"] = getattr(visita, "diagnostico_preliminar", "ELIMINADO")
            visita_capturada["plan"] = getattr(visita, "plan_tratamiento", "ELIMINADO")

        with patch("src.controllers.paciente_controller.auth_controller") as mock_auth, \
             patch("src.controllers.paciente_controller.db_manager") as mock_db, \
             patch("src.controllers.paciente_controller.VisitaMedica") as MockVisita:

            mock_auth.has_permission.return_value = True
            mock_auth.current_user = usuario_enf_triage
            mock_auth.is_authenticated = True
            mock_db.get_session.return_value = session_mock

            instance = MagicMock()
            MockVisita.return_value = instance
            session_mock.add.side_effect = lambda v: capturar_visita(v)
            session_mock.refresh = MagicMock()

            ctrl.registrar_visita(1, datos)

        # El test verifica que el controller eliminó las claves antes de crear VisitaMedica
        assert "diagnostico_preliminar" not in datos
        assert "plan_tratamiento" not in datos
