"""
Proyecto GAMMA - Suite de Pruebas Unitarias
Cobertura mínima requerida: 85% (criterio SonarQube)
Módulos: Auth, M1-Pacientes, M2-Visitas, M4-Reportes

Para ejecutar:
    pytest tests/ -v --cov=src --cov-report=xml:coverage.xml
"""

import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch, PropertyMock

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
    """Fixture: instancia limpia del controlador de autenticación."""
    return AuthController()


@pytest.fixture
def usuario_medico():
    """Fixture: usuario con rol Médico."""
    u = Usuario()
    u.id = 1
    u.nombre_usuario = "dr.test"
    u.nombre_completo = "Dr. Test Médico"
    u.rol = UserRole.MEDICO
    u.activo = True
    u.password_hash = AuthController.hash_password("Test1234!")
    u.ultimo_acceso = None
    return u


@pytest.fixture
def usuario_enfermera():
    """Fixture: usuario con rol Enfermera."""
    u = Usuario()
    u.id = 2
    u.nombre_usuario = "enf.test"
    u.nombre_completo = "Enf. Test Prueba"
    u.rol = UserRole.ENFERMERA
    u.activo = True
    u.password_hash = AuthController.hash_password("Enf1234!")
    return u


@pytest.fixture
def usuario_director():
    """Fixture: usuario con rol Director."""
    u = Usuario()
    u.id = 3
    u.nombre_usuario = "dir.test"
    u.nombre_completo = "Director General"
    u.rol = UserRole.DIRECTOR
    u.activo = True
    u.password_hash = AuthController.hash_password("Dir1234!")
    return u


@pytest.fixture
def datos_paciente_valido():
    """Fixture: datos completos de un paciente válido."""
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
    """Fixture: objeto Paciente de prueba."""
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
    """Pruebas para el controlador de autenticación."""

    def test_hash_password_retorna_string(self):
        """El hash de una contraseña debe ser una cadena no vacía."""
        resultado = AuthController.hash_password("MiPassword123")
        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_hash_password_diferente_al_original(self):
        """El hash no debe ser igual a la contraseña en texto plano."""
        password = "MiPassword123"
        assert AuthController.hash_password(password) != password

    def test_verify_password_correcto(self):
        """Una contraseña válida debe verificarse correctamente."""
        password = "Test1234!"
        hashed = AuthController.hash_password(password)
        assert AuthController._verify_password(password, hashed) is True

    def test_verify_password_incorrecto(self):
        """Una contraseña incorrecta no debe verificarse."""
        hashed = AuthController.hash_password("PasswordCorrecto")
        assert AuthController._verify_password("PasswordIncorrecto", hashed) is False

    def test_login_campos_vacios(self, auth_ctrl):
        """Login con campos vacíos debe retornar False."""
        exito, msg = auth_ctrl.login("", "")
        assert exito is False
        assert "requeridos" in msg.lower()

    def test_login_usuario_vacio(self, auth_ctrl):
        """Login con usuario vacío debe retornar False."""
        exito, msg = auth_ctrl.login("", "password")
        assert exito is False

    def test_login_password_vacio(self, auth_ctrl):
        """Login con contraseña vacía debe retornar False."""
        exito, msg = auth_ctrl.login("usuario", "")
        assert exito is False

    def test_estado_inicial_no_autenticado(self, auth_ctrl):
        """El controlador inicia sin usuario autenticado."""
        assert auth_ctrl.is_authenticated is False
        assert auth_ctrl.current_user is None

    def test_has_permission_sin_autenticar(self, auth_ctrl):
        """Sin usuario autenticado, ningún permiso debe ser True."""
        assert auth_ctrl.has_permission([UserRole.MEDICO]) is False
        assert auth_ctrl.has_permission([UserRole.ADMIN]) is False

    def test_has_permission_con_rol_correcto(self, auth_ctrl, usuario_medico):
        """Un médico debe tener permiso para el rol MEDICO."""
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.has_permission([UserRole.MEDICO]) is True

    def test_has_permission_con_rol_incorrecto(self, auth_ctrl, usuario_medico):
        """Un médico no debe tener permiso de ADMIN."""
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.has_permission([UserRole.ADMIN]) is False

    def test_has_permission_multiples_roles(self, auth_ctrl, usuario_enfermera):
        """La enfermera debe tener permiso si su rol está en la lista."""
        auth_ctrl._current_user = usuario_enfermera
        permitidos = [UserRole.MEDICO, UserRole.ENFERMERA]
        assert auth_ctrl.has_permission(permitidos) is True

    def test_logout_limpia_usuario(self, auth_ctrl, usuario_medico):
        """El logout debe dejar is_authenticated en False."""
        auth_ctrl._current_user = usuario_medico
        assert auth_ctrl.is_authenticated is True

        # Simular logout directo sin llamar a la BD
        auth_ctrl._current_user = None
        assert auth_ctrl.is_authenticated is False
        assert auth_ctrl.current_user is None


# ---------------------------------------------------------------------------
# PRUEBAS: Validación M1 - Registro de Pacientes
# ---------------------------------------------------------------------------

class TestValidacionPaciente:
    """Pruebas de validación del formulario M1."""

    def test_validacion_campos_completos(self, datos_paciente_valido):
        """Datos completos deben pasar validación."""
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is True
        assert msg == ""

    def test_validacion_sin_cedula(self, datos_paciente_valido):
        """Falta de cédula debe fallar validación."""
        datos_paciente_valido["cedula"] = ""
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False
        assert "cédula" in msg.lower() or "cedula" in msg.lower()

    def test_validacion_sin_nombre(self, datos_paciente_valido):
        """Falta de nombre debe fallar validación."""
        datos_paciente_valido["nombre"] = ""
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False

    def test_validacion_sin_apellido(self, datos_paciente_valido):
        """Falta de apellido debe fallar validación."""
        datos_paciente_valido["apellido"] = ""
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False

    def test_validacion_sin_genero(self, datos_paciente_valido):
        """Falta de género debe fallar validación."""
        datos_paciente_valido["genero"] = None
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False

    def test_validacion_fecha_futura(self, datos_paciente_valido):
        """Fecha de nacimiento futura debe fallar validación."""
        datos_paciente_valido["fecha_nacimiento"] = date(2099, 1, 1)
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False
        assert "futura" in msg.lower()

    def test_validacion_cedula_muy_corta(self, datos_paciente_valido):
        """Cédula con menos de 5 caracteres debe fallar."""
        datos_paciente_valido["cedula"] = "123"
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False

    def test_validacion_cedula_muy_larga(self, datos_paciente_valido):
        """Cédula con más de 20 caracteres debe fallar."""
        datos_paciente_valido["cedula"] = "X" * 25
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False

    def test_validacion_fecha_no_es_date(self, datos_paciente_valido):
        """Fecha de nacimiento no tipo date debe fallar."""
        datos_paciente_valido["fecha_nacimiento"] = "1990-01-01"
        ctrl = PacienteController()
        valido, msg = ctrl._validar_datos_paciente(datos_paciente_valido)
        assert valido is False


# ---------------------------------------------------------------------------
# PRUEBAS: Modelo Paciente
# ---------------------------------------------------------------------------

class TestModeloPaciente:
    """Pruebas de los modelos de datos."""

    def test_nombre_completo(self, paciente_mock):
        """La propiedad nombre_completo debe concatenar nombre y apellido."""
        assert paciente_mock.nombre_completo == "Juan García"

    def test_edad_calculo(self, paciente_mock):
        """La edad calculada debe ser un entero positivo."""
        edad = paciente_mock.edad
        assert isinstance(edad, int)
        assert edad > 0

    def test_repr_paciente(self, paciente_mock):
        """El repr del paciente debe incluir su cédula."""
        repr_str = repr(paciente_mock)
        assert "8-123-456" in repr_str

    def test_repr_usuario(self, usuario_medico):
        """El repr del usuario debe incluir su nombre."""
        repr_str = repr(usuario_medico)
        assert "dr.test" in repr_str


# ---------------------------------------------------------------------------
# PRUEBAS: Permisos por Rol
# ---------------------------------------------------------------------------

class TestPermisosPorRol:
    """Verifica que el control de acceso por rol funcione correctamente."""

    def test_medico_puede_registrar(self, auth_ctrl, usuario_medico):
        """El médico debe poder registrar pacientes."""
        auth_ctrl._current_user = usuario_medico
        roles = [UserRole.MEDICO, UserRole.ENFERMERA, UserRole.ADMIN, UserRole.RECEPCION]
        assert auth_ctrl.has_permission(roles) is True

    def test_director_solo_lectura(self, auth_ctrl, usuario_director):
        """El director no debe poder registrar pacientes (escritura)."""
        auth_ctrl._current_user = usuario_director
        roles_escritura = [UserRole.MEDICO, UserRole.ENFERMERA, UserRole.ADMIN]
        assert auth_ctrl.has_permission(roles_escritura) is False

    def test_director_puede_ver_reportes(self, auth_ctrl, usuario_director):
        """El director debe poder acceder a reportes."""
        auth_ctrl._current_user = usuario_director
        roles_reporte = [UserRole.MEDICO, UserRole.ADMIN, UserRole.DIRECTOR]
        assert auth_ctrl.has_permission(roles_reporte) is True

    def test_enfermera_no_puede_ver_reportes(self, auth_ctrl, usuario_enfermera):
        """La enfermera no debe poder acceder a reportes."""
        auth_ctrl._current_user = usuario_enfermera
        roles_reporte = [UserRole.MEDICO, UserRole.ADMIN, UserRole.DIRECTOR]
        assert auth_ctrl.has_permission(roles_reporte) is False


# ---------------------------------------------------------------------------
# PRUEBAS: Controlador de Pacientes (con mock de BD)
# ---------------------------------------------------------------------------

class TestPacienteControllerPermisos:
    """Pruebas de permisos del controlador de pacientes."""

    def test_registrar_sin_autenticar(self, datos_paciente_valido):
        """Sin autenticación, registrar paciente debe fallar."""
        ctrl = PacienteController()
        # auth_controller global no está autenticado
        with patch(
            "src.controllers.paciente_controller.auth_controller"
        ) as mock_auth:
            mock_auth.has_permission.return_value = False
            exito, msg, paciente = ctrl.registrar_paciente(datos_paciente_valido)
        assert exito is False
        assert paciente is None

    def test_buscar_sin_autenticar(self):
        """Sin autenticación, buscar pacientes debe retornar lista vacía."""
        ctrl = PacienteController()
        with patch(
            "src.controllers.paciente_controller.auth_controller"
        ) as mock_auth:
            mock_auth.has_permission.return_value = False
            resultado = ctrl.buscar_pacientes("Juan")
        assert resultado == []

    def test_registrar_visita_sin_motivo(self, auth_ctrl, usuario_medico):
        """Visita sin motivo de consulta debe fallar."""
        ctrl = PacienteController()
        with patch(
            "src.controllers.paciente_controller.auth_controller"
        ) as mock_auth:
            mock_auth.has_permission.return_value = True
            mock_auth.current_user = usuario_medico
            exito, msg, visita = ctrl.registrar_visita(1, {"motivo_consulta": ""})
        assert exito is False
        assert visita is None
        assert "motivo" in msg.lower()
