import mysql.connector
from app.database import DatabaseConnection
from app.websocket_manager import manager

class VehiculoService:

    # Helper genérico para ejecutar Stored Procedures
    @staticmethod
    def _execute_sp(sp_name: str, params: list = None, fetch_one: bool = False, fetch_all: bool = False):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc(sp_name, params or [])
            result = None
            for res in cursor.stored_results():
                if fetch_one:
                    result = res.fetchone()
                elif fetch_all:
                    result = res.fetchall()
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

        # --- 1. VEHÍCULOS ---
    @classmethod
    def crear_vehiculo(cls, nombre: str, descripcion: str, ip: str, conectado: bool = False):
        cls._execute_sp("sp_crear_vehiculo", [nombre, descripcion, ip, conectado])
        return {"status": True, "message": "Vehículo creado con éxito"}

    @classmethod
    def obtener_vehiculos(cls):
        return cls._execute_sp("sp_obtener_vehiculos", fetch_all=True)

    @classmethod
    def obtener_vehiculo_por_id(cls, id_vehiculo: int):
        vehiculos = cls._execute_sp("sp_obtener_vehiculos", fetch_all=True) or []
        for v in vehiculos:
            if v.get("id_vehiculo") == id_vehiculo or v.get("id") == id_vehiculo:
                return v
        return None

    @classmethod
    def actualizar_vehiculo(cls, id_vehiculo: int, nombre: str, descripcion: str, ip: str, conectado: bool = False, activo: bool = True):
        cls._execute_sp("sp_actualizar_vehiculo", [id_vehiculo, nombre, descripcion, ip, conectado, activo])
        return {"status": True, "message": "Vehículo actualizado con éxito"}

    @classmethod
    def eliminar_vehiculo(cls, id_vehiculo: int):
        cls._execute_sp("sp_eliminar_vehiculo", [id_vehiculo])
        return {"status": True, "message": "Vehículo eliminado con éxito"}

    # --- 2. COMANDOS ---
    @classmethod
    def crear_comando(cls, id_vehiculo: int, nombre: str, codigo: str, descripcion: str):
        cls._execute_sp("sp_crear_comando", [id_vehiculo, nombre, codigo, descripcion])
        return {"status": True, "message": "Comando creado con éxito"}

    @classmethod
    def obtener_comandos_vehiculo(cls, id_vehiculo: int):
        return cls._execute_sp("sp_obtener_comandos_vehiculo", [id_vehiculo], fetch_all=True)

    @classmethod
    def actualizar_comando(cls, id_comando: int, nombre: str, codigo: str, descripcion: str):
        return cls._execute_sp("sp_actualizar_comando", [id_comando, nombre, codigo, descripcion])

    @classmethod
    def eliminar_comando(cls, id_comando: int):
        return cls._execute_sp("sp_eliminar_comando", [id_comando])

    # --- 3. ESTADO E HISTORIAL ---
    @classmethod
    def obtener_estado(cls, id_vehiculo: int):
        return cls._execute_sp("sp_obtener_estado", [id_vehiculo], fetch_one=True)

    @classmethod
    def obtener_historial(cls, id_vehiculo: int, limite: int = 10):
        # Punto 6: Devuelve como MÁXIMO sus 10 movimientos individuales más recientes
        return cls._execute_sp("sp_obtener_historial", [id_vehiculo, limite], fetch_all=True)

    # --- 4. MOVIMIENTO INDIVIDUAL (Punto 5: Transacción y Validación) ---
    @classmethod
    def ejecutar_movimiento_transaccion(cls, id_vehiculo: int, id_comando: int, origen: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()

            # 1. Validar existencia del vehículo
            cursor.callproc("sp_obtener_vehiculo", [id_vehiculo])
            vehiculo = None
            for res in cursor.stored_results():
                vehiculo = res.fetchone()
            
            if not vehiculo:
                raise ValueError("El vehículo especificado no existe o no está activo.")

            # 2. Validar que el comando pertenezca a este vehículo
            cursor.callproc("sp_obtener_comandos_vehiculo", [id_vehiculo])
            comandos = []
            for res in cursor.stored_results():
                comandos = res.fetchall()
            
            comando_valido = any(c['id_comando'] == id_comando for c in comandos)
            if not comando_valido:
                raise ValueError("El comando solicitado no pertenece a este vehículo.")

            # 3. Transacción: Actualizar Estado + Registrar Historial
            cursor.callproc("sp_actualizar_estado", [id_vehiculo, id_comando, 1])
            for res in cursor.stored_results():
                res.fetchall()

            cursor.callproc("sp_registrar_historial", [id_vehiculo, id_comando, origen])
            for res in cursor.stored_results():
                res.fetchall()

            conn.commit()
            return {"status": True, "message": "Movimiento registrado e historial actualizado en transacción"}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    # --- 5. DEMO Y MOVIMIENTOS DEMO ---
    @classmethod
    def crear_demo(cls, id_vehiculo: int, nombre: str, descripcion: str):
        cls._execute_sp("sp_crear_demo", [id_vehiculo, nombre, descripcion])
        return {"status": True, "message": "Demo creada con éxito"}

    @classmethod
    def obtener_demos(cls, id_vehiculo: int):
        return cls._execute_sp("sp_obtener_demos", [id_vehiculo], fetch_all=True)

    @classmethod
    def actualizar_demo(cls, id_demo: int, nombre: str, descripcion: str):
        return cls._execute_sp("sp_actualizar_demo", [id_demo, nombre, descripcion])

    @classmethod
    def eliminar_demo(cls, id_demo: int):
        return cls._execute_sp("sp_eliminar_demo", [id_demo])

    @classmethod
    def agregar_movimiento_demo(cls, id_demo: int, id_comando: int, orden: int, duracion_ms: int, potencia: int):
        return cls._execute_sp("sp_agregar_movimiento_demo", [id_demo, id_comando, orden, duracion_ms, potencia])

    @classmethod
    def obtener_movimientos_demo(cls, id_demo: int):
        return cls._execute_sp("sp_obtener_movimientos_demo", [id_demo], fetch_all=True)

    @classmethod
    def actualizar_movimiento_demo(cls, id_movimiento_demo: int, orden: int, duracion_ms: int, potencia: int):
        return cls._execute_sp("sp_actualizar_movimiento_demo", [id_movimiento_demo, orden, duracion_ms, potencia])

    @classmethod
    def eliminar_movimiento_demo(cls, id_movimiento_demo: int):
        return cls._execute_sp("sp_eliminar_movimiento_demo", [id_movimiento_demo])