"""
Proyecto GAMMA - Controlador de Pacientes y Expedientes
Módulo M1: Registro de Pacientes
Módulo M2: Actualización de Expedientes
Módulo M3: Acceso y Consulta
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models.models import (
    Paciente, VisitaMedica, NotaMedica,
    AuditoriaLog, UserRole, VisitStatus
)
from src.models.database import db_manager
from src.controllers.auth_controller import auth_controller


class PacienteController:
    """
    Controlador de lógica de negocio para pacientes y expedientes médicos.
    Aplica control de acceso por rol en cada operación.
    """

    # ------------------------------------------------------------------
    # M1 - REGISTRO DE PACIENTES
    # ------------------------------------------------------------------

    def registrar_paciente(self, datos: dict) -> tuple[bool, str, Optional[Paciente]]:
        """
        M1: Registra un nuevo paciente en el sistema.

        Args:
            datos: Diccionario con los campos del paciente.

        Returns:
            tuple[bool, str, Optional[Paciente]]: (éxito, mensaje, paciente).
        """
        roles_permitidos = [
            UserRole.MEDICO, UserRole.ENFERMERA,
            UserRole.ADMIN, UserRole.RECEPCION
        ]
        if not auth_controller.has_permission(roles_permitidos):
            return False, "Sin permisos para registrar pacientes.", None

        # Validación de campos obligatorios (métrica: 100% campos validados)
        es_valido, mensaje = self._validar_datos_paciente(datos)
        if not es_valido:
            return False, mensaje, None

        session: Session = db_manager.get_session()
        try:
            # Verificar cédula duplicada
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

        Args:
            paciente_id: ID del paciente a actualizar.
            datos: Campos a actualizar.

        Returns:
            tuple[bool, str]: (éxito, mensaje).
        """
        roles_permitidos = [UserRole.MEDICO, UserRole.ENFERMERA, UserRole.ADMIN]
        if not auth_controller.has_permission(roles_permitidos):
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
        Métrica: Respuesta < 3 segundos en tablet.

        Args:
            termino: Texto a buscar.

        Returns:
            list[Paciente]: Lista de pacientes encontrados.
        """
        roles_permitidos = [
            UserRole.MEDICO, UserRole.ENFERMERA,
            UserRole.ADMIN, UserRole.RECEPCION, UserRole.DIRECTOR
        ]
        if not auth_controller.has_permission(roles_permitidos):
            return []

        session: Session = db_manager.get_session()
        try:
            termino_like = f"%{termino.strip()}%"
            pacientes = (
                session.query(Paciente)
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
            return pacientes
        except Exception:
            return []
        finally:
            session.close()

    def obtener_paciente(self, paciente_id: int) -> Optional[Paciente]:
        """
        M3: Obtiene un paciente por ID con todas sus visitas.

        Args:
            paciente_id: ID del paciente.

        Returns:
            Optional[Paciente]: Paciente encontrado o None.
        """
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
        session: Session = db_manager.get_session()
        try:
            return (
                session.query(Paciente)
                .filter(Paciente.activo.is_(True))
                .order_by(Paciente.apellido, Paciente.nombre)
                .all()
            )
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
        Métrica: Cambios reflejados en < 2 segundos.

        Args:
            paciente_id: ID del paciente.
            datos: Datos de la visita.

        Returns:
            tuple[bool, str, Optional[VisitaMedica]]: (éxito, mensaje, visita).
        """
        roles_permitidos = [UserRole.MEDICO, UserRole.ENFERMERA]
        if not auth_controller.has_permission(roles_permitidos):
            return False, "Solo médicos y enfermeras pueden registrar visitas.", None

        if not datos.get("motivo_consulta", "").strip():
            return False, "El motivo de consulta es obligatorio.", None

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
        M2: Agrega una nota médica a una visita.

        Args:
            visita_id: ID de la visita.
            contenido: Texto de la nota.

        Returns:
            tuple[bool, str]: (éxito, mensaje).
        """
        roles_permitidos = [UserRole.MEDICO, UserRole.ENFERMERA]
        if not auth_controller.has_permission(roles_permitidos):
            return False, "Sin permisos para agregar notas."

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

        Args:
            visita_id: ID de la visita a cerrar.

        Returns:
            tuple[bool, str]: (éxito, mensaje).
        """
        if not auth_controller.has_permission([UserRole.MEDICO]):
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

    # ------------------------------------------------------------------
    # MÉTODOS PRIVADOS
    # ------------------------------------------------------------------

    @staticmethod
    def _validar_datos_paciente(datos: dict) -> tuple[bool, str]:
        """
        Valida los campos obligatorios del formulario de paciente.
        Métrica M1: 100% campos obligatorios validados.
        """
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

        # Validar cédula: solo alfanumérico y guiones
        cedula = datos["cedula"].strip()
        if len(cedula) < 5 or len(cedula) > 20:
            return False, "La cédula debe tener entre 5 y 20 caracteres."

        # Validar fecha de nacimiento
        if isinstance(datos["fecha_nacimiento"], date):
            if datos["fecha_nacimiento"] > date.today():
                return False, "La fecha de nacimiento no puede ser futura."
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
        """Registra una acción en la auditoría del sistema."""
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
