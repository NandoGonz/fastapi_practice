import uuid
from fastapi import FastAPI, APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date
from sqlalchemy import Column, String, Float, Date, Text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from config import Base, engine, get_db


# Modelos pydantic
class ProyectoBase(BaseModel):
    """Modelo base para proyectos"""

    nombre: str = Field(
        ..., min_length=3, max_length=100, examples=["Sistema de gestión web"]
    )
    descripcion: str = Field(
        ...,
        min_length=10,
        max_length=500,
        examples=[
            "Desarrollo de un web para gestión de inventarios con panel de administración"
        ],
    )
    presupuesto: float = Field(..., gt=0, le=1000000, examples=[25000.50])
    fecha_inicio: str = Field(..., description="YYYY-MM-DD", examples=["2025-06-21"])
    estado: str = Field(
        ...,
        pattern=r"^(planificacion|en_progreso|completado|cancelado)$",
        examples=["en_progreso"],
    )


class ProyectoCreate(ProyectoBase):
    """Modelo para crear un proyecto (entrada)"""

    pass


class ProyectoUpdate(BaseModel):
    """Modelo para actualizar parcialmente el proyecto"""

    nombre: Optional[str] = Field(
        None, min_length=3, max_length=100, examples=["Sistema de gestión actualizado"]
    )
    descripcion: Optional[str] = Field(
        None,
        min_length=10,
        max_length=500,
        examples=["Descripción actualizada del proyecto con nuevas funcionalidades"],
    )
    presupuesto: Optional[float] = Field(None, gt=0, le=1000000, examples=[30000.75])
    fecha_inicio: Optional[str] = Field(
        None, examples=["2024-02-01"]
    )  # También opcional; cuando venga se parsea
    estado: str = Field(
        ...,
        pattern=r"^(planificacion|en_progreso|completado|cancelado)$",
        examples=["planificacion"],
    )  # Estado con patrón restringido a valores permitidos


class ProyectoResponse(ProyectoBase):
    """Modelo de respuesta para un proyecto"""

    proyecto_id: str = Field(
        ...,
        description="ID único del proyecto (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )  # Agrega el ID del proyecto a la respuesta


# modelos para los clientes
class ClienteBase(BaseModel):
    nombre: str = Field(
        ..., min_length=2, max_length=50, examples=["Luis Fernando González Borja"]
    )
    email: EmailStr = Field(
        ..., examples=["lasmarcas14@gmail.com"]
    )  # validamos el email usando pydantic
    telefono: str = Field(..., min_length=7, max_length=20, examples=["+573126429417"])
    empresa: str = Field(
        ..., min_length=2, max_length=100, examples=["Tech Solutions S.A.S"]
    )
    direccion: str = Field(
        ...,
        min_length=10,
        max_length=200,
        examples=["Calle 123 #45-67, Medellin, Colombia"],
    )


class ClienteCreate(ClienteBase):
    """Modelo para crear un cliente (entrada)"""

    pass


class ClienteUpdate(BaseModel):
    """Modelo para actualizar parcialmente un cliente"""

    nombre: Optional[str] = Field(
        None, min_length=2, max_length=50, examples=["María García López"]
    )
    email: Optional[EmailStr] = Field(None, examples=["maria.garcia@nuevaempresa.com"])
    telefono: Optional[str] = Field(
        None, min_length=7, max_length=20, examples=["+573009876543"]
    )
    empresa: Optional[str] = Field(
        None, min_length=2, max_length=100, examples=["Innovación Digital Ltda."]
    )
    direccion: Optional[str] = Field(
        None,
        min_length=10,
        max_length=200,
        examples=["Avenida 68 #25-30, Medellín, Colombia"],
    )


class ClienteResponse(ClienteBase):
    cliente_id: str = Field(
        ...,
        description="ID único del cliente (UUID)",
        examples=["6ba7b810-9dad-11d1-80b4-00c04fd430c8"],
    )  # ID en la respuesta


# Modelos ORM sqlalchemy


class Proyecto(Base):
    __tablename__ = "proyectos"
    __table_args__ = {"extend_existing": True}  # permite definir la tabla si ya existe

    proyecto_id = Column(String(36), primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    presupuesto = Column(Float, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)


class Cliente(Base):
    __tablename__ = "clientes"  # Tabla para clientes
    __table_args__ = {"extend_existing": True}  # Igual que arriba

    cliente_id = Column(String(36), primary_key=True)  # UUID string como PK
    nombre = Column(String(50), nullable=False)  # Nombre del cliente
    email = Column(String(255), nullable=False)  # Email almacenado como string
    telefono = Column(String(20), nullable=False)  # Teléfono
    empresa = Column(String(100), nullable=False)  # Empresa asociada
    direccion = Column(String(200), nullable=False)  # Dirección


# Rutas personalizadas

# Route del proyecto
proyectos_router = APIRouter(
    prefix="/proyectos",
    tags=["Proyectos"],
    responses={404: {"description": "Proyecto no encontrado"}},
)

# Router Cliente
clientes_router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={404: {"description": "Cliente no encontrado"}},
)


# Endpoints para el proyecto
@proyectos_router.post(
    "/",
    response_model=ProyectoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proyecto",
)
async def create_proyecto(proyecto: ProyectoCreate, db: Session = Depends(get_db)):
    # Endpoint asíncrono para crear un proyecto. Recibe un pydantic (proyecto) y la sesión por dependencia
    try:
        proyecto_id = str(uuid.uuid4())
        fecha_dt = date.fromisoformat(
            proyecto.fecha_inicio
        )  # convierte la fecha en un string
        orm_obj = Proyecto(
            proyecto_id=proyecto_id,
            nombre=proyecto.nombre,
            descripcion=proyecto.descripcion,
            presupuesto=float(round(proyecto.presupuesto, 2)),
            fecha_inicio=fecha_dt,
            estado=proyecto.estado,
        )
        db.add(orm_obj)  # añade el objeto ORM ala sesión (pendiente de commit)
        db.commit()
        db.refresh(orm_obj)
        return {
            "proyecto_id": orm_obj.proyecto_id,
            "nombre": orm_obj.nombre,
            "descripcion": orm_obj.descripcion,
            "presupuesto": orm_obj.presupuesto,
            "fecha_inicio": orm_obj.fecha_inicio.strftime("%Y-%m-%d"),
            "estado": orm_obj.estado,
        }
    except SQLAlchemyError as e:
        db.rollback()  # en case de error de DB, revertir la transacción
        raise HTTPException(status_code=500, detail=f"[ERROR] interno. {str(e)}") from (
            e
        )
    except Exception as e:
        db.rollback()  # revertir ante cualquier otra exepción
        raise HTTPException(status_code=500, detail=f"[ERROR] interno: {str(e)}") from (
            e
        )


@proyectos_router.get(
    "/", response_model=List[ProyectoResponse], summary="Obtener todos los proyectos"
)
async def get_all_proyectos(db: Session = Depends(get_db)):
    # Endpoint para obtener todos los proyectos
    try:
        rows = db.query(
            Proyecto
        ).all()  # consulta todos los registros de la table proyectos
        return [
            {
                "proyecto_id": r.proyecto_id,
                "nombre": r.nombre,
                "descripcion": r.descripcion,
                "presupuesto": r.presupuesto,
                "fecha_inicio": r.fecha_inicio.strftime("%Y-%m-%d"),
                "estado": r.estado,
            }
            for r in rows
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


@proyectos_router.get(
    "/{proyecto_id}",
    response_model=ProyectoResponse,
    summary="Obtener un proyecto por ID",
)
async def read_proyecto(proyecto_id: str, db: Session = Depends(get_db)):
    try:
        uuid.UUID(
            proyecto_id
        )  # intenta crear un UUID a partie del string; lanza ValueError sino es valido
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="Formato de ID ded pproyecto inválido. Debe ser un UUID válido",
        ) from exc

    try:
        obj = db.query(Proyecto).filter(Proyecto.proyecto_id == proyecto_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return {
            "proyecto_id": obj.proyecto_id,
            "nombre": obj.nombre,
            "descripcion": obj.descripcion,
            "presupuesto": obj.presupuesto,
            "fecha_inicio": obj.fecha_inicio.strftime("%Y-%m-%d"),
            "estado": obj.estado,
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


@proyectos_router.patch(
    "/{proyecto_id}",
    response_model=ProyectoResponse,
    summary="Actualizar un proyecto existente",
)
async def update_proyecto(
    proyecto_id: str, proyecto: ProyectoUpdate, db: Session = Depends(get_db)
):
    # Validar formato UUID
    try:
        uuid.UUID(proyecto_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="Formato de ID de proyecto inválido. Debe ser un UUDI v+alido",
        ) from exc
    try:
        obj = (
            db.query(Proyecto).filter(Proyecto.proyecto_id == proyecto_id).first()
        )  # Busca el objeto existente
        if not obj:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        data = proyecto.model_dump(exclude_unset=True)  # Extrae los campos enviados
        if "fecha_inicio" in data and data["fecha_inicio"] is not None:
            data["fecha_inicio"] = date.fromisoformat(data["fecha_inicio"])
            for k, v in data.items():
                setattr(obj, k, v)  # Asigna dinámicamente atributos al objeto ORM
            db.commit()
            db.refresh(obj)
            return {
                "proyecto_id": obj.proyecto_id,
                "nombre": obj.nombre,
                "descripcion": obj.descripcion,
                "presupuesto": obj.presupuesto,
                "fecha_inicio": obj.fecha_inicio.strftime("%Y-%m-%d"),
                "estado": obj.estado,
            }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


@proyectos_router.delete(
    "/{proyecto_id}", status_code=status.HTTP_200_OK, summary="Eliminar un proyecto"
)
async def delete_proyecto(proyecto_id: str, db: Session = Depends(get_db)):
    # Validar formato UUID
    try:
        uuid.UUID(proyecto_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Formado de ID inválido. debe ser UUID"
        ) from exc

    try:
        obj = (
            db.query(Proyecto).filter(Proyecto.proyecto_id == proyecto_id).first()
        )  # Busca el pryecto
        if not obj:
            raise HTTPException(status_code=422, detail="Proyecto no encontrado")
        db.delete(obj)
        db.commit()
        return {"mensaje": "Proyecto eliminado con exito"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


# Endpoints para clientes
@clientes_router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo cliente",
)
async def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    # Crea un nuevo cliente en la BD
    try:
        cliente_id = (str(uuid.uuid4()),)
        orm_obj = Cliente(
            cliente_id=cliente_id,
            nombre=cliente.nombre,
            email=str(cliente.email),
            telefono=cliente.telefono,
            empresa=cliente.empresa,
            direccion=cliente.direccion,
        )
        db.add(orm_obj)
        db.commit()
        db.refresh(orm_obj)
        return {
            "cliente_id": orm_obj.cliente_id,
            "nombre": orm_obj.nombre,
            "email": orm_obj.email,
            "telefono": orm_obj.telefono,
            "empresa": orm_obj.empresa,
            "direccion": orm_obj.direccion,
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


@clientes_router.get(
    "/", response_model=List[ClienteResponse], summary="Obtener todos los clientes"
)
async def get_all_clientes(db: Session = Depends(get_db)):
    # Endpoint para obtener todos los clientes
    try:
        rows = db.query(
            Cliente
        ).all()  # consulta todos los registros de la tabla clientes
        return [
            {
                "cliente_id": r.cliente_id,
                "nombre": r.nombre,
                "email": r.email,
                "telefono": r.telefono,
                "empresa": r.empresa,
                "direccion": r.direccion,
            }
            for r in rows
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


@clientes_router.patch(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Actualizar un cliente existente",
)
async def update_cliente(
    cliente_id: str, cliente: ClienteUpdate, db: Session = Depends(get_db)
):
    # Validar formato UUID
    try:
        uuid.UUID(cliente_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="Formato de ID de cliente inválido. Debe ser un UUID válido",
        ) from exc
    try:
        obj = (
            db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
        )  # Busca el objeto existente
        if not obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        data = cliente.model_dump(exclude_unset=True)  # Extrae los campos enviados
        for k, v in data.items():
            setattr(obj, k, v)  # Asigna dinámicamente atributos al objeto ORM
        db.commit()
        db.refresh(obj)
        return {
            "cliente_id": obj.cliente_id,
            "nombre": obj.nombre,
            "email": obj.email,
            "telefono": obj.telefono,
            "empresa": obj.empresa,
            "direccion": obj.direccion,
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


@clientes_router.delete(
    "/{cliente_id}", status_code=status.HTTP_200_OK, summary="Eliminar un cliente"
)
async def delete_cliente(cliente_id: str, db: Session = Depends(get_db)):
    # Validar formato UUID
    try:
        uuid.UUID(cliente_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Formato de ID inválido. Debe ser un UUID válido"
        ) from exc

    try:
        obj = (
            db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
        )  # Busca el cliente
        if not obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        db.delete(obj)
        db.commit()
        return {"mensaje": "Cliente eliminado con éxito"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error de base de datos: {str(e)}"
        ) from (e)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}") from (e)


# LIFESPAN MANAGER
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Starup
    print("Iniciando la aplicación...")
    print("Conectando a PostgreSQL...")

    # Crear tablas con ORM (simple y directo)
    try:
        Base.metadata.create_all(
            bind=engine, checkfirst=True
        )  # Crea las tablas si no existen
        print("Tablas creadas/veridicadas correctamente.")
    except Exception as e:
        print(f"Error al crear/verificar las tablas: {str(e)}")
        print("Continuadno ...")
    yield  # Punto en el que FastAPI ejecuta la aplicación entre el startup y shutdown

    # Shutdown
    print("Crando conexiones a la base de datos...")


# APP PRINCIPAL
app = FastAPI(
    title="API de Gestión de Proyectos y Clientes",
    description="API para gestionar proyectos y clientes con FastAPI y PostgreSQL, validación de datos con Pydantic y manejo de errores.",
    version="1.0.0",
    lifespan=lifespan,  # Asignamos el lifespan manager de lifespan definido arriba
)


# ENDPOINTS RAÍZ
@app.get("/", summary="Págian raíz de la API")
async def root():
    return {
        "mensaje": "Bienvenido a la API de Gestión de Proyectos y Clientes!",
        "version": "2.2.0",
        "documentation": "/docs",
        "base_de_datos": "PostgreSQL",
        "endpoints": {"proyectos": "/proyectos", "clientes": "/clientes"},
    }


# iNLCUIR ROUETERS PERSONALIZADOS
app.include_router(proyectos_router)
app.include_router(clientes_router)

# Punto de entrada
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
