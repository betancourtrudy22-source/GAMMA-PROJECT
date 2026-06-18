"""
Proyecto GAMMA - Controlador de Reportes
Módulo M4: Generación de Reportes Médicos y Estadísticas
Métrica: Sin errores estadísticos. Generación < 10s para 100 registros.
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from src.models.models import (
    Paciente, VisitaMedica, Usuario, UserRole
)
from src.models.database import db_manager
from src.controllers.auth_controller import auth_controller


class ReporteController:
    """
    Controlador M4: Generación de reportes estadísticos hospitalarios.
    Rol con acceso: Médico, Admin, Director.
    """

    def obtener_estadisticas_generales(self) -> Optional[dict]:
        """
        M4: Genera estadísticas generales del sistema.

        Returns:
            Optional[dict]: Estadísticas o None si no hay permisos.
        """
        roles_permitidos = [UserRole.MEDICO, UserRole.ADMIN, UserRole.DIRECTOR]
        if not auth_controller.has_permission(roles_permitidos):
            return None

        session: Session = db_manager.get_session()
        try:
            # 1. Contamos el total de pacientes
            total_pacientes = session.query(func.count(Paciente.id)).scalar()
            
            # 2. Contamos el total de visitas
            total_visitas = session.query(func.count(VisitaMedica.id)).scalar()
       
            # 3. Visitas con estado ACTIVA
            from src.models.models import VisitStatus
            visitas_activas = (
                session.query(func.count(VisitaMedica.id))
                .filter(VisitaMedica.estado == VisitStatus.ACTIVA)
                .scalar()
            )

            return {
                "total_pacientes": total_pacientes or 0,
                "total_visitas": total_visitas or 0,
                "visitas_activas": visitas_activas or 0,
                "generado_en": datetime.utcnow().isoformat(),
            }
        finally:
            session.close()

    def obtener_visitas_por_mes(self, anio: int = None) -> list[dict]:
        """
        M4: Retorna el conteo de visitas agrupadas por mes.

        Args:
            anio: Año a consultar. Si es None, usa el año actual.

        Returns:
            list[dict]: Lista con mes y cantidad de visitas.
        """
        roles_permitidos = [UserRole.MEDICO, UserRole.ADMIN, UserRole.DIRECTOR]
        if not auth_controller.has_permission(roles_permitidos):
            return []

        anio = anio or datetime.utcnow().year
        session: Session = db_manager.get_session()
        try:
            resultados = (
                session.query(
                    extract("month", VisitaMedica.fecha_ingreso).label("mes"),
                    func.count(VisitaMedica.id).label("cantidad"),
                )
                .filter(
                    extract("year", VisitaMedica.fecha_ingreso) == anio
                )
                .group_by("mes")
                .order_by("mes")
                .all()
            )

            meses = [
                "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
            ]
            datos = []
            for fila in resultados:
                mes_idx = int(fila.mes) - 1
                datos.append({
                    "mes": meses[mes_idx],
                    "mes_num": int(fila.mes),
                    "cantidad": int(fila.cantidad),
                })
            return datos
        finally:
            session.close()

    def obtener_distribucion_genero(self) -> dict:
        """
        M4: Distribución de pacientes por género.

        Returns:
            dict: Conteo por género.
        """
        roles_permitidos = [UserRole.MEDICO, UserRole.ADMIN, UserRole.DIRECTOR]
        if not auth_controller.has_permission(roles_permitidos):
            return {}

        session: Session = db_manager.get_session()
        try:
            resultados = (
                session.query(
                    Paciente.genero,
                    func.count(Paciente.id).label("cantidad"),
                )
                .filter(Paciente.activo.is_(True))
                .group_by(Paciente.genero)
                .all()
            )
            return {
                str(fila.genero.value): int(fila.cantidad)
                for fila in resultados
            }
        finally:
            session.close()

    def obtener_top_diagnosticos(self, limite: int = 10) -> list[dict]:
        """
        M4: Diagnósticos más frecuentes.

        Args:
            limite: Número máximo de resultados.

        Returns:
            list[dict]: Lista con diagnóstico y frecuencia.
        """
        roles_permitidos = [UserRole.MEDICO, UserRole.ADMIN, UserRole.DIRECTOR]
        if not auth_controller.has_permission(roles_permitidos):
            return []

        session: Session = db_manager.get_session()
        try:
            resultados = (
                session.query(
                    VisitaMedica.diagnostico_final,
                    func.count(VisitaMedica.id).label("cantidad"),
                )
                .filter(VisitaMedica.diagnostico_final.isnot(None))
                .filter(VisitaMedica.diagnostico_final != "")
                .group_by(VisitaMedica.diagnostico_final)
                .order_by(func.count(VisitaMedica.id).desc())
                .limit(limite)
                .all()
            )
            return [
                {"diagnostico": fila.diagnostico_final, "cantidad": int(fila.cantidad)}
                for fila in resultados
            ]
        finally:
            session.close()

    def obtener_pacientes_rango_fecha(
        self, fecha_inicio: date, fecha_fin: date
    ) -> list[dict]:
        """
        M4: Lista de pacientes registrados en un rango de fechas.

        Args:
            fecha_inicio: Fecha de inicio del rango.
            fecha_fin: Fecha fin del rango.

        Returns:
            list[dict]: Datos de pacientes registrados en el rango.
        """
        roles_permitidos = [UserRole.ADMIN, UserRole.DIRECTOR]
        if not auth_controller.has_permission(roles_permitidos):
            return []

        session: Session = db_manager.get_session()
        try:
            pacientes = (
                session.query(Paciente)
                .filter(
                    func.date(Paciente.creado_en) >= fecha_inicio,
                    func.date(Paciente.creado_en) <= fecha_fin,
                    Paciente.activo.is_(True),
                )
                .order_by(Paciente.creado_en.desc())
                .all()
            )
            return [
                {
                    "id": p.id,
                    "nombre_completo": p.nombre_completo,
                    "cedula": p.cedula,
                    "fecha_registro": p.creado_en.strftime("%d/%m/%Y"),
                    "total_visitas": len(p.visitas),
                }
                for p in pacientes
            ]
        finally:
            session.close()


# Instancia global
reporte_controller = ReporteController()