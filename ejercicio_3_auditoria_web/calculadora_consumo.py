
import json
import re
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

from shared.enums.enums import TipoMaquinaria
from shared.exceptions.exception import (
    EnumValidationError,
    InfrastructureError,
    ValidationError,
)
from shared.validators.data_validator import DataValidator
from shared.validators.file_validator import FileValidator


class CalculadoraConsumoIndustrial:
    """Define una herramienta auxiliar para el cálculo adecuado del consumo en kwh
    de las maquinarias existentes en el proceso industrial"""

    def __init__(
        self,
        tipo_maquinaria: TipoMaquinaria,
        codigo_maquinaria: str,
        nombre_maquinaria: str,
        potencia_watts: float | Decimal,
        horas_dia: float,
        dias_mes: int,
        tarifa_kwh: float | Decimal,
        factor_carga: float | Decimal = 0.90,
    ) -> dict:

        self.calculadora_consumo_id: UUID = uuid4()

        self.tipo_maquinaria = DataValidator.validar_enum(
            value=tipo_maquinaria, enum_cls=TipoMaquinaria,
            field_name="tipo_maquinaria",
            allowed_subset=None
        )
        self.codigo_maquinaria = DataValidator.validar_str(
            value=codigo_maquinaria, field_name="codigo_maquinaria",
            min_length=5,
            max_length=100,
            pattern=r"^(INSPECCION_CLASIFICACION|CORTADORA_LASER|ENCADENADO|ESTACION_ENCORDADO|LAMINADORA|ESTACION_ENMARCADO_AUTOMATICO|CURADORA_SILICONA|SIMULADOR_SOLAR|PRUEBAS_ELECTROLUMINISCENCIA|ENSACADORA_ENCORDADORA)-\d+$",
            pattern_description="""El código debe iniciar con un TipoMaquinaria válido
                seguido de guion y número (Ej: ENCADENADO-001)"""
        )
        self.nombre_maquinaria = DataValidator.validar_str(
            value=nombre_maquinaria, field_name="nombre_maquinaria",
            min_length=5,
            max_length=100,
            allow_none=None,
        )
        self.potencia_watts = DataValidator.validar_numero(
            value=potencia_watts, field_name="potencia_watts",
            min_value=0.0,
            max_value=None,
            allow_float=True
        )
        self.horas_dia = DataValidator.validar_numero(
            value=horas_dia, field_name="horas_dia",
            min_value=0.0,
            max_value=None,
            allow_float=True
        )
        self.dias_mes = DataValidator.validar_numero(
            value=dias_mes, field_name="dias_mes",
            min_value=0,
            max_value=None,
            allow_float=False
        )
        self.tarifa_kwh = DataValidator.validar_numero(
            value=tarifa_kwh, field_name="tarifa_kwh",
            min_value=0.0,
            max_value=None,
            allow_float=True
        )
        self.factor_carga = DataValidator.validar_numero(
            value=factor_carga, field_name="factor_carga",
            min_value=0.0,
            max_value=None,
            allow_float=True
        )

        self.registros_consumos_kwh = []

    def calcular_consumo_kwh(self) -> dict:
        """Cálculo de kWh mensuales por equipo aplicando el factor de carga"""

        potencia_kw = float(self.potencia_watts) / 1000.0
        kwh_mensual = potencia_kw * self.horas_dia * self.dias_mes * self.factor_carga
        costo_mensual = kwh_mensual * self.tarifa_kwh

        consumo_kwh = {
            "tipo_maquinaria": self.tipo_maquinaria,
            "codigo_maquinaria": self.codigo_maquinaria,
            "nombre_maquinaria": self.nombre_maquinaria,
            "kwh_mensual": round(kwh_mensual, 2),
            "costo_mensual": round(costo_mensual, 2),
            "tarifa_kwh": self.tarifa_kwh
        }
        return consumo_kwh

    def limpiar_registro_consumo(self) -> dict:
        """Limpia registros guardados en memoria"""

        registro_consumo = self.calcular_consumo_kwh()

        for i, raw in enumerate(registro_consumo, 1):
            # Limpiar código del sensor

            tipo_maquinaria_raw = registro_consumo.get(
                "tipo_maquinaria", "Otra Máquina")
            try:
                tipo_maquinaria_limpia = DataValidator.validar_enum(
                    value=tipo_maquinaria_raw,
                    enum_cls=TipoMaquinaria,
                    field_name="tipo_maquinaria"
                )
            except (ValidationError, EnumValidationError, ValueError, TypeError):
                tipo_maquinaria_limpia = TipoMaquinaria.OTRA_MAQUINA
                        
            maquina_codigo_raw = str(registro_consumo.get("codigo_maquinaria", ""))
            coincidir_numero = re.search(r"\d+", maquina_codigo_raw)
                    
            numero_serie = int(coincidir_numero.group()) if coincidir_numero else 1
                        
            prefijo_codigo = tipo_maquinaria_limpia.value if tipo_maquinaria_limpia else "Maquinaria Desconocida"
            codigo_construido = f"{prefijo_codigo}-{numero_serie:03d}"
            try:
                codigo_maquinaria_limpia = DataValidator.validar_str(
                    value=codigo_construido,
                    field_name="codigo_maquinaria",
                    pattern=r"^[A-Za-záéíóúÁÉÍÓÚñÑ]+-\d+$",
                    pattern_description="El código debe iniciar con un TipoMaquinaria seguido de guion y número",
                    allow_none=False
                )
            except (ValidationError, ValueError, TypeError):
                codigo_maquinaria_limpia = f"MaquinariaDesconocida-{numero_serie:03d}"
                
            # Extrae y limpia nombre maquinaria
            nombre_maquinaria_raw = registro_consumo.get(
                "nombre_maquinaria", "Nombre Máquina")
            try:
                nombre_maquinaria_limpia = DataValidator.validar_str(
                    value=nombre_maquinaria_raw,
                    field_name="nombre_maquinaria"
                )
            except (ValidationError, ValueError, TypeError):
                nombre_maquinaria_limpia = "NombreDesconocido"

            # Extrae y limpia Consumo kwh Mensual
            kwh_mensual_raw = registro_consumo.get("kwh_mensual", 0.0)
            if isinstance(kwh_mensual_raw, str):
                match_temp = re.search(r"[-+]?\d*\.?\d+", kwh_mensual_raw)
                kwh_mensual_extraido = float(match_temp.group()) if match_temp else 0.0
            else:
                kwh_mensual_extraido = float(kwh_mensual_raw)
                try:
                    kwh_mensual_limpio = DataValidator.validar_numero(
                        value=kwh_mensual_extraido,
                        field_name="kwh_mensual",
                        min_value=None,
                        max_value=None,
                        allow_float=True
                    )
                except (ValidationError, ValueError, TypeError):
                    kwh_mensual_limpio = 0.0
                
            # Extrae y limpia Costo Estimado
            costo_mensual_raw = registro_consumo.get("costo_mensual", 0.0)
            if isinstance(costo_mensual_raw, str):
                match_temp = re.search(r"[-+]?\d*\.?\d+", costo_mensual_raw)
                costo_mensual_extraido = float(match_temp.group()) if match_temp else 0.0
            else:
                costo_mensual_extraido = float(costo_mensual_raw)
                try:
                    costo_mensual_limpio = DataValidator.validar_numero(
                        value=costo_mensual_extraido,
                        field_name="costo_mensual",
                        min_value=None,
                        max_value=None,
                        allow_float=True
                    )
                except (ValidationError, ValueError, TypeError):
                    costo_mensual_limpio = 0.0

            # Extrae y limpia tarifa_kwh
            tarifa_kwh_raw = registro_consumo.get("tarifa_kwh", 0.0)
            if isinstance(tarifa_kwh_raw, str):
                match_temp = re.search(r"[-+]?\d*\.?\d+", tarifa_kwh_raw)
                tarifa_kwh_extraido = float(match_temp.group()) if match_temp else 0.0
            else:
                tarifa_kwh_extraido = float(tarifa_kwh_raw)
                try:
                    tarifa_kwh_limpia = DataValidator.validar_numero(
                        value=tarifa_kwh_extraido,
                        field_name="tarifa_kwh",
                        min_value=None,
                        max_value=None,
                        allow_float=True
                    )
                except (ValidationError, ValueError, TypeError):
                    tarifa_kwh_limpia = 0.0
          
            # Retorna estrictamente el diccionario limpio
            registro_limpio = {
                "tipo_maquinaria": tipo_maquinaria_limpia,
                "codigo_maquinaria": codigo_maquinaria_limpia,
                "nombre_maquinaria": nombre_maquinaria_limpia,
                "kwh_mensual": kwh_mensual_limpio,
                "costo_mensual": costo_mensual_limpio,
                "tarifa_kwh": tarifa_kwh_limpia,
            }

        self.registros_consumos_kwh = registro_limpio

    def guardar_consumo_json(
        self, ruta_entrada: Path | str, ruta_salida: Path | str):
        """Guarda el cálculo realizado en un archivo json"""

        try:
            registros_consumos_kwh = FileValidator.validar_archivo_json(
                path=ruta_entrada,
                field_name="registros_consumos_kwh",
                allow_empty=False
            )
        except (ValidationError, InfrastructureError) as e:
            print(f"Error crítico al validar el archivo de entrada: {e}")
            return

        try:
            with open(ruta_salida, "w", encoding="utf-8") as archivo_out:
                json.dump(registros_consumos_kwh, archivo_out,
                          ensure_ascii=False, indent=4)
            print(
                f"¡Proceso exitoso! Se guardaron {len(registros_consumos_kwh)} registros limpios en '{ruta_salida}'.")
        except OSError as err:
            print(f"Error al escribir el archivo de salida: {err}")

    @staticmethod
    def calcular_consumo_total(ruta_json: Path | str) -> dict:
        """Lee el archivo json generado,
        suma el total de kWh y calcula las emisiones globales."""
            
        ruta = Path(ruta_json)
        
        if not ruta.exists():
            print(f"No se encontró el archivo de consumos en: {ruta}")
            return {"kwh_mensual": 0.0}
    
        with open(ruta, "r", encoding="utf-8") as f:
            registros_consumos_kwh = json.load(f)
    
        consumo_total_planta = sum(float(reg.get("kwh_mensual", 0.0)) for reg in registros_consumos_kwh)
    
        return {
            "consumo_global_kwh": round(consumo_total_planta, 2)
        }