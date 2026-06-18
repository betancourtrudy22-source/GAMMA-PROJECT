"""
Proyecto GAMMA - Script de Inicialización de Base de Datos
Crea las tablas y usuarios iniciales del sistema.
Roles actualizados: ADMIN, MEDICO, ENF_TRIAGE, ENF_ASISTENCIAL, DIRECTOR, RECEPCION.

Uso:
    python scripts/init_db.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date
from src.models.database import db_manager
from src.models.models import CitaMedica, CitaStatus, Usuario, Paciente, Gender, BloodType, UserRole
from src.controllers.auth_controller import AuthController


def crear_usuarios_iniciales(session) -> None:
    """Crea los usuarios del sistema con todos sus roles."""
    usuarios_iniciales = [
        {
            "nombre_usuario": "admin",
            "nombre_completo": "Administrador del Sistema",
            "password": "Admin1234!",
            "rol": UserRole.ADMIN,
            "email": "admin@hospital.gob.pa",
        },
        {
            "nombre_usuario": "dr.medico",
            "nombre_completo": "Dr. Carlos Méndez",
            "password": "Medico1234!",
            "rol": UserRole.MEDICO,
            "email": "cmedico@hospital.gob.pa",
        },
        {
            "nombre_usuario": "enf.triage",
            "nombre_completo": "Enf. Ana García — Triage",
            "password": "Triage1234!",
            "rol": UserRole.ENF_TRIAGE,
            "email": "agarcia.triage@hospital.gob.pa",
        },
        {
            "nombre_usuario": "enf.asistencial",
            "nombre_completo": "Enf. Pedro Ruiz — Asistencial",
            "password": "Asist1234!",
            "rol": UserRole.ENF_ASISTENCIAL,
            "email": "pruiz@hospital.gob.pa",
        },
        {
            "nombre_usuario": "director",
            "nombre_completo": "Dr. Luis Varela — Director Médico",
            "password": "Director1234!",
            "rol": UserRole.DIRECTOR,
            "email": "director@hospital.gob.pa",
        },
        {
            "nombre_usuario": "recepcion",
            "nombre_completo": "María López — Admisiones",
            "password": "Recep1234!",
            "rol": UserRole.RECEPCION,
            "email": "mlopez@hospital.gob.pa",
        },
        {
            "nombre_usuario": "med.interna",
            "nombre_completo": "Dr. Jorge Castillo — Medicina Interna",
            "password": "MedInt1234!",
            "rol": UserRole.MEDICINA_INTERNA,
            "email": "jcastillo.interna@hospital.gob.pa",
        },
    ]

    for datos in usuarios_iniciales:
        existente = (
            session.query(Usuario)
            .filter(Usuario.nombre_usuario == datos["nombre_usuario"])
            .first()
        )
        if existente is None:
            usuario = Usuario(
                nombre_usuario=datos["nombre_usuario"],
                nombre_completo=datos["nombre_completo"],
                password_hash=AuthController.hash_password(datos["password"]),
                rol=datos["rol"],
                email=datos["email"],
                activo=True,
            )
            session.add(usuario)
            print(f"  ✓ Usuario creado: {datos['nombre_usuario']} [{datos['rol'].value}]")
        else:
            print(f"  — Ya existe: {datos['nombre_usuario']}")


def crear_pacientes_prueba(session) -> None:
    """Crea pacientes de prueba para desarrollo."""
    pacientes_prueba = [
        {
            "cedula": "8-123-001",
            "nombre": "Carlos",
            "apellido": "Rodríguez",
            "fecha_nacimiento": date(1975, 3, 20),
            "genero": Gender.MASCULINO,
            "tipo_sangre": BloodType.O_POS,
            "nacionalidad": "Panameño",
            "telefono": "6100-0001",
            "alergias": "Penicilina",
            "enfermedades_cronicas": "Diabetes tipo 2, Hipertensión",
        },
        {
            "cedula": "4-567-002",
            "nombre": "María",
            "apellido": "González",
            "fecha_nacimiento": date(1990, 7, 14),
            "genero": Gender.FEMENINO,
            "tipo_sangre": BloodType.A_POS,
            "nacionalidad": "Panameña",
            "telefono": "6200-0002",
            "alergias": "Ninguna conocida",
            "enfermedades_cronicas": "",
        },
        {
            "cedula": "2-888-003",
            "nombre": "Roberto",
            "apellido": "Morales",
            "fecha_nacimiento": date(1960, 11, 5),
            "genero": Gender.MASCULINO,
            "tipo_sangre": BloodType.B_NEG,
            "nacionalidad": "Panameño",
            "telefono": "6300-0003",
            "alergias": "Sulfas, Aspirina",
            "enfermedades_cronicas": "EPOC",
        },
    ]

    for datos in pacientes_prueba:
        existente = (
            session.query(Paciente)
            .filter(Paciente.cedula == datos["cedula"])
            .first()
        )
        if existente is None:
            paciente = Paciente(**datos)
            session.add(paciente)
            print(f"  ✓ Paciente creado: {datos['nombre']} {datos['apellido']}")
        else:
            print(f"  — Ya existe paciente: {datos['cedula']}")


def main() -> None:
    print("=" * 60)
    print("  Proyecto GAMMA — Inicialización de Base de Datos")
    print("=" * 60)

    print("\n[1/3] Conectando a PostgreSQL...")
    db_manager.initialize()

    if not db_manager.test_connection():
        print("  ✗ No se pudo conectar a la base de datos.")
        print("  Verifique el archivo .env y que PostgreSQL esté activo.")
        sys.exit(1)
    print("  ✓ Conexión exitosa.")

    print("\n[2/3] Creando tablas...")
    db_manager.create_tables()
    print("  ✓ Tablas creadas (o ya existentes).")

    print("\n[3/3] Insertando datos iniciales...")
    session = db_manager.get_session()
    try:
        print("  — Usuarios del sistema:")
        crear_usuarios_iniciales(session)
        print("  — Pacientes de prueba:")
        crear_pacientes_prueba(session)
        session.commit()
        print("\n✓ Base de datos inicializada exitosamente.")
    except Exception as exc:
        session.rollback()
        print(f"\n✗ Error: {exc}")
        sys.exit(1)
    finally:
        session.close()

    print("\nCredenciales de acceso:")
    print("  admin           / Admin1234!       [Administrador]")
    print("  dr.medico       / Medico1234!      [Médico]")
    print("  enf.triage      / Triage1234!      [Enfermero Triage]")
    print("  enf.asistencial / Asist1234!       [Enfermero Asistencial]")
    print("  director        / Director1234!    [Director Médico]")
    print("  recepcion       / Recep1234!       [Recepción]")
    print("  med.interna     / MedInt1234!      [Medicina Interna]")
    print("\n⚠  Cambie todas las contraseñas antes de producción.\n")


if __name__ == "__main__":
    main()
