from pydantic import BaseModel
from typing import Optional

# --- VEHÍCULOS ---
class VehiculoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ip_asignada: Optional[str] = None
    conectado: Optional[bool] = False

class VehiculoUpdate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ip_asignada: Optional[str] = None
    conectado: Optional[bool] = False
    activo: Optional[bool] = True

# --- COMANDOS ---
class ComandoCreate(BaseModel):
    id_vehiculo: int
    nombre: str
    codigo: str
    descripcion: Optional[str] = None

class ComandoUpdate(BaseModel):
    id_vehiculo: int
    nombre: str
    codigo: str
    descripcion: Optional[str] = None

# --- MOVIMIENTO INDIVIDUAL (Punto 5) ---
class MovimientoIndividualRequest(BaseModel):
    id_vehiculo: int
    id_comando: int
    origen: Optional[str] = "WEB"

# --- DEMO ---
class DemoCreate(BaseModel):
    id_vehiculo: int
    nombre: str
    descripcion: Optional[str] = None

class DemoUpdate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

# --- MOVIMIENTO DEMO ---
class MovimientoDemoCreate(BaseModel):
    id_demo: int
    id_comando: int
    orden: int
    duracion_ms: int
    pausa_ms: Optional[int] = 500

class MovimientoDemoUpdate(BaseModel):
    orden: int
    duracion_ms: int
    pausa_ms: Optional[int] = 500