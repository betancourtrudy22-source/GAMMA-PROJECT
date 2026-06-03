-- =============================================================================
-- Gamma — Módulo M1: Registro de Pacientes
-- Migración DDL para PostgreSQL
-- Generado desde models_m1.py — ejecutar en orden.
-- =============================================================================

-- Crear schema dedicado para Gamma
-- Razón: separar del schema public permite control de permisos por schema.
CREATE SCHEMA IF NOT EXISTS gamma;

-- =============================================================================
-- 1. TIPOS ENUM
-- Razón: PostgreSQL valida los Enums en INSERT/UPDATE independientemente
-- de la aplicación, proporcionando una segunda línea de defensa.
-- =============================================================================

CREATE TYPE gamma.genero_enum AS ENUM (
    'masculino', 'femenino', 'otro', 'desconocido'
);

CREATE TYPE gamma.tipo_sangre_enum AS ENUM (
    'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'desconocido'
);

CREATE TYPE gamma.estado_paciente_enum AS ENUM (
    'activo', 'inactivo', 'fallecido'
);

CREATE TYPE gamma.estado_expediente_enum AS ENUM (
    'abierto', 'cerrado', 'urgencia'
);

CREATE TYPE gamma.modo_registro_enum AS ENUM (
    'normal', 'urgencia'
);

CREATE TYPE gamma.resultado_auditoria_enum AS ENUM (
    'exito', 'fallo', 'denegado'
);

-- =============================================================================
-- 2. TABLA: usuarios (referenciada por M1, propietaria de M7)
-- Se crea aquí con columnas mínimas para que las FK de M1 resuelvan.
-- M7 añadirá las columnas adicionales en su propia migración.
-- =============================================================================

CREATE TABLE IF NOT EXISTS gamma.usuarios (
    id          UUID        NOT NULL DEFAULT gen_random_uuid(),
    username    VARCHAR(100) NOT NULL,
    rol         VARCHAR(50)  NOT NULL,
    activo      BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT pk_usuarios PRIMARY KEY (id),
    CONSTRAINT uq_usuarios_username UNIQUE (username)
);

COMMENT ON TABLE  gamma.usuarios             IS 'Usuarios del sistema Gamma. Propietario: M7.';
COMMENT ON COLUMN gamma.usuarios.id          IS 'PK: UUID v4. Opaco e impredecible.';
COMMENT ON COLUMN gamma.usuarios.username    IS 'Nombre de usuario para login. Único.';
COMMENT ON COLUMN gamma.usuarios.rol         IS 'Rol: recepcionista, enfermera, medico, admin_ti, director.';
COMMENT ON COLUMN gamma.usuarios.activo      IS 'False = cuenta desactivada. No puede autenticarse.';

-- =============================================================================
-- 3. TABLA: pacientes
-- =============================================================================

CREATE TABLE gamma.pacientes (
    id                   UUID                     NOT NULL DEFAULT gen_random_uuid(),
    cedula               VARCHAR(20)              NOT NULL,
    nombre_completo      VARCHAR(200)             NOT NULL,
    fecha_nacimiento     DATE                     NOT NULL,
    genero               gamma.genero_enum        NOT NULL,
    nacionalidad         VARCHAR(100)             NOT NULL DEFAULT 'panameña',
    direccion            TEXT,
    telefono             VARCHAR(20),
    contacto_emergencia  VARCHAR(200),
    telefono_emergencia  VARCHAR(20),
    estado               gamma.estado_paciente_enum NOT NULL DEFAULT 'activo',
    created_at           TIMESTAMPTZ              NOT NULL DEFAULT NOW(),
    creado_por           UUID                     NOT NULL,

    -- Clave primaria
    CONSTRAINT pk_pacientes PRIMARY KEY (id),

    -- UNIQUE: cédula es el identificador hospitalario único del paciente
    -- Razón: previene duplicados a nivel de BD, no solo de aplicación.
    CONSTRAINT uq_pacientes_cedula UNIQUE (cedula),

    -- CHECK: la cédula no puede ser un string vacío o de espacios
    CONSTRAINT ck_pacientes_cedula_nonempty
        CHECK (length(trim(cedula)) > 0),

    -- CHECK: nombre mínimo de 3 caracteres
    CONSTRAINT ck_pacientes_nombre_min
        CHECK (length(trim(nombre_completo)) > 2),

    -- CHECK: fecha de nacimiento en el pasado
    -- Razón: dato médico imposible de ser futuro.
    CONSTRAINT ck_pacientes_fecha_nacimiento
        CHECK (fecha_nacimiento < CURRENT_DATE),

    -- FK: quién registró este paciente
    -- ON DELETE RESTRICT: no se puede eliminar un usuario que registró pacientes.
    CONSTRAINT fk_pacientes_creado_por
        FOREIGN KEY (creado_por)
        REFERENCES gamma.usuarios(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

COMMENT ON TABLE  gamma.pacientes                   IS 'Datos de identificación personal del paciente. M1.';
COMMENT ON COLUMN gamma.pacientes.id                IS 'PK UUID v4. Opaco.';
COMMENT ON COLUMN gamma.pacientes.cedula            IS 'Cédula/ID. Clave de búsqueda principal. UNIQUE.';
COMMENT ON COLUMN gamma.pacientes.nombre_completo   IS 'Nombre completo. Mínimo 3 chars.';
COMMENT ON COLUMN gamma.pacientes.fecha_nacimiento  IS 'Fecha de nacimiento. Debe ser en el pasado.';
COMMENT ON COLUMN gamma.pacientes.genero            IS 'Género HL7 FHIR administrative-gender.';
COMMENT ON COLUMN gamma.pacientes.alergias_criticas IS 'True = banner de alerta crítico en M3.';
COMMENT ON COLUMN gamma.pacientes.created_at        IS 'Timestamp PostgreSQL. No depende del reloj de la app.';
COMMENT ON COLUMN gamma.pacientes.creado_por        IS 'FK al usuario (recepcionista) que registró.';

-- Índices de pacientes
-- idx_pacientes_cedula: búsqueda más frecuente de M1 (verificar duplicados)
CREATE INDEX idx_pacientes_cedula  ON gamma.pacientes (cedula);
-- idx_pacientes_nombre: búsqueda por nombre (candidato a índice trigram con pg_trgm)
CREATE INDEX idx_pacientes_nombre  ON gamma.pacientes (nombre_completo);
-- idx_pacientes_estado: filtrar pacientes activos en listas
CREATE INDEX idx_pacientes_estado  ON gamma.pacientes (estado);

-- =============================================================================
-- 4. TABLA: expedientes_medicos
-- =============================================================================

CREATE TABLE gamma.expedientes_medicos (
    id              UUID                        NOT NULL DEFAULT gen_random_uuid(),
    nro_expediente  VARCHAR(20)                 NOT NULL,
    id_paciente     UUID                        NOT NULL,
    estado          gamma.estado_expediente_enum NOT NULL DEFAULT 'abierto',
    fecha_apertura  TIMESTAMPTZ                 NOT NULL DEFAULT NOW(),
    creado_por      UUID                        NOT NULL,

    CONSTRAINT pk_expedientes_medicos PRIMARY KEY (id),

    -- UNIQUE en id_paciente: refuerza cardinalidad 1:1 con pacientes
    -- Razón: un paciente tiene exactamente un expediente activo.
    CONSTRAINT uq_expedientes_paciente UNIQUE (id_paciente),

    -- UNIQUE en nro_expediente: número hospitalario único
    CONSTRAINT uq_expedientes_nro UNIQUE (nro_expediente),

    -- CHECK: formato del número de expediente EXP-YYYY-NNNNNN
    -- Razón: garantiza consistencia del identificador hospitalario.
    CONSTRAINT ck_expedientes_nro_formato
        CHECK (nro_expediente ~ '^EXP-[0-9]{4}-[0-9]{6}$'),

    -- FK al paciente con RESTRICT: preserva integridad referencial
    CONSTRAINT fk_expedientes_paciente
        FOREIGN KEY (id_paciente)
        REFERENCES gamma.pacientes(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- FK al usuario creador
    CONSTRAINT fk_expedientes_creado_por
        FOREIGN KEY (creado_por)
        REFERENCES gamma.usuarios(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

COMMENT ON TABLE  gamma.expedientes_medicos               IS 'Expediente médico: contenedor raíz del historial. M1.';
COMMENT ON COLUMN gamma.expedientes_medicos.nro_expediente IS 'Número hospitalario. Formato: EXP-YYYY-NNNNNN. UNIQUE.';
COMMENT ON COLUMN gamma.expedientes_medicos.id_paciente    IS 'FK al paciente. UNIQUE: cardinalidad 1:1 garantizada.';

-- Índices de expedientes
-- Búsqueda por número de expediente desde M3
CREATE INDEX idx_expedientes_nro_expediente ON gamma.expedientes_medicos (nro_expediente);
-- Join frecuente paciente → expediente
CREATE INDEX idx_expedientes_id_paciente    ON gamma.expedientes_medicos (id_paciente);
-- Filtrar por estado
CREATE INDEX idx_expedientes_estado         ON gamma.expedientes_medicos (estado);

-- =============================================================================
-- 5. TABLA: datos_medicos_iniciales
-- =============================================================================

CREATE TABLE gamma.datos_medicos_iniciales (
    id                     UUID                    NOT NULL DEFAULT gen_random_uuid(),
    id_expediente          UUID                    NOT NULL,
    tipo_sangre            gamma.tipo_sangre_enum,
    alergias               TEXT,
    alergias_criticas      BOOLEAN                 NOT NULL DEFAULT FALSE,
    enfermedades_cronicas  TEXT,
    medicamentos_actuales  TEXT,
    antecedentes_familiares TEXT,
    vacunas_aplicadas      TEXT,
    cirugias_previas       TEXT,
    updated_at             TIMESTAMPTZ,
    actualizado_por        UUID,

    CONSTRAINT pk_datos_medicos_iniciales PRIMARY KEY (id),

    -- UNIQUE: garantiza relación 1:1 con expedientes_medicos
    CONSTRAINT uq_datos_medicos_expediente UNIQUE (id_expediente),

    CONSTRAINT fk_datos_medicos_expediente
        FOREIGN KEY (id_expediente)
        REFERENCES gamma.expedientes_medicos(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_datos_medicos_actualizado_por
        FOREIGN KEY (actualizado_por)
        REFERENCES gamma.usuarios(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

COMMENT ON TABLE  gamma.datos_medicos_iniciales                  IS 'Datos médicos estáticos del paciente. Separados del expediente por SRP.';
COMMENT ON COLUMN gamma.datos_medicos_iniciales.alergias_criticas IS 'True = muestra banner de alerta al abrir expediente (RF-M3-09).';
COMMENT ON COLUMN gamma.datos_medicos_iniciales.tipo_sangre       IS 'Nullable: puede desconocerse al ingreso.';

CREATE INDEX idx_datos_medicos_expediente ON gamma.datos_medicos_iniciales (id_expediente);

-- =============================================================================
-- 6. TABLA: visitas_clinicas
-- =============================================================================

CREATE TABLE gamma.visitas_clinicas (
    id                    UUID                     NOT NULL DEFAULT gen_random_uuid(),
    id_expediente         UUID                     NOT NULL,
    motivo_consulta       VARCHAR(500)             NOT NULL,
    fecha_hora_ingreso    TIMESTAMPTZ              NOT NULL DEFAULT NOW(),
    id_medico             UUID,
    area_especialidad     VARCHAR(100),
    presion_arterial      VARCHAR(20),
    temperatura           NUMERIC(5, 2),
    saturacion_o2         NUMERIC(5, 2),
    diagnostico_preliminar TEXT,
    plan_tratamiento      TEXT,
    modo_registro         gamma.modo_registro_enum NOT NULL DEFAULT 'normal',
    created_at            TIMESTAMPTZ              NOT NULL DEFAULT NOW(),
    registrado_por        UUID                     NOT NULL,

    CONSTRAINT pk_visitas_clinicas PRIMARY KEY (id),

    -- CHECK: temperatura en rango fisiológico válido (°C)
    -- Razón: valores fuera de rango son errores de captura que la BD rechaza.
    CONSTRAINT ck_visitas_temperatura_rango
        CHECK (temperatura IS NULL OR (temperatura >= 30.0 AND temperatura <= 45.0)),

    -- CHECK: saturación de O2 en porcentaje válido
    CONSTRAINT ck_visitas_saturacion_rango
        CHECK (saturacion_o2 IS NULL OR (saturacion_o2 >= 0 AND saturacion_o2 <= 100)),

    -- CHECK condicional: en modo normal el médico es obligatorio
    -- Razón: implementa RF-M1-04 (modo urgencia relaja validaciones).
    CONSTRAINT ck_visitas_medico_requerido_modo_normal
        CHECK (modo_registro = 'urgencia' OR id_medico IS NOT NULL),

    -- CHECK: motivo de consulta no puede ser vacío
    CONSTRAINT ck_visitas_motivo_nonempty
        CHECK (length(trim(motivo_consulta)) > 0),

    CONSTRAINT fk_visitas_expediente
        FOREIGN KEY (id_expediente)
        REFERENCES gamma.expedientes_medicos(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_visitas_medico
        FOREIGN KEY (id_medico)
        REFERENCES gamma.usuarios(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_visitas_registrado_por
        FOREIGN KEY (registrado_por)
        REFERENCES gamma.usuarios(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

COMMENT ON TABLE  gamma.visitas_clinicas                  IS 'Registro append-only de visitas clínicas. Cada atención genera una fila nueva.';
COMMENT ON COLUMN gamma.visitas_clinicas.temperatura      IS 'Temperatura en °C. Numeric(5,2) para precisión médica. Rango: 30.00-45.00.';
COMMENT ON COLUMN gamma.visitas_clinicas.saturacion_o2    IS 'Saturación O2 en %. Rango: 0-100.';
COMMENT ON COLUMN gamma.visitas_clinicas.presion_arterial IS 'Formato: sistólica/diastólica mmHg. VARCHAR por ser texto libre.';
COMMENT ON COLUMN gamma.visitas_clinicas.modo_registro    IS 'urgencia = relaja campos obligatorios. Normal = médico requerido.';

-- Índice en id_expediente: carga del historial de visitas de un paciente
CREATE INDEX idx_visitas_expediente   ON gamma.visitas_clinicas (id_expediente);
-- Índice compuesto médico+fecha: agenda del médico, reportes M4
CREATE INDEX idx_visitas_medico_fecha ON gamma.visitas_clinicas (id_medico, fecha_hora_ingreso);
-- Índice en fecha: filtrar por rango de fechas en M3 y M4
CREATE INDEX idx_visitas_fecha_ingreso ON gamma.visitas_clinicas (fecha_hora_ingreso);

-- =============================================================================
-- 7. TABLA: auditoria_m1
-- SEGURIDAD: revocar UPDATE y DELETE de esta tabla al usuario de la aplicación
-- =============================================================================

CREATE TABLE gamma.auditoria_m1 (
    id               UUID                          NOT NULL DEFAULT gen_random_uuid(),
    id_usuario       UUID,
    rol_usuario      VARCHAR(50)                   NOT NULL,
    accion           VARCHAR(100)                  NOT NULL,
    entidad_afectada VARCHAR(100)                  NOT NULL,
    id_entidad       UUID,
    timestamp_accion TIMESTAMPTZ                   NOT NULL DEFAULT NOW(),
    ip_origen        VARCHAR(45)                   NOT NULL,
    resultado        gamma.resultado_auditoria_enum NOT NULL,
    descripcion      TEXT,

    CONSTRAINT pk_auditoria_m1 PRIMARY KEY (id),

    -- SET NULL: preserva el log si el usuario es desactivado/eliminado
    -- Razón: el log de auditoría debe sobrevivir a cambios en usuarios.
    --        rol_usuario desnormalizado preserva el contexto histórico.
    CONSTRAINT fk_auditoria_m1_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES gamma.usuarios(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

COMMENT ON TABLE  gamma.auditoria_m1               IS 'Log de auditoría INMUTABLE de M1. Solo INSERT. ISO 27799.';
COMMENT ON COLUMN gamma.auditoria_m1.rol_usuario   IS 'Desnormalizado: preserva el rol en el momento de la acción.';
COMMENT ON COLUMN gamma.auditoria_m1.id_entidad    IS 'Sin FK formal: el log persiste aunque la entidad cambie.';
COMMENT ON COLUMN gamma.auditoria_m1.ip_origen     IS 'IP del cliente. Hasta 45 chars para IPv6. Requerido ISO 27799.';

-- Índices de auditoría
-- Consultas por usuario + rango de fechas (caso más frecuente de auditoría)
CREATE INDEX idx_auditoria_m1_usuario_ts ON gamma.auditoria_m1 (id_usuario, timestamp_accion);
-- Rastrear todas las acciones sobre un registro específico
CREATE INDEX idx_auditoria_m1_entidad    ON gamma.auditoria_m1 (entidad_afectada, id_entidad);
-- Filtrar accesos denegados o fallos de seguridad
CREATE INDEX idx_auditoria_m1_resultado  ON gamma.auditoria_m1 (resultado);
-- Consultas por rango de fechas globales
CREATE INDEX idx_auditoria_m1_timestamp  ON gamma.auditoria_m1 (timestamp_accion);

-- =============================================================================
-- 8. PERMISOS DE BASE DE DATOS (ejecutar como superusuario)
-- El usuario de la aplicación solo tiene los permisos mínimos necesarios.
-- =============================================================================

-- Crear usuario de aplicación (si no existe)
-- CREATE USER gamma_app WITH PASSWORD 'usar_variable_de_entorno';

-- Permisos de schema
GRANT USAGE ON SCHEMA gamma TO gamma_app;

-- Permisos por tabla (principio de mínimo privilegio)
GRANT SELECT, INSERT, UPDATE ON gamma.pacientes             TO gamma_app;
GRANT SELECT, INSERT, UPDATE ON gamma.expedientes_medicos   TO gamma_app;
GRANT SELECT, INSERT, UPDATE ON gamma.datos_medicos_iniciales TO gamma_app;
GRANT SELECT, INSERT, UPDATE ON gamma.visitas_clinicas      TO gamma_app;
GRANT SELECT               ON gamma.usuarios                TO gamma_app;

-- CRÍTICO: la tabla de auditoría solo recibe INSERT desde la aplicación
-- No UPDATE, no DELETE — garantiza inmutabilidad del log.
GRANT INSERT, SELECT ON gamma.auditoria_m1 TO gamma_app;

-- Permisos para usar los tipos ENUM
GRANT USAGE ON TYPE gamma.genero_enum              TO gamma_app;
GRANT USAGE ON TYPE gamma.tipo_sangre_enum         TO gamma_app;
GRANT USAGE ON TYPE gamma.estado_paciente_enum     TO gamma_app;
GRANT USAGE ON TYPE gamma.estado_expediente_enum   TO gamma_app;
GRANT USAGE ON TYPE gamma.modo_registro_enum       TO gamma_app;
GRANT USAGE ON TYPE gamma.resultado_auditoria_enum TO gamma_app;

-- =============================================================================
-- 9. ÍNDICE TRIGRAM OPCIONAL (requiere extensión pg_trgm)
-- Mejora búsquedas por nombre parcial ("Juan P." → "Juan Pérez")
-- Activar solo si se instala la extensión en el servidor.
-- =============================================================================

-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX idx_pacientes_nombre_trgm
--     ON gamma.pacientes USING GIN (nombre_completo gin_trgm_ops);

