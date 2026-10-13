from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
from app.models.schemas import (
    VehiculoCreate, VehiculoUpdate,
    ComandoCreate, ComandoUpdate,
    MovimientoIndividualRequest,
    DemoCreate, DemoUpdate,
    MovimientoDemoCreate, MovimientoDemoUpdate
)
from app.services import VehiculoService
from app.websocket_manager import manager

app = FastAPI(
    title="API IoT - Práctica 2.5",
    description="Integración de 21 Stored Procedures para control de vehículos IoT"
)

# --- WEBSOCKET ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==========================================
# 1. VEHÍCULOS
# ==========================================
@app.get("/api/vehiculos", tags=["Vehículos"])
def listar_vehiculos():
    return VehiculoService.obtener_vehiculos() or []

@app.get("/api/vehiculos/{id_vehiculo}", tags=["Vehículos"])
def obtener_vehiculo(id_vehiculo: int):
    res = VehiculoService.obtener_vehiculo_por_id(id_vehiculo)
    if not res:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return res

@app.post("/api/vehiculos", tags=["Vehículos"])
def crear_vehiculo(data: VehiculoCreate):
    return VehiculoService.crear_vehiculo(data.nombre, data.descripcion, data.ip_asignada)

@app.put("/api/vehiculos/{id_vehiculo}", tags=["Vehículos"])
def actualizar_vehiculo(id_vehiculo: int, data: VehiculoUpdate):
    VehiculoService.actualizar_vehiculo(id_vehiculo, data.nombre, data.descripcion, data.ip_asignada)
    return {"message": "Vehículo actualizado"}

@app.delete("/api/vehiculos/{id_vehiculo}", tags=["Vehículos"])
def eliminar_vehiculo(id_vehiculo: int):
    VehiculoService.eliminar_vehiculo(id_vehiculo)
    return {"message": "Vehículo eliminado"}

# ==========================================
# 2. COMANDOS
# ==========================================
@app.get("/api/vehiculos/{id_vehiculo}/comandos", tags=["Comandos"])
def listar_comandos(id_vehiculo: int):
    return VehiculoService.obtener_comandos_vehiculo(id_vehiculo) or []

@app.post("/api/comandos", tags=["Comandos"])
def crear_comando(data: ComandoCreate):
    return VehiculoService.crear_comando(data.id_vehiculo, data.nombre, data.codigo, data.descripcion)

@app.put("/api/comandos/{id_comando}", tags=["Comandos"])
def actualizar_comando(id_comando: int, data: ComandoUpdate):
    VehiculoService.actualizar_comando(id_comando, data.nombre, data.codigo, data.descripcion)
    return {"message": "Comando actualizado"}

@app.delete("/api/comandos/{id_comando}", tags=["Comandos"])
def eliminar_comando(id_comando: int):
    VehiculoService.eliminar_comando(id_comando)
    return {"message": "Comando eliminado"}

# ==========================================
# 3. ESTADO E HISTORIAL (Punto 5 y 6)
# ==========================================
@app.get("/api/vehiculos/{id_vehiculo}/estado", tags=["Estado e Historial"])
def obtener_estado(id_vehiculo: int):
    res = VehiculoService.obtener_estado(id_vehiculo)
    if not res:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return res

@app.get("/api/vehiculos/{id_vehiculo}/historial", tags=["Estado e Historial"])
def obtener_historial(id_vehiculo: int):
    # Punto 6: MÁXIMO 10 movimientos más recientes
    return VehiculoService.obtener_historial(id_vehiculo, limite=10) or []

@app.post("/api/movimiento", tags=["Estado e Historial"])
async def ejecutar_movimiento(req: MovimientoIndividualRequest):
    try:
        res = VehiculoService.ejecutar_movimiento_transaccion(req.id_vehiculo, req.id_comando, req.origen)
        # Notificar por WebSocket tras confirmar transacción en RDS
        await manager.broadcast({
            "event": "MOVIMIENTO_INDIVIDUAL",
            "vehiculo": req.id_vehiculo,
            "comando": req.id_comando
        })
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 4. DEMOS Y MOVIMIENTOS DEMO
# ==========================================
@app.get("/api/vehiculos/{id_vehiculo}/demos", tags=["Demos"])
def obtener_demos(id_vehiculo: int):
    return VehiculoService.obtener_demos(id_vehiculo) or []

@app.post("/api/demos", tags=["Demos"])
def crear_demo(data: DemoCreate):
    return VehiculoService.crear_demo(data.id_vehiculo, data.nombre, data.descripcion)

@app.put("/api/demos/{id_demo}", tags=["Demos"])
def actualizar_demo(id_demo: int, data: DemoUpdate):
    VehiculoService.actualizar_demo(id_demo, data.nombre, data.descripcion)
    return {"message": "Demo actualizada"}

@app.delete("/api/demos/{id_demo}", tags=["Demos"])
def eliminar_demo(id_demo: int):
    VehiculoService.eliminar_demo(id_demo)
    return {"message": "Demo eliminada"}

@app.get("/api/demos/{id_demo}/movimientos", tags=["Demos"])
def obtener_movimientos_demo(id_demo: int):
    return VehiculoService.obtener_movimientos_demo(id_demo) or []

@app.post("/api/demos/movimientos", tags=["Demos"])
def agregar_movimiento_demo(data: MovimientoDemoCreate):
    VehiculoService.agregar_movimiento_demo(data.id_demo, data.id_comando, data.orden, data.duracion_ms, data.potencia)
    return {"message": "Movimiento agregado a la demo"}

@app.put("/api/demos/movimientos/{id_movimiento_demo}", tags=["Demos"])
def actualizar_movimiento_demo(id_movimiento_demo: int, data: MovimientoDemoUpdate):
    VehiculoService.actualizar_movimiento_demo(id_movimiento_demo, data.orden, data.duracion_ms, data.potencia)
    return {"message": "Movimiento de demo actualizado"}

@app.delete("/api/demos/movimientos/{id_movimiento_demo}", tags=["Demos"])
def eliminar_movimiento_demo(id_movimiento_demo: int):
    VehiculoService.eliminar_movimiento_demo(id_movimiento_demo)
    return {"message": "Movimiento de demo eliminado"}