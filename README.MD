# API de Gestión de Proyectos y Clientes

## 📋 Descripción del Proyecto

Sistema RESTful desarrollado con **FastAPI** para la gestión integral de proyectos y clientes. La API proporciona funcionalidades completas para crear, leer, actualizar y eliminar proyectos, así como administrar la información de los clientes asociados a estos proyectos.

Este proyecto implementa buenas prácticas de desarrollo backend como validación de datos, manejo de errores, inyección de dependencias y utilización de una base de datos relacional.

---

## 🎯 Características Principales

- ✅ **Gestión de Proyectos**: Crear, leer, actualizar y eliminar proyectos con campos validados
- ✅ **Gestión de Clientes**: Administrar información de clientes con validación de email
- ✅ **Validación de Datos**: Usando Pydantic con restricciones y patrones
- ✅ **Base de Datos**: PostgreSQL con SQLAlchemy ORM
- ✅ **IDs Únicos**: Generación de UUIDs para identificar proyectos
- ✅ **Estados de Proyectos**: planificación, en progreso, completado, cancelado
- ✅ **Documentación Interactiva**: Swagger UI integrado en FastAPI

---

## 🛠️ Stack Tecnológico

| Tecnología | Propósito |
|-----------|----------|
| **FastAPI** | Framework web moderno y rápido |
| **Uvicorn** | Servidor ASGI |
| **Pydantic** | Validación de datos y serialización |
| **SQLAlchemy** | ORM para manejo de base de datos |
| **PostgreSQL** | Base de datos relacional |
| **psycopg2** | Adaptador PostgreSQL para Python |

---

## 📦 Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd ejercicioAPI_1
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos
Editar `config.py` con las credenciales de PostgreSQL:
```python
DATABASE_URL = "postgresql+psycopg2://usuario:contraseña@localhost:5432/api_db"
```

### 5. Crear la base de datos
```bash
createdb api_db
```

### 6. Ejecutar la aplicación
```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

---

## 📚 Documentación de la API

### Acceder a la Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### Proyectos
- `GET /proyectos` - Listar todos los proyectos
- `POST /proyectos` - Crear un nuevo proyecto
- `GET /proyectos/{proyecto_id}` - Obtener un proyecto específico
- `PUT /proyectos/{proyecto_id}` - Actualizar un proyecto
- `DELETE /proyectos/{proyecto_id}` - Eliminar un proyecto

#### Clientes
- `GET /clientes` - Listar todos los clientes
- `POST /clientes` - Crear un nuevo cliente
- `GET /clientes/{cliente_id}` - Obtener un cliente específico
- `PUT /clientes/{cliente_id}` - Actualizar un cliente
- `DELETE /clientes/{cliente_id}` - Eliminar un cliente

---

## 🏗️ Estructura del Proyecto

```
ejercicioAPI_1/
├── main.py                 # Aplicación principal y rutas
├── config.py              # Configuración de base de datos
├── requirements.txt       # Dependencias del proyecto
└── README.md             # Este archivo
```

### Estructura de Datos

#### Modelo Proyecto
```python
{
  "proyecto_id": "uuid",
  "nombre": "string",
  "descripcion": "string",
  "presupuesto": 0.0,
  "fecha_inicio": "YYYY-MM-DD",
  "estado": "planificacion|en_progreso|completado|cancelado"
}
```

#### Modelo Cliente
```python
{
  "nombre": "string",
  "email": "email@example.com",
  "telefono": "string",
  "empresa": "string",
  "direccion": "string"
}
```

---

---

## 🔐 Validaciones Implementadas

- **Proyecto**:
  - Nombre: 3-100 caracteres
  - Descripción: 10-500 caracteres
  - Presupuesto: Mayor a 0, máximo 1,000,000
  - Estado: Solo valores permitidos (planificación, en_progreso, completado, cancelado)
  - Fecha: Formato YYYY-MM-DD

- **Cliente**:
  - Nombre: 2-50 caracteres
  - Email: Validación de formato de email
  - Teléfono: 7-20 caracteres
  - Empresa: 2-100 caracteres
  - Dirección: 10-200 caracteres

---

## 📝 Ejemplos de Uso

### Crear un Proyecto
```bash
curl -X POST "http://localhost:8000/proyectos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sistema de gestión web",
    "descripcion": "Desarrollo de un web para gestión de inventarios",
    "presupuesto": 25000.50,
    "fecha_inicio": "2025-06-21",
    "estado": "en_progreso"
  }'
```

### Crear un Cliente
```bash
curl -X POST "http://localhost:8000/clientes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Luis Fernando González",
    "email": "luis@example.com",
    "telefono": "+573126429417",
    "empresa": "Tech Solutions S.A.S",
    "direccion": "Calle 123 #45-67, Medellin, Colombia"
  }'
```

---

## 🐛 Manejo de Errores

La API implementa gestión robusta de errores:

| Código | Significado |
|--------|------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Error de validación |
| 500 | Internal Server Error - Error en el servidor |

---

## 🔗 Dependencias

Ver [requirements.txt](requirements.txt) para la lista completa de dependencias con versiones.

---



 
