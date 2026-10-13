from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.services import VehiculoService
from app.websocket_manager import manager

app = FastAPI(
    title="API IoT - Práctica 2.5",
    description="API HTTP y WebSocket con POO y Stored Procedures en AWS RDS"
)

class MovimientoRequest(BaseModel):
    id_vehiculo: int
    id_comando: int
    origen: str = "VSCODE-DEV"

class DemoRequest(BaseModel):
    id_demo: int
    id_vehiculo: int

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Servidor local API IoT activo"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/movimiento")
async def movimiento_individual(req: MovimientoRequest):
    res = VehiculoService.ejecutar_movimiento_individual(req.id_vehiculo, req.id_comando, req.origen)
    await manager.broadcast({
        "tipo": "MOVIMIENTO_INDIVIDUAL",
        "vehiculo": req.id_vehiculo,
        "comando": req.id_comando
    })
    return res

@app.post("/api/demo/ejecutar")
async def ejecutar_demo(req: DemoRequest):
    return await VehiculoService.ejecutar_demo(req.id_demo, req.id_vehiculo)