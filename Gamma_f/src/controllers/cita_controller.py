"""
Proyecto GAMMA - Controlador de Citas Médicas
Solo el médico puede crear, modificar y cancelar citas.
ISO 27799 / Ley 81 - Mínimo privilegio.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import joinedload
from src.models.models import CitaMedica, CitaStatus, UserRole, AuditoriaLog
from src.models.database import db_manager
from src.controllers.auth_controller import auth_controller

ROLES_CITAS = [UserRole.MEDICO, UserRole.ADMIN]

class CitaController:

    def crear_cita(self, paciente_id: int, datos: dict) -> tuple[bool, str, Optional[CitaMedica]]:
        if not auth_controller.has_permission(ROLES_CITAS):
            return False, "Solo el médico puede programar citas.", None
        session = db_manager.get_session()
        try:
            cita = CitaMedica(
                paciente_id=paciente_id,
                medico_id=auth_controller.current_user.id,
                visita_id=datos.get("visita_id"),
                fecha_cita=datos["fecha_cita"],
                motivo=datos.get("motivo", ""),
                area_especialidad=datos.get("area_especialidad", ""),
                notas=datos.get("notas", ""),
                estado=CitaStatus.PROGRAMADA,
            )
            session.add(cita)
            # Auditoría ISO 27799
            log = AuditoriaLog(
                usuario_id=auth_controller.current_user.id,
                accion="CITA_PROGRAMADA",
                tabla_afectada="citas_medicas",
                registro_id=paciente_id,
                detalle=f"Fecha: {datos['fecha_cita']}"
            )
            session.add(log)
            session.commit()
            session.refresh(cita)
            return True, f"Cita programada para {cita.fecha_cita.strftime('%d/%m/%Y %H:%M')}.", cita
        except Exception as e:
            session.rollback()
            return False, f"Error al crear cita: {e}", None
        finally:
            session.close()

    def obtener_citas_paciente(self, paciente_id: int) -> list[CitaMedica]:
        session = db_manager.get_session()
        try:
            citas = (session.query(CitaMedica)
                     .filter(CitaMedica.paciente_id == paciente_id)
                     .order_by(CitaMedica.fecha_cita.desc())
                     .all())
            session.expunge_all()
            return citas
        finally:
            session.close()

    def obtener_todas_citas(self) -> list[CitaMedica]:
        session = db_manager.get_session()
        try:
            citas = (session.query(CitaMedica)
                     .options(joinedload(CitaMedica.paciente))
                     .order_by(CitaMedica.fecha_cita.asc())
                     .all())
            session.expunge_all()
            return citas
        finally:
            session.close()

    def cambiar_estado(self, cita_id: int, nuevo_estado: CitaStatus) -> tuple[bool, str]:
        if not auth_controller.has_permission(ROLES_CITAS):
            return False, "Sin permisos."
        session = db_manager.get_session()
        try:
            cita = session.get(CitaMedica, cita_id)
            if not cita:
                return False, "Cita no encontrada."
            cita.estado = nuevo_estado
            session.commit()
            return True, f"Cita actualizada a {nuevo_estado.value}."
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def cancelar_cita(self, cita_id: int) -> tuple[bool, str]:
        return self.cambiar_estado(cita_id, CitaStatus.CANCELADA)

cita_controller = CitaController()
