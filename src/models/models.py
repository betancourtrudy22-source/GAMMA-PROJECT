"""
Proyecto GAMMA - Modelos de Base de Datos
Sistema de Gestión de Expedientes Médicos
Universidad Tecnológica de Panamá

Módulos cubiertos:
    M1 - Registro de Pacientes
    M2 - Actualización de Expedientes
    M3 - Acceso y Consulta
    M4 - Generación de Reportes (datos)
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Date, Enum, ForeignKey, Boolean, Float
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""
    pass


# ---------------------------------------------------------------------------
# ENUMERACIONES
# ---------------------------------------------------------------------------

class UserRole(enum.Enum):
    """Roles de usuario del sistema (ISO 27799 - Control de acceso por rol)."""
    MEDICO = "medico"
    ENFERMERA = "enfermera"
    ADMIN = "admin"
    DIRECTOR = "director"
    RECEPCION = "recepcion"


class BloodType(enum.Enum):
    """Tipos de sangre."""
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class Gender(enum.Enum):
    """Género del paciente."""
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"
    OTRO = "Otro"


class VisitStatus(enum.Enum):
    """Estado de la visita médica."""
    ACTIVA = "Activa"
    CERRADA = "Cerrada"
    PENDIENTE = "Pendiente"


# ---------------------------------------------------------------------------
# M0 - USUARIOS DEL SISTEMA
# ---------------------------------------------------------------------------

class Usuario(Base):
    """
    Modelo de usuario del sistema.
    Control de acceso por roles según ISO 27799.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(UserRole), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    ultimo_acceso = Column(DateTime, nullable=True)

    # Relaciones
    visitas_registradas = relationship(
        "VisitaMedica", back_populates="medico_tratante",
        foreign_keys="VisitaMedica.medico_id"
    )
    logs = relationship("AuditoriaLog", back_populates="usuario")

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, usuario='{self.nombre_usuario}', rol={self.rol})>"


# ---------------------------------------------------------------------------
# M1 - REGISTRO DE PACIENTES
# ---------------------------------------------------------------------------

class Paciente(Base):
    """
    Módulo M1: Registro de Pacientes.
    Captura de datos personales y médicos iniciales.
    Métrica: 100% campos obligatorios validados.
    """
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Datos de identificación
    cedula = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(80), nullable=False)
    apellido = Column(String(80), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(Enum(Gender), nullable=False)
    nacionalidad = Column(String(60), nullable=True)
    direccion = Column(Text, nullable=True)
    telefono = Column(String(20), nullable=True)
    contacto_emergencia = Column(String(150), nullable=True)
    telefono_emergencia = Column(String(20), nullable=True)

    # Datos médicos iniciales
    tipo_sangre = Column(Enum(BloodType), nullable=True)
    alergias = Column(Text, nullable=True)
    enfermedades_cronicas = Column(Text, nullable=True)
    medicamentos_actuales = Column(Text, nullable=True)
    antecedentes_familiares = Column(Text, nullable=True)
    vacunas_aplicadas = Column(Text, nullable=True)
    cirugias_previas = Column(Text, nullable=True)

    # Metadata
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(
        DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    visitas = relationship(
        "VisitaMedica", back_populates="paciente",
        order_by="desc(VisitaMedica.fecha_ingreso)"
    )

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del paciente."""
        return f"{self.nombre} {self.apellido}"

    @property
    def edad(self) -> int:
        """Calcula la edad actual del paciente."""
        hoy = datetime.today().date()
        edad = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (
            self.fecha_nacimiento.month, self.fecha_nacimiento.day
        ):
            edad -= 1
        return edad

    def __repr__(self) -> str:
        return (
            f"<Paciente(id={self.id}, cedula='{self.cedula}', "
            f"nombre='{self.nombre_completo}')>"
        )


# ---------------------------------------------------------------------------
# M2 - ACTUALIZACIÓN DE EXPEDIENTES
# ---------------------------------------------------------------------------

class VisitaMedica(Base):
    """
    Módulo M2: Actualización de Expedientes.
    Registro de visitas, diagnósticos, tratamientos y seguimiento.
    Métrica: Cambios reflejados en < 2 segundos.
    """
    __tablename__ = "visitas_medicas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Datos de la visita
    fecha_ingreso = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_cierre = Column(DateTime, nullable=True)
    motivo_consulta = Column(Text, nullable=False)
    area_especialidad = Column(String(100), nullable=True)
    estado = Column(Enum(VisitStatus), default=VisitStatus.ACTIVA, nullable=False)

    # Signos vitales
    presion_arterial = Column(String(20), nullable=True)
    temperatura = Column(Float, nullable=True)
    saturacion_oxigeno = Column(Float, nullable=True)
    frecuencia_cardiaca = Column(Integer, nullable=True)
    peso_kg = Column(Float, nullable=True)
    talla_cm = Column(Float, nullable=True)

    # Evaluación clínica
    diagnostico_preliminar = Column(Text, nullable=True)
    diagnostico_final = Column(Text, nullable=True)
    plan_tratamiento = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    # Metadata
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(
        DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    paciente = relationship("Paciente", back_populates="visitas")
    medico_tratante = relationship(
        "Usuario", back_populates="visitas_registradas",
        foreign_keys=[medico_id]
    )
    notas = relationship(
        "NotaMedica", back_populates="visita",
        order_by="desc(NotaMedica.creado_en)"
    )

    def __repr__(self) -> str:
        return (
            f"<VisitaMedica(id={self.id}, paciente_id={self.paciente_id}, "
            f"fecha='{self.fecha_ingreso}')>"
        )


class NotaMedica(Base):
    """Notas clínicas adicionales por visita médica."""
    __tablename__ = "notas_medicas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visita_id = Column(Integer, ForeignKey("visitas_medicas.id"), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    visita = relationship("VisitaMedica", back_populates="notas")
    autor = relationship("Usuario")

    def __repr__(self) -> str:
        return f"<NotaMedica(id={self.id}, visita_id={self.visita_id})>"


# ---------------------------------------------------------------------------
# AUDITORÍA - ISO 27799
# ---------------------------------------------------------------------------

class AuditoriaLog(Base):
    """
    Log de auditoría de accesos y acciones.
    Requerido por ISO 27799 y ISO 27001.
    Registra quién accedió a qué expediente y cuándo.
    """
    __tablename__ = "auditoria_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    accion = Column(String(100), nullable=False)
    tabla_afectada = Column(String(50), nullable=True)
    registro_id = Column(Integer, nullable=True)
    detalle = Column(Text, nullable=True)
    ip_origen = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="logs")

    def __repr__(self) -> str:
        return (
            f"<AuditoriaLog(id={self.id}, usuario_id={self.usuario_id}, "
            f"accion='{self.accion}')>"
        )
