"""
Proyecto GAMMA - Controlador de Pacientes y Expedientes
Módulo M1: Registro de Pacientes
Módulo M2: Actualización de Expedientes
Módulo M3: Acceso y Consulta

Permisos aplicados por rol según Plan Maestro de Rescate (Ley 81 / ISO 27799):
  - ADMIN          : gestión completa de usuarios y pacientes
  - MEDICO         : registro de pacientes, visitas, diagnósticos, cierre
  - ENF_TRIAGE     : registro de pacientes, signos vitales, motivo de consulta
  - ENF_ASISTENCIAL: ver indicaciones, registrar notas de enfermería
  - DIRECTOR       : solo lectura (consulta y reportes)
  - RECEPCION      : registro de paciente (datos básicos), búsqueda
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from src.models.models import (
    Paciente, VisitaMedica, NotaMedica,
    AuditoriaLog, UserRole, VisitStatus
)
from src.models.database import db_manager
from src.controllers.auth_controller import auth_controller

# ── Grupos de roles reutilizables ────────────────────────────────────────────
ROLES_REGISTRO_PACIENTE = [
    UserRole.MEDICO, UserRole.ENF_TRIAGE, UserRole.ADMIN, UserRole.RECEPCION
]
ROLES_EDITAR_PACIENTE = [
    UserRole.MEDICO, UserRole.ENF_TRIAGE, UserRole.ADMIN
]
ROLES_VER_EXPEDIENTE = [
    UserRole.MEDICO, UserRole.ENF_TRIAGE, UserRole.ENF_ASISTENCIAL,
    UserRole.ADMIN, UserRole.RECEPCION, UserRole.DIRECTOR
]
ROLES_REGISTRO_VISITA = [
    UserRole.MEDICO, UserRole.ENF_TRIAGE
]
ROLES_DIAGNOSTICO = [
    UserRole.MEDICO  # Solo médicos crean diagnósticos (ISO 27799 mínimo privilegio)
]
ROLES_NOTAS_ENFERMERIA = [
    UserRole.MEDICO, UserRole.ENF_TRIAGE, UserRole.ENF_ASISTENCIAL
]
ROLES_CERRAR_VISITA = [
    UserRole.MEDICO
]


class PacienteController:
    """
    Controlador de lógica de negocio para pacientes y expedientes médicos.
    Aplica control de acceso por rol en cada operación (Ley 81 / ISO 27799).
    """

    # ------------------------------------------------------------------
    # M1 - REGISTRO DE PACIENTES
    # ------------------------------------------------------------------

    def registrar_paciente(self, datos: dict) -> tuple[bool, str, Optional[Paciente]]:
        """
        M1: Registra un nuevo paciente en el sistema.
        Roles: Admin, Médico, Enfermero Triage, Recepción.
        """
        if not auth_controller.has_permission(ROLES_REGISTRO_PACIENTE):
            return False, "Sin permisos para registrar pacientes.", None

        es_valido, mensaje = self._validar_datos_paciente(datos)
        if not es_valido:
            return False, mensaje, None

        session: Session = db_manager.get_session()
        try:
            existente = (
                session.query(Paciente)
                .filter(Paciente.cedula == datos["cedula"])
                .first()
            )
            if existente:
                return (
                    False,
                    f"Ya existe un paciente con cédula {datos['cedula']}.",
                    None,
                )

            paciente = Paciente(
                cedula=datos["cedula"].strip(),
                nombre=datos["nombre"].strip(),
                apellido=datos["apellido"].strip(),
                fecha_nacimiento=datos["fecha_nacimiento"],
                genero=datos["genero"],
                nacionalidad=datos.get("nacionalidad", ""),
                direccion=datos.get("direccion", ""),
                telefono=datos.get("telefono", ""),
                contacto_emergencia=datos.get("contacto_emergencia", ""),
                telefono_emergencia=datos.get("telefono_emergencia", ""),
                tipo_sangre=datos.get("tipo_sangre"),
                alergias=datos.get("alergias", ""),
                enfermedades_cronicas=datos.get("enfermedades_cronicas", ""),
                medicamentos_actuales=datos.get("medicamentos_actuales", ""),
                antecedentes_familiares=datos.get("antecedentes_familiares", ""),
                vacunas_aplicadas=datos.get("vacunas_aplicadas", ""),
                cirugias_previas=datos.get("cirugias_previas", ""),
            )

            session.add(paciente)
            self._registrar_auditoria(
                session, "PACIENTE_REGISTRADO",
                "pacientes", detalle=f"Cédula: {datos['cedula']}"
            )
            session.commit()
            session.refresh(paciente)
            return True, "Paciente registrado exitosamente.", paciente

        except Exception as exc:
            session.rollback()
            return False, f"Error al registrar paciente: {exc}", None
        finally:
            session.close()

    def actualizar_paciente(
        self, paciente_id: int, datos: dict
    ) -> tuple[bool, str]:
        """
        M1/M2: Actualiza los datos de un paciente existente.
        Roles: Admin, Médico, Enfermero Triage.
        """
        if not auth_controller.has_permission(ROLES_EDITAR_PACIENTE):
            return False, "Sin permisos para actualizar pacientes."

        session: Session = db_manager.get_session()
        try:
            paciente = session.get(Paciente, paciente_id)
            if paciente is None:
                return False, "Paciente no encontrado."

            campos_actualizables = [
                "nombre", "apellido", "direccion", "telefono",
                "contacto_emergencia", "telefono_emergencia",
                "alergias", "enfermedades_cronicas",
                "medicamentos_actuales", "antecedentes_familiares",
                "vacunas_aplicadas", "cirugias_previas",
                "tipo_sangre", "nacionalidad",
            ]
            for campo in campos_actualizables:
                if campo in datos:
                    setattr(paciente, campo, datos[campo])

            paciente.actualizado_en = datetime.utcnow()
            self._registrar_auditoria(
                session, "PACIENTE_ACTUALIZADO",
                "pacientes", paciente_id
            )
            session.commit()
            return True, "Paciente actualizado exitosamente."

        except Exception as exc:
            session.rollback()
            return False, f"Error al actualizar: {exc}"
        finally:
            session.close()

    # ------------------------------------------------------------------
    # M3 - CONSULTA DE EXPEDIENTES
    # ------------------------------------------------------------------

    def buscar_pacientes(self, termino: str) -> list[Paciente]:
        """
        M3: Busca pacientes por cédula, nombre o apellido.
        Roles: Todos los roles tienen acceso (con distintos niveles de detalle).
        """
        if not auth_controller.has_permission(ROLES_VER_EXPEDIENTE):
            return []

        session: Session = db_manager.get_session()
        try:
            termino_like = f"%{termino.strip()}%"
            pacientes = (
                session.query(Paciente)
                .options(joinedload(Paciente.visitas), joinedload(Paciente.citas))
                .filter(
                    Paciente.activo.is_(True),
                    or_(
                        Paciente.cedula.ilike(termino_like),
                        Paciente.nombre.ilike(termino_like),
                        Paciente.apellido.ilike(termino_like),
                    )
                )
                .order_by(Paciente.apellido, Paciente.nombre)
                .limit(50)
                .all()
            )
            session.expunge_all()
            return pacientes
        except Exception:
            return []
        finally:
            session.close()

    def obtener_paciente(self, paciente_id: int) -> Optional[Paciente]:
        """M3: Obtiene un paciente por ID con todas sus visitas."""
        session: Session = db_manager.get_session()
        try:
            paciente = session.get(Paciente, paciente_id)
            if paciente:
                self._registrar_auditoria(
                    session, "EXPEDIENTE_CONSULTADO",
                    "pacientes", paciente_id
                )
                session.commit()
            return paciente
        finally:
            session.close()

    def obtener_todos_pacientes(self) -> list[Paciente]:
        """Retorna todos los pacientes activos del sistema."""
        if not auth_controller.has_permission(ROLES_VER_EXPEDIENTE):
            return []
        session: Session = db_manager.get_session()
        try:
            pacientes = (
                session.query(Paciente)
                .options(joinedload(Paciente.visitas), joinedload(Paciente.citas))
                .filter(Paciente.activo.is_(True))
                .order_by(Paciente.apellido, Paciente.nombre)
                .all()
            )
            session.expunge_all()
            return pacientes
        finally:
            session.close()

    # ------------------------------------------------------------------
    # M2 - GESTIÓN DE VISITAS
    # ------------------------------------------------------------------

    def registrar_visita(
        self, paciente_id: int, datos: dict
    ) -> tuple[bool, str, Optional[VisitaMedica]]:
        """
        M2: Registra una nueva visita médica.
        Roles: Médico (completo), Enfermero Triage (signos vitales + motivo).
        El diagnóstico y plan de tratamiento son exclusivos del Médico.
        """
        if not auth_controller.has_permission(ROLES_REGISTRO_VISITA):
            return False, "Solo médicos y enfermeros de triage pueden registrar visitas.", None

        if not datos.get("motivo_consulta", "").strip():
            return False, "El motivo de consulta es obligatorio.", None

        # Enfermero de triage NO puede escribir diagnóstico ni tratamiento
        rol_actual = auth_controller.current_user.rol
        if rol_actual == UserRole.ENF_TRIAGE:
            datos.pop("diagnostico_preliminar", None)
            datos.pop("diagnostico_final", None)
            datos.pop("plan_tratamiento", None)

        session: Session = db_manager.get_session()
        try:
            paciente = session.get(Paciente, paciente_id)
            if paciente is None:
                return False, "Paciente no encontrado.", None

            visita = VisitaMedica(
                paciente_id=paciente_id,
                medico_id=auth_controller.current_user.id,
                motivo_consulta=datos["motivo_consulta"].strip(),
                area_especialidad=datos.get("area_especialidad", ""),
                presion_arterial=datos.get("presion_arterial"),
                temperatura=datos.get("temperatura"),
                saturacion_oxigeno=datos.get("saturacion_oxigeno"),
                frecuencia_cardiaca=datos.get("frecuencia_cardiaca"),
                peso_kg=datos.get("peso_kg"),
                talla_cm=datos.get("talla_cm"),
                diagnostico_preliminar=datos.get("diagnostico_preliminar", ""),
                plan_tratamiento=datos.get("plan_tratamiento", ""),
                observaciones=datos.get("observaciones", ""),
            )

            session.add(visita)
            self._registrar_auditoria(
                session, "VISITA_REGISTRADA",
                "visitas_medicas", paciente_id
            )
            session.commit()
            session.refresh(visita)
            return True, "Visita registrada exitosamente.", visita

        except Exception as exc:
            session.rollback()
            return False, f"Error al registrar visita: {exc}", None
        finally:
            session.close()

    def agregar_nota(
        self, visita_id: int, contenido: str
    ) -> tuple[bool, str]:
        """
        M2: Agrega una nota clínica a una visita.
        Roles: Médico, Enfermero Triage, Enfermero Asistencial.
        """
        if not auth_controller.has_permission(ROLES_NOTAS_ENFERMERIA):
            return False, "Sin permisos para agregar notas clínicas."

        if not contenido.strip():
            return False, "El contenido de la nota no puede estar vacío."

        session: Session = db_manager.get_session()
        try:
            nota = NotaMedica(
                visita_id=visita_id,
                autor_id=auth_controller.current_user.id,
                contenido=contenido.strip(),
            )
            session.add(nota)
            session.commit()
            return True, "Nota agregada exitosamente."
        except Exception as exc:
            session.rollback()
            return False, f"Error: {exc}"
        finally:
            session.close()

    def cerrar_visita(self, visita_id: int) -> tuple[bool, str]:
        """
        M2: Cierra una visita médica activa.
        Rol exclusivo: Médico.
        """
        if not auth_controller.has_permission(ROLES_CERRAR_VISITA):
            return False, "Solo médicos pueden cerrar visitas."

        session: Session = db_manager.get_session()
        try:
            visita = session.get(VisitaMedica, visita_id)
            if visita is None:
                return False, "Visita no encontrada."
            if visita.estado == VisitStatus.CERRADA:
                return False, "La visita ya está cerrada."

            visita.estado = VisitStatus.CERRADA
            visita.fecha_cierre = datetime.utcnow()
            session.commit()
            return True, "Visita cerrada exitosamente."
        except Exception as exc:
            session.rollback()
            return False, f"Error: {exc}"
        finally:
            session.close()

    def guardar_evaluacion_clinica(
        self, visita_id: int, diagnostico: str, tratamiento: str, observaciones: str
    ) -> tuple[bool, str]:
        """
        M2: Registra o actualiza la evaluación clínica por parte del Médico.
        Aplica control de acceso y auditoría ISO 27799.
        """
        if not auth_controller.has_permission(ROLES_DIAGNOSTICO):
            return False, "Solo médicos pueden registrar diagnósticos y planes de tratamiento."

        if not diagnostico.strip():
            return False, "El diagnóstico es obligatorio."

        session: Session = db_manager.get_session()
        try:
            visita = session.get(VisitaMedica, visita_id)
            if visita is None:
                return False, "Visita no encontrada."
            if visita.estado == VisitStatus.CERRADA:
                return False, "No se puede modificar una visita cerrada."

            visita.diagnostico_preliminar = diagnostico.strip()
            visita.plan_tratamiento = tratamiento.strip()
            visita.observaciones = observaciones.strip()
            visita.actualizado_en = datetime.utcnow()

            self._registrar_auditoria(
                session, "EVALUACION_CLINICA_ACTUALIZADA",
                "visitas_medicas", visita.paciente_id,
                detalle=f"Visita ID: {visita_id}"
            )
            session.commit()
            return True, "Evaluación clínica guardada exitosamente."
        except Exception as exc:
            session.rollback()
            return False, f"Error al guardar la evaluación clínica: {exc}"
        finally:
            session.close()

    # ------------------------------------------------------------------
    # MÉTODOS PRIVADOS
    # ------------------------------------------------------------------

    @staticmethod
    def _validar_datos_paciente(datos: dict) -> tuple[bool, str]:
        """
        Valida los campos obligatorios y formatos del formulario de paciente.
        Métrica M1: 100% campos obligatorios validados.
        """
        import re
        campos_obligatorios = {
            "cedula": "Número de cédula",
            "nombre": "Nombre",
            "apellido": "Apellido",
            "fecha_nacimiento": "Fecha de nacimiento",
            "genero": "Género",
        }
        for campo, etiqueta in campos_obligatorios.items():
            valor = datos.get(campo)
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                return False, f"El campo '{etiqueta}' es obligatorio."

        cedula = datos["cedula"].strip()
        # Formato de cédula panameña: provincia-tomo-asiento (ej. 8-123-456, PE-123-456, 12-456-789)
        patron_cedula = re.compile(r'^(?:[1-9]|1[0-2]|PE|E|N|PI|SB|AV)-\d+-\d+$', re.IGNORECASE)
        if not patron_cedula.match(cedula):
            return False, "La cédula ingresada no tiene un formato panameño válido (ej. 8-123-456 o PE-123-456)."

        telefono = datos.get("telefono", "").strip()
        if telefono:
            # En Panamá los números telefónicos tienen entre 7 y 8 dígitos
            patron_tel = re.compile(r'^\+?(?:507-?)?(?:\d{4}-\d{4}|\d{7,8})$')
            if not patron_tel.match(telefono):
                return False, "El teléfono debe ser numérico y tener entre 7 y 8 dígitos (ej. 6100-0001)."

        if isinstance(datos["fecha_nacimiento"], date):
            if datos["fecha_nacimiento"] > date.today():
                return False, "La fecha de nacimiento no puede ser futura."
            if datos["fecha_nacimiento"].year < 1900:
                return False, "La fecha de nacimiento no puede ser anterior al año 1900."
        else:
            return False, "Formato de fecha de nacimiento inválido."

        return True, ""

    @staticmethod
    def _registrar_auditoria(
        session: Session,
        accion: str,
        tabla: str,
        registro_id: int = None,
        detalle: str = None,
    ) -> None:
        """Registra una acción en la auditoría del sistema (ISO 27799)."""
        if not auth_controller.is_authenticated:
            return
        log = AuditoriaLog(
            usuario_id=auth_controller.current_user.id,
            accion=accion,
            tabla_afectada=tabla,
            registro_id=registro_id,
            detalle=detalle,
        )
        session.add(log)


# Instancia global del controlador
paciente_controller = PacienteController()
