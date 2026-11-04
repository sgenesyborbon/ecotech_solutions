
import json
from pathlib import Path
from uuid import UUID, uuid4

from ejercicio_2_productos.paneles_solares import PanelSolar
from shared.enums.enums import EtapaProducto
from shared.validators.data_validator import DataValidator


class AuditoriaHuellaCarbono:
    """Define las métricas solicitadas para el cálculo correcto de
    Huella de Carbono en el proceso industrial de EchoTechSolutions"""

    def __init__(
        self,
        consumo_kwh: float,
        factor_emision: float=0.4,
        producto: PanelSolar | None = None,
        etapa_producto: EtapaProducto | None = None,
    ):

        self.auditoria_huella_carbono_id: UUID = uuid4()

        self.producto = DataValidator.validar_clase(
            value=producto, expected_class=PanelSolar,
            field_name="producto",
            allow_none=True,
        ) if producto else None

        self.etapa_producto = DataValidator.validar_enum(
            value=etapa_producto,
            enum_cls=EtapaProducto,
            field_name="etapa_producto",
        ) if etapa_producto else None

        self.consumo_kwh = DataValidator.validar_numero(
            value=consumo_kwh, field_name="consumo_kwh",
            min_value=0.0,
            max_value=None,
            allow_float=True,
        )
        self.factor_emision = DataValidator.validar_numero(
            value=factor_emision, field_name="factor_emision",
            min_value=0.0,
            max_value=None,
            allow_float=True,
        )
    
    def calcular_emisiones_carbono(self) -> float:
        """Calcula la emisión carbono por etapa"""
        
        if self.consumo_kwh < 0.0:
            raise ValueError("El consumo en kWh no puede ser negativo.")
        calculo_emision = float(self.consumo_kwh) * float(self.factor_emision)
        emision_carbono = round(calculo_emision)

        return emision_carbono

    @staticmethod
    def obtener_metricas_consumo(
        registros_consumos_kwh: list[dict], ruta_json: Path | str) -> dict:
        """Procesa el historial de consumos de las máquinas (historial en Calculadora).
        Determina el total global de emisiones y la máquina de mayor consumo."""

        registros = registros_consumos_kwh
        if not registros and ruta_json:
            ruta = Path(ruta_json)
            if ruta.exists():
                with open(ruta, "r", encoding="utf-8") as f:
                    registros = json.load(f)
            registros = []
        if not registros:
            return {"total_emisiones": 0.0, "maquina_mayor_consumo": None, "consumo_global_kwh": 0.0, "registros": []}

        consumo_global_kwh = 0.0
        total_emisiones = 0.0
        max_consumo = -1.0
        maquina_mayor = None

        for reg in registros:
            # Extrae el consumo calculado por la calculadora
            kwh = float(reg.get("kwh_mensual", 0.0))
            nombre = reg.get("nombre_maquinaria", "Desconocida")
            
            consumo_global_kwh += kwh
            
            # Auditoría de emisiones por equipo (asumiendo un factor estándar de 0.4)
            auditor_equipo = AuditoriaHuellaCarbono(
                consumo_kwh=kwh, factor_emision=0.4)
            total_emisiones += auditor_equipo.calcular_emisiones_carbono()

            if kwh > max_consumo:
                max_consumo = kwh
                maquina_mayor = nombre

        diccionario_metricas = {
            "consumo_global_kwh": round(consumo_global_kwh, 2),
            "total_emisiones": round(total_emisiones, 2),
            "maquina_mayor_consumo": maquina_mayor,
            "registros": registros
        }

        ruta_metricas = Path("ejercicio_3_auditoria_web/metricas_sustentabilidad.json")
        with open(ruta_metricas, "w", encoding="utf-8") as f:
            json.dump(diccionario_metricas, f, ensure_ascii=False, indent=4)

        return diccionario_metricas