"""
Gamma — Módulo M1: Registro de Pacientes
Modelos SQLAlchemy para PostgreSQL.

Decisiones de arquitectura:
- Schema 'gamma' separado del schema public para control de permisos.
- UUID como PK: opacos, seguros, no inferibles por atacantes.
- Campos de auditoría en cada tabla (created_at, creado_por).
- Relaciones con ON DELETE RESTRICT: datos médicos son inmutables.
- Enums para campos con valores controlados (estado, género, tipo_sangre).
- Todos los modelos heredan de Base con configuración de schema centralizada.
"""

from __future__ import annotations

import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ── Base declarativa con schema centralizado ──────────────────────────────────
# Razón: centralizar el schema evita errores si cambia el nombre.
# Todos los modelos de Gamma usan schema='gamma' para separar del schema public
# de PostgreSQL y facilitar control de permisos por schema.
class Base(DeclarativeBase):
    pass


SCHEMA = "gamma"


# ── Enumeraciones controladas ─────────────────────────────────────────────────
# Razón: usar Enum en lugar de VARCHAR libre previene datos inválidos a nivel
# de base de datos, no solo de aplicación. PostgreSQL valida el Enum
# en el INSERT/UPDATE, independientemente del ORM.

class GeneroEnum(str, enum.Enum):
    """Géneros conforme a estándar HL7 FHIR administrative-gender."""
    MASCULINO   = "masculino"
    FEMENINO    = "femenino"
    OTRO        = "otro"
    DESCONOCIDO = "desconocido"


class TipoSangreEnum(str, enum.Enum):
    """Grupos sanguíneos ABO + factor Rh."""
    A_POS  = "A+"
    A_NEG  = "A-"
    B_POS  = "B+"
    B_NEG  = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS  = "O+"
    O_NEG  = "O-"
    DESCONOCIDO = "desconocido"


class EstadoPacienteEnum(str, enum.Enum):
    """Estado administrativo del registro del paciente."""
    ACTIVO    = "activo"
    INACTIVO  = "inactivo"   # Dado de baja administrativamente
    FALLECIDO = "fallecido"


class EstadoExpedienteEnum(str, enum.Enum):
    """Estado del expediente médico."""
    ABIERTO  = "abierto"
    CERRADO  = "cerrado"    # Alta definitiva
    URGENCIA = "urgencia"   # Registro parcial en modo emergencia


class ModoRegistroEnum(str, enum.Enum):
    """Modo en que se registró la visita clínica."""
    NORMAL   = "normal"
    URGENCIA = "urgencia"   # Campos obligatorios relajados


class ResultadoAuditoriaEnum(str, enum.Enum):
    """Resultado de la acción auditada."""
    EXITO  = "exito"
    FALLO  = "fallo"
    DENEGADO = "denegado"   # Intento de acceso sin permisos


# ── Modelo: usuarios (referencia — propietario M7) ────────────────────────────
# Razón: M1 referencia la tabla usuarios de M7 como FK.
# Se define aquí como modelo mínimo para que SQLAlchemy resuelva las relaciones
# sin importar el módulo completo de M7 en este archivo.
# En el proyecto real, se importa desde app.models.usuario.
class Usuario(Base):
    """
    Referencia mínima al modelo Usuario de M7.
    En el proyecto real: from app.models.usuario import Usuario
    """
    __tablename__ = "usuarios"
    __table_args__ = (
        {"schema": SCHEMA},
    )

    # PK: UUID generado por PostgreSQL con gen_random_uuid()
    # Razón: no usar SERIAL para que los IDs sean opacos e impredecibles.
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        comment="Identificador único del usuario. UUID v4 opaco.",
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Nombre de usuario para login. Único en el sistema.",
    )

    rol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Rol del usuario: recepcionista, enfermera, medico, admin_ti, director.",
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="False = cuenta desactivada. No puede iniciar sesión.",
    )

    # Relaciones inversas (back_populates)
    pacientes_registrados:   Mapped[list["Paciente"]]       = relationship(back_populates="creador")
    visitas_registradas:     Mapped[list["VisitaClinica"]]  = relationship(back_populates="registrador", foreign_keys="VisitaClinica.registrado_por")
    acciones_auditoria:      Mapped[list["AuditoriaM1"]]    = relationship(back_populates="usuario")


# ── Modelo: pacientes ─────────────────────────────────────────────────────────
class Paciente(Base):
    """
    Datos de identificación personal del paciente.

    Decisiones de diseño:
    - cedula tiene UNIQUE constraint: evita duplicados a nivel de BD,
      no solo de aplicación. Es el campo de búsqueda principal en M1.
    - nombre_completo como campo único: en hospitales panameños el nombre
      completo es un campo de texto libre. Separarlo en nombre/apellido
      añade complejidad sin beneficio operacional claro en este contexto.
    - contacto_emergencia y telefono_emergencia separados de telefono del paciente:
      son datos de personas distintas con roles distintos.
    - estado como Enum controlado: evita valores libres como "dado de baja",
      "muerto", etc. que rompen queries de filtrado.
    - created_at con server_default: el timestamp lo pone PostgreSQL,
      no la aplicación. Esto elimina desfases por zona horaria del cliente.
    """
    __tablename__ = "pacientes"
    __table_args__ = (
        # UNIQUE en cédula a nivel de BD (refuerza la validación de la app)
        UniqueConstraint("cedula", name="uq_pacientes_cedula"),
        # CHECK: cédula no puede ser string vacío
        CheckConstraint("length(trim(cedula)) > 0", name="ck_pacientes_cedula_nonempty"),
        # CHECK: nombre no puede ser string vacío
        CheckConstraint("length(trim(nombre_completo)) > 2", name="ck_pacientes_nombre_min"),
        # CHECK: fecha de nacimiento debe ser en el pasado
        CheckConstraint("fecha_nacimiento < CURRENT_DATE", name="ck_pacientes_fecha_nacimiento"),
        # Índice en cedula: búsqueda más frecuente del módulo M1
        Index("idx_pacientes_cedula", "cedula"),
        # Índice en nombre para búsqueda por nombre (trigram en producción)
        Index("idx_pacientes_nombre", "nombre_completo"),
        # Índice en estado para filtrar pacientes activos
        Index("idx_pacientes_estado", "estado"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        comment="PK: UUID v4. Opaco, no inferible por terceros.",
    )

    # ── Datos de identificación ───────────────────────────────────────────
    cedula: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="N° de cédula o ID del paciente. UNIQUE. Clave de búsqueda principal.",
    )

    nombre_completo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre completo del paciente. Mínimo 3 caracteres.",
    )

    fecha_nacimiento: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        comment="Fecha de nacimiento. Debe ser anterior a la fecha actual.",
    )

    genero: Mapped[GeneroEnum] = mapped_column(
        Enum(GeneroEnum, schema=SCHEMA, name="genero_enum"),
        nullable=False,
        comment="Género conforme a HL7 FHIR administrative-gender.",
    )

    nacionalidad: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="panameña",
        comment="Nacionalidad del paciente.",
    )

    # ── Datos de contacto ─────────────────────────────────────────────────
    direccion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Dirección de residencia. Nullable: puede faltar en urgencias.",
    )

    telefono: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Teléfono del paciente. Nullable: puede no tener.",
    )

    contacto_emergencia: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Nombre del contacto de emergencia.",
    )

    telefono_emergencia: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Teléfono del contacto de emergencia.",
    )

    # ── Estado y auditoría ────────────────────────────────────────────────
    estado: Mapped[EstadoPacienteEnum] = mapped_column(
        Enum(EstadoPacienteEnum, schema=SCHEMA, name="estado_paciente_enum"),
        nullable=False,
        default=EstadoPacienteEnum.ACTIVO,
        server_default="activo",
        comment="Estado administrativo del registro.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp de creación. Generado por PostgreSQL (no por la app).",
    )

    # FK a usuarios: quién registró este paciente
    # ON DELETE RESTRICT: no se puede eliminar un usuario que registró pacientes
    creado_por: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT", name="fk_pacientes_creado_por"),
        nullable=False,
        comment="FK al usuario que registró el paciente. Trazabilidad de auditoría.",
    )

    # ── Relaciones ORM ────────────────────────────────────────────────────
    creador:    Mapped["Usuario"]           = relationship(back_populates="pacientes_registrados", foreign_keys=[creado_por])
    expediente: Mapped["ExpedienteMedico"]  = relationship(back_populates="paciente", uselist=False)


# ── Modelo: expedientes_medicos ───────────────────────────────────────────────
class ExpedienteMedico(Base):
    """
    Expediente médico: contenedor raíz del historial clínico del paciente.

    Decisiones de diseño:
    - Relación 1:1 con Paciente reforzada con UNIQUE en id_paciente.
      Un paciente tiene exactamente un expediente activo.
    - nro_expediente generado por la aplicación con formato hospitalario
      (ej: EXP-2024-000001). UNIQUE en BD para prevenir duplicados.
    - Separado de Paciente para seguir SRP: pacientes tiene datos de identidad,
      expedientes tiene datos clínicos y ciclo de vida del historial.
    """
    __tablename__ = "expedientes_medicos"
    __table_args__ = (
        # UNIQUE en id_paciente: garantiza cardinalidad 1:1 con pacientes
        UniqueConstraint("id_paciente", name="uq_expedientes_paciente"),
        # UNIQUE en nro_expediente: número hospitalario único
        UniqueConstraint("nro_expediente", name="uq_expedientes_nro"),
        # CHECK: nro_expediente debe seguir el formato EXP-YYYY-NNNNNN
        CheckConstraint(
            "nro_expediente ~ '^EXP-[0-9]{4}-[0-9]{6}$'",
            name="ck_expedientes_nro_formato",
        ),
        # Índice en nro_expediente: búsqueda más frecuente desde M3
        Index("idx_expedientes_nro_expediente", "nro_expediente"),
        # Índice en id_paciente: join frecuente desde pacientes → expediente
        Index("idx_expedientes_id_paciente", "id_paciente"),
        # Índice en estado: filtrar expedientes activos
        Index("idx_expedientes_estado", "estado"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        comment="PK: UUID v4.",
    )

    nro_expediente: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Número de expediente hospitalario. Formato: EXP-YYYY-NNNNNN. Generado por la app.",
    )

    id_paciente: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.pacientes.id", ondelete="RESTRICT", name="fk_expedientes_paciente"),
        nullable=False,
        comment="FK al paciente. UNIQUE: garantiza relación 1:1.",
    )

    estado: Mapped[EstadoExpedienteEnum] = mapped_column(
        Enum(EstadoExpedienteEnum, schema=SCHEMA, name="estado_expediente_enum"),
        nullable=False,
        default=EstadoExpedienteEnum.ABIERTO,
        server_default="abierto",
        comment="Estado del expediente. 'urgencia' permite campos incompletos.",
    )

    fecha_apertura: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha y hora de apertura del expediente.",
    )

    creado_por: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT", name="fk_expedientes_creado_por"),
        nullable=False,
        comment="FK al usuario (recepcionista) que creó el expediente.",
    )

    # ── Relaciones ORM ────────────────────────────────────────────────────
    paciente:      Mapped["Paciente"]              = relationship(back_populates="expediente")
    datos_medicos: Mapped["DatosMedicosIniciales"] = relationship(back_populates="expediente", uselist=False)
    visitas:       Mapped[list["VisitaClinica"]]   = relationship(back_populates="expediente", order_by="VisitaClinica.fecha_hora_ingreso.desc()")


# ── Modelo: datos_medicos_iniciales ───────────────────────────────────────────
class DatosMedicosIniciales(Base):
    """
    Datos médicos estáticos del paciente: alergias, antecedentes, medicamentos.

    Decisiones de diseño:
    - Separado de expedientes_medicos porque son datos de naturaleza distinta:
      el expediente es el contenedor administrativo, los datos médicos son el
      contenido clínico inicial (relativamente estático a lo largo del tiempo).
    - Campos de tipo TEXT (no VARCHAR) para campos de texto libre médico:
      las alergias, antecedentes y cirugías pueden ser textos largos y no
      tiene sentido limitar su longitud arbitrariamente.
    - alergias_criticas como Boolean separado: permite hacer banner de alerta
      rápido sin parsear el texto de alergias (requisito funcional RF-M3-09).
    - tipo_sangre como Enum: previene valores inválidos. Es dato crítico para
      transfusiones y emergencias.
    - updated_at y actualizado_por: estos datos pueden cambiar con el tiempo
      (nuevo medicamento, nueva alergia detectada). El historial de cambios
      completo vive en la tabla de auditoría.
    - Relación 1:1 con expediente_medico reforzada con UNIQUE en id_expediente.
    """
    __tablename__ = "datos_medicos_iniciales"
    __table_args__ = (
        # UNIQUE en id_expediente: garantiza 1:1 con expedientes_medicos
        UniqueConstraint("id_expediente", name="uq_datos_medicos_expediente"),
        # Índice en id_expediente: acceso directo desde el expediente
        Index("idx_datos_medicos_expediente", "id_expediente"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        comment="PK: UUID v4.",
    )

    id_expediente: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.expedientes_medicos.id", ondelete="RESTRICT", name="fk_datos_medicos_expediente"),
        nullable=False,
        comment="FK al expediente médico. UNIQUE: cardinalidad 1:1.",
    )

    # ── Datos médicos ─────────────────────────────────────────────────────
    tipo_sangre: Mapped[TipoSangreEnum | None] = mapped_column(
        Enum(TipoSangreEnum, schema=SCHEMA, name="tipo_sangre_enum"),
        nullable=True,
        comment="Grupo sanguíneo ABO + Rh. Nullable: puede desconocerse al ingreso.",
    )

    alergias: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción libre de alergias conocidas.",
    )

    alergias_criticas: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="True = muestra banner de alerta crítico al abrir el expediente (RF-M3-09).",
    )

    enfermedades_cronicas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Listado de enfermedades crónicas diagnosticadas.",
    )

    medicamentos_actuales: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Medicamentos que el paciente toma actualmente al momento del registro.",
    )

    antecedentes_familiares: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Antecedentes médicos relevantes de familiares directos.",
    )

    vacunas_aplicadas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Historial de vacunas aplicadas previamente.",
    )

    cirugias_previas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Cirugías previas del paciente con fecha aproximada si se conoce.",
    )

    # ── Auditoría de actualización ────────────────────────────────────────
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
        comment="Timestamp de última actualización de estos datos médicos.",
    )

    actualizado_por: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT", name="fk_datos_medicos_actualizado_por"),
        nullable=True,
        comment="FK al usuario que realizó la última actualización.",
    )

    # ── Relaciones ORM ────────────────────────────────────────────────────
    expediente: Mapped["ExpedienteMedico"] = relationship(back_populates="datos_medicos")


# ── Modelo: visitas_clinicas ──────────────────────────────────────────────────
class VisitaClinica(Base):
    """
    Registro de cada visita/atención del paciente al hospital.

    Decisiones de diseño:
    - Es la tabla de mayor crecimiento del módulo: cada vez que el paciente
      es atendido, se crea una nueva fila. Nunca se actualiza una visita
      existente; se agregan nuevas (append-only para datos clínicos).
    - presion_arterial como VARCHAR: el formato es "120/80 mmHg", no numérico.
      Separarlo en sistólica/diastólica añade complejidad innecesaria en M1;
      puede normalizarse en M2 si los reportes lo requieren.
    - temperatura y saturacion_o2 como Numeric(5,2): precisión médica necesaria.
      Evita errores de redondeo de float. Temperatura en °C (35.5 a 42.0),
      saturación como porcentaje (0.00 a 100.00).
    - CHECK constraints en signos vitales: valores fuera de rango son errores
      de captura, no datos válidos. La BD los rechaza antes de que lleguen
      al historial clínico.
    - modo_registro: distingue el registro normal del modo urgencia donde los
      campos obligatorios están relajados (RF-M1-04).
    - id_medico puede ser NULL en modo urgencia: el médico puede asignarse
      posteriormente. En modo normal es NOT NULL.
    - La restricción de id_medico NOT NULL en modo normal se implementa con
      un CHECK constraint condicional en PostgreSQL.
    """
    __tablename__ = "visitas_clinicas"
    __table_args__ = (
        # CHECK en temperatura: rango fisiológico válido en °C
        CheckConstraint(
            "temperatura IS NULL OR (temperatura >= 30.0 AND temperatura <= 45.0)",
            name="ck_visitas_temperatura_rango",
        ),
        # CHECK en saturación: porcentaje válido
        CheckConstraint(
            "saturacion_o2 IS NULL OR (saturacion_o2 >= 0 AND saturacion_o2 <= 100)",
            name="ck_visitas_saturacion_rango",
        ),
        # CHECK condicional: en modo normal el médico es obligatorio
        CheckConstraint(
            "modo_registro = 'urgencia' OR id_medico IS NOT NULL",
            name="ck_visitas_medico_requerido_modo_normal",
        ),
        # CHECK: motivo de consulta no puede ser vacío
        CheckConstraint(
            "length(trim(motivo_consulta)) > 0",
            name="ck_visitas_motivo_nonempty",
        ),
        # Índice en id_expediente: carga de historial de visitas de un paciente
        Index("idx_visitas_expediente", "id_expediente"),
        # Índice compuesto médico + fecha: agenda del médico, reportes M4
        Index("idx_visitas_medico_fecha", "id_medico", "fecha_hora_ingreso"),
        # Índice en fecha: filtrar por rango de fechas en M3 y M4
        Index("idx_visitas_fecha_ingreso", "fecha_hora_ingreso"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        comment="PK: UUID v4.",
    )

    id_expediente: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.expedientes_medicos.id", ondelete="RESTRICT", name="fk_visitas_expediente"),
        nullable=False,
        comment="FK al expediente médico al que pertenece esta visita.",
    )

    # ── Datos de la visita ────────────────────────────────────────────────
    motivo_consulta: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Motivo principal de la consulta (síntoma principal). Obligatorio.",
    )

    fecha_hora_ingreso: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha y hora de ingreso. Generada por PostgreSQL.",
    )

    # Nullable en modo urgencia (ver CHECK constraint condicional)
    id_medico: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT", name="fk_visitas_medico"),
        nullable=True,
        comment="FK al médico tratante. NOT NULL en modo normal, nullable en urgencia.",
    )

    area_especialidad: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Área o especialidad médica de la visita (p.ej. Medicina General, Cardiología).",
    )

    # ── Signos vitales ────────────────────────────────────────────────────
    presion_arterial: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Presión arterial en formato 'sistólica/diastólica mmHg' (ej: '120/80'). VARCHAR por formato.",
    )

    temperatura: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Temperatura corporal en °C. Rango válido: 30.00–45.00 (CHECK constraint).",
    )

    saturacion_o2: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Saturación de oxígeno en porcentaje (0–100). Numeric(5,2) para precisión médica.",
    )

    # ── Evaluación clínica ────────────────────────────────────────────────
    diagnostico_preliminar: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Diagnóstico preliminar de la visita. Nullable: puede completarse después.",
    )

    plan_tratamiento: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Plan de tratamiento inicial. Nullable en modo urgencia.",
    )

    # ── Control operativo ─────────────────────────────────────────────────
    modo_registro: Mapped[ModoRegistroEnum] = mapped_column(
        Enum(ModoRegistroEnum, schema=SCHEMA, name="modo_registro_enum"),
        nullable=False,
        default=ModoRegistroEnum.NORMAL,
        server_default="normal",
        comment="'urgencia' relaja validaciones de campos obligatorios (RF-M1-04).",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp de creación del registro de visita.",
    )

    registrado_por: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="RESTRICT", name="fk_visitas_registrado_por"),
        nullable=False,
        comment="FK al usuario que registró la visita (recepcionista o enfermera).",
    )

    # ── Relaciones ORM ────────────────────────────────────────────────────
    expediente:   Mapped["ExpedienteMedico"] = relationship(back_populates="visitas")
    medico:       Mapped["Usuario | None"]   = relationship(foreign_keys=[id_medico])
    registrador:  Mapped["Usuario"]          = relationship(back_populates="visitas_registradas", foreign_keys=[registrado_por])


# ── Modelo: auditoria_m1 ──────────────────────────────────────────────────────
class AuditoriaM1(Base):
    """
    Log de auditoría inmutable de todas las acciones del módulo M1.

    Decisiones de diseño de seguridad críticas:
    - SOLO INSERT: esta tabla nunca recibe UPDATE ni DELETE.
      Se garantiza a nivel de permisos de BD: el usuario de la app solo tiene
      privilegio INSERT sobre esta tabla (no UPDATE, no DELETE).
    - id_entidad como UUID nullable: referencia el ID del registro afectado
      (id del paciente, id del expediente) sin FK formal, para preservar
      el log incluso si la entidad es eliminada (aunque no puede serlo
      con ON DELETE RESTRICT, el log debe sobrevivir a cualquier cambio).
    - rol_usuario desnormalizado (string, no FK a roles): el log debe ser
      autocontenido. Si el rol del usuario cambia en el futuro, el log
      debe preservar el rol que tenía en el momento de la acción.
    - ip_origen: requerido por ISO 27799 para trazabilidad de accesos.
    - resultado como Enum: exito, fallo, denegado. Permite filtrar intentos
      de acceso no autorizados rápidamente.
    - Sin updated_at, sin soft-delete: la tabla de auditoría es inmutable.
    """
    __tablename__ = "auditoria_m1"
    __table_args__ = (
        # Índice compuesto: consultas de auditoría por usuario + rango de fechas
        Index("idx_auditoria_m1_usuario_ts", "id_usuario", "timestamp_accion"),
        # Índice en entidad: rastrear todas las acciones sobre un registro
        Index("idx_auditoria_m1_entidad", "entidad_afectada", "id_entidad"),
        # Índice en resultado: filtrar accesos denegados o fallos
        Index("idx_auditoria_m1_resultado", "resultado"),
        # Índice en timestamp solo: consultas por rango de fechas globales
        Index("idx_auditoria_m1_timestamp", "timestamp_accion"),
        {"schema": SCHEMA},
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
        comment="PK: UUID v4. Inmutable.",
    )

    # FK con nullable=True: el log debe persistir incluso si el usuario
    # es desactivado. SET NULL en este caso específico es aceptable
    # porque preservamos el log y en rol_usuario queda el rol histórico.
    id_usuario: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{SCHEMA}.usuarios.id", ondelete="SET NULL", name="fk_auditoria_m1_usuario"),
        nullable=True,
        comment="FK al usuario que realizó la acción. SET NULL si el usuario es eliminado.",
    )

    # Desnormalizado: preserva el rol en el momento de la acción
    rol_usuario: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Rol del usuario en el momento de la acción. Desnormalizado para preservar historial.",
    )

    accion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Acción realizada. Ej: CREAR_PACIENTE, CREAR_EXPEDIENTE, REGISTRAR_VISITA.",
    )

    entidad_afectada: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre de la entidad/tabla afectada. Ej: pacientes, expedientes_medicos.",
    )

    # Sin FK formal: el log debe sobrevivir a cambios en la entidad referenciada
    id_entidad: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="ID del registro afectado. Sin FK formal para preservar el log.",
    )

    timestamp_accion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp exacto de la acción. Generado por PostgreSQL.",
    )

    ip_origen: Mapped[str] = mapped_column(
        String(45),    # Hasta 45 chars para IPv6 completo
        nullable=False,
        comment="IP del cliente que realizó la acción. Requerido por ISO 27799.",
    )

    resultado: Mapped[ResultadoAuditoriaEnum] = mapped_column(
        Enum(ResultadoAuditoriaEnum, schema=SCHEMA, name="resultado_auditoria_enum"),
        nullable=False,
        comment="Resultado de la acción: exito, fallo, denegado.",
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción detallada opcional. Útil en casos de fallo para el mensaje de error.",
    )

    # ── Relación ORM ──────────────────────────────────────────────────────
    usuario: Mapped["Usuario | None"] = relationship(back_populates="acciones_auditoria")
