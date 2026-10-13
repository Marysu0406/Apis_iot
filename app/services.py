import asyncio
from app.database import DatabaseConnection
from app.websocket_manager import manager

class VehiculoService:

    @staticmethod
    def ejecutar_movimiento_individual(id_vehiculo: int, id_comando: int, origen: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            # 1. Actualizar estado
            cursor.callproc("sp_actualizar_estado", [id_vehiculo, id_comando, 1])
            for result in cursor.stored_results():
                result.fetchall()

            # 2. Registrar en historial
            cursor.callproc("sp_registrar_historial", [id_vehiculo, id_comando, origen])
            for result in cursor.stored_results():
                result.fetchall()

            conn.commit()
            return {"status": True, "message": "Movimiento individual ejecutado con éxito"}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    async def ejecutar_demo(id_demo: int, id_vehiculo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Obtener movimientos de la demo
            cursor.callproc("sp_obtener_movimientos_demo", [id_demo])
            movimientos = []
            for result in cursor.stored_results():
                movimientos = result.fetchall()
            
            ultimo_comando = None
            # 2. Transmitir N movimientos por WebSocket respetando tiempos
            for mov in movimientos:
                msg = {
                    "tipo": "DEMO_STEP",
                    "orden": mov.get("orden"),
                    "comando": mov.get("nombre_comando"),
                    "duracion_ms": mov.get("duracion_ms"),
                    "potencia": mov.get("potencia")
                }
                await manager.broadcast(msg)
                
                # Pausa según duración
                duracion_seg = mov.get("duracion_ms", 1000) / 1000.0
                await asyncio.sleep(duracion_seg)
                ultimo_comando = mov.get("id_comando")

            # 3. Actualizar estado final (REGLA: NO ejecuta sp_registrar_historial)
            if ultimo_comando:
                cursor.callproc("sp_actualizar_estado", [id_vehiculo, ultimo_comando, 1])
                conn.commit()

            return {"status": True, "message": "DEMO ejecutada exitosamente sin guardar en historial"}
        finally:
            cursor.close()
            conn.close()