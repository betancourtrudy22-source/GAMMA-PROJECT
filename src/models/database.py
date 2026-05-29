"""
Proyecto GAMMA - Gestor de Conexión a Base de Datos
PostgreSQL + SQLAlchemy 2.0

Implementa patrón Singleton para la sesión de BD.
"""

import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from src.models.models import Base

load_dotenv()


class DatabaseManager:
    """
    Gestor centralizado de la conexión a PostgreSQL.
    Implementa patrón Singleton para evitar múltiples instancias.
    """

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, database_url: str = None) -> None:
        """
        Inicializa el motor de base de datos.

        Args:
            database_url: URL de conexión. Si es None, usa variables de entorno.
        """
        if database_url is None:
            database_url = self._build_url_from_env()

        self._engine = create_engine(
            database_url,
            echo=os.getenv("APP_DEBUG", "False").lower() == "true",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verifica conexión antes de usar
        )

        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
        )

    def _build_url_from_env(self) -> str:
        """Construye la URL de conexión desde variables de entorno."""
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "gamma_db")
        user = os.getenv("DB_USER", "gamma_user")
        password = os.getenv("DB_PASSWORD", "")
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

    def create_tables(self) -> None:
        """Crea todas las tablas definidas en los modelos."""
        Base.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        """
        Retorna una nueva sesión de base de datos.

        Returns:
            Session: Sesión de SQLAlchemy lista para usar.

        Raises:
            RuntimeError: Si el gestor no ha sido inicializado.
        """
        if self._session_factory is None:
            raise RuntimeError(
                "DatabaseManager no inicializado. Llame a initialize() primero."
            )
        return self._session_factory()

    def get_session_context(self) -> Generator[Session, None, None]:
        """
        Context manager para sesiones con commit/rollback automático.

        Yields:
            Session: Sesión de SQLAlchemy.
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def test_connection(self) -> bool:
        """
        Verifica que la conexión a la BD esté activa.

        Returns:
            bool: True si la conexión es exitosa.
        """
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Cierra todas las conexiones del pool."""
        if self._engine:
            self._engine.dispose()


# Instancia global del gestor
db_manager = DatabaseManager()
