# Proyecto GAMMA Γ
## Sistema de Gestión de Expedientes Médicos
**Universidad Tecnológica de Panamá — Calidad del Software 2026**

---

## Stack Tecnológico
| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11+ |
| Frontend | PyQt6 |
| Base de Datos | PostgreSQL 16 + SQLAlchemy 2.0 |
| Seguridad | bcrypt · ISO 27001 · ISO 27799 |
| Pruebas | pytest · pytest-cov |
| Análisis de Calidad | SonarQube |

---

## Módulos del Sistema
- **M1** — Registro de Pacientes (100% campos validados)
- **M2** — Actualización de Expedientes (<2s de respuesta)
- **M3** — Consulta de Expedientes (<3s en tablet)
- **M4** — Reportes Estadísticos (sin errores estadísticos)

---

## Configuración Inicial

### 1. Requisitos previos
- Python 3.11+
- PostgreSQL 16 activo y corriendo
- pip

### 2. Clonar e instalar dependencias
```bash
git clone <url-del-repositorio>
cd proyecto_gamma
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con las credenciales de PostgreSQL
```

### 4. Crear la base de datos en PostgreSQL
```sql
CREATE DATABASE gamma_db;
CREATE USER gamma_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE gamma_db TO gamma_user;
```

### 5. Inicializar tablas y datos
```bash
python scripts/init_db.py
```

### 6. Ejecutar la aplicación
```bash
python main.py
```

---

## Credenciales Iniciales
| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | Admin1234! | Administrador |
| dr.medico | Medico1234! | Médico |
| enf.garcia | Enfer1234! | Enfermera |
| director | Director1234! | Director |
| recepcion | Recep1234! | Recepción |

> ⚠ **Cambie estas contraseñas antes de desplegar en producción.**

---

## Pruebas con pytest

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Con reporte de cobertura (para SonarQube)
pytest tests/ -v --cov=src --cov-report=xml:coverage.xml --cov-report=term

# Ver cobertura en consola
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Análisis con SonarQube

```bash
# Instalar SonarScanner (requiere Java 17+)
# https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/

# Generar reporte de cobertura primero
pytest tests/ --cov=src --cov-report=xml:coverage.xml

# Ejecutar análisis
sonar-scanner \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=TU_TOKEN_SONAR
```

---

## Estructura del Proyecto

```
proyecto_gamma/
├── main.py                         # Punto de entrada
├── requirements.txt                # Dependencias
├── pyproject.toml                  # Configuración pytest/coverage
├── sonar-project.properties        # Config SonarQube
├── .env.example                    # Template de variables de entorno
├── scripts/
│   └── init_db.py                  # Inicialización de BD
├── src/
│   ├── models/
│   │   ├── models.py               # Modelos ORM (Paciente, Usuario, etc.)
│   │   └── database.py             # Gestor de conexión PostgreSQL
│   ├── controllers/
│   │   ├── auth_controller.py      # Autenticación + auditoría
│   │   ├── paciente_controller.py  # M1, M2, M3 - lógica de negocio
│   │   └── reporte_controller.py   # M4 - estadísticas
│   └── views/
│       ├── login_view.py           # Pantalla de login (PyQt6)
│       ├── main_window.py          # Ventana principal + navegación
│       ├── paciente_view.py        # M1 - Formulario de registro
│       ├── expediente_view.py      # M2 - Visitas y notas
│       ├── consulta_view.py        # M3 - Búsqueda y detalle
│       └── reporte_view.py         # M4 - Dashboard con gráficas
└── tests/
    └── test_gamma.py               # Suite de pruebas unitarias
```

---

## Roles y Permisos

| Rol | M1 Registro | M2 Expediente | M3 Consulta | M4 Reportes |
|-----|:-----------:|:-------------:|:-----------:|:-----------:|
| Médico | ✓ | ✓ | ✓ | ✓ |
| Enfermera | ✓ | ✓ | ✓ | ✗ |
| Admin | ✓ | ✓ | ✓ | ✓ |
| Director | ✗ | ✗ | ✗ | ✓ |
| Recepción | ✓ | ✗ | ✓ | ✗ |

---

## Normas ISO Implementadas
- **ISO 27001** — Gestión de seguridad: autenticación bcrypt, log de auditoría
- **ISO 27799** — Datos médicos: control de acceso por rol, trazabilidad
- **ISO/IEC 25010** — Calidad del producto: métricas de rendimiento por módulo
