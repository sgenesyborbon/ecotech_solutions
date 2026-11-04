import os
import sys
from pathlib import Path

os.environ["NPY_DISABLE_CPU_FEATURES"] = "AVX,AVX2,AVX512F"
raiz_proyecto = Path(__file__).resolve().parent
sys.path.append(str(raiz_proyecto))

import json
import re
from datetime import datetime as dt
from uuid import UUID, uuid4

import numpy as np

from shared.enums.enums import Categoria, TipoProducto, TipoSensor, Ubicacion
from shared.exceptions.exception import (
    EnumValidationError,
    InfrastructureError,
    ValidationError,
)
from shared.validators.data_validator import DataValidator
from shared.validators.datetime_validator import DatetimeValidator
from shared.validators.file_validator import FileValidator

# En hardware sin AVX para utilizar numpy y pandas debemos seguir esta secuencia de instalación
# - instalar visual studio tools 2022
# - instalar librerías: cython meson-python meson, ninja y versiones anteriores de numpy y pandas 
# ("numpy<2" "pandas<2.2.2" --no-build-isolation)

class Sensor:
    """Define el dispositivo utilizado como sensor para el registro de datos"""

    def __init__(
        self,
        categoria: Categoria,
        tipo_producto: TipoProducto,
        tipo_sensor: TipoSensor,
        codigo_producto: str,
        ubicacion: Ubicacion,
        dia_registro: dt,
        temperatura: float,
    ):

        self.sensor_id: UUID = DataValidator.validar_uuid(
            value=uuid4(), field_name="pub_sensor_id", allow_none=False
        ) # ID tipo UUID

        self.categoria = DataValidator.validar_enum(
            value=categoria, enum_cls=Categoria, field_name="categoria",
            allowed_subset=None
        )
        self.tipo_producto = DataValidator.validar_enum(
            value=tipo_producto, enum_cls=TipoProducto, field_name="tipo_producto",
            allowed_subset=None
        )
        self.tipo_sensor =  DataValidator.validar_enum(
            value=tipo_sensor, enum_cls=TipoSensor, field_name="tipo_sensor",
            allowed_subset=None
        )
        self.codigo_producto = DataValidator.validar_str(
            value=codigo_producto, 
            field_name="codigo_producto",
            pattern=r"^(TERMOPARES|TERMORESISTENCIAS|TERMISTORES|PIROMETROS)-\d+$",
            pattern_description="""El código debe iniciar con un TipoSensor válido
            seguido de guion y número (Ej: TERMOPARES-001)"""
        )

        self.ubicacion = DataValidator.validar_enum(
            value=ubicacion, enum_cls=Ubicacion, field_name="ubicacion",
            allowed_subset=None
        )
        self.dia_registro = DatetimeValidator.validar_datetime(
            value=dia_registro, field_name="dia_registro",
            allow_none=False,
        )

        self.temperatura = DataValidator.validar_numero(
            value=temperatura, field_name="temperatura",
            min_value=None,
            max_value=None,
            allow_float=True,
        )

        self.lista_sensores_limpios = [{}]
        self.lista_sensores_alerta = []

        self.UMBRALES_SENSORES = {
            TipoSensor.TERMOPARES: (-200.0, 2000.0),
            TipoSensor.TERMORESISTENCIAS: (-200.0, 850.0),
            TipoSensor.TERMISTORES: (-50.0, 450.0),
            TipoSensor.PIROMETROS: (-50.0, 3000.0),
            # Rango seguro por defecto
            TipoSensor.SENSOR_DESCONOCIDO: (-200.0, 3000.0),
        }

    def limpiar_registro_sensor(self, registro_raw: dict) -> dict:
        """Transforma un diccionario crudo individual en un diccionario
        estandarizado"""

        # Limpiar código del sensor
        
        categoria_raw = registro_raw.get("categoria", "Otro")
        try:
            categoria_limpia = DataValidator.validar_enum(
            value=categoria_raw,
            enum_cls=Categoria,
            field_name="categoria"
        )
        except (ValidationError, EnumValidationError, ValueError, TypeError):
            # Si falla, la limpieza interviene y asigna un valor por defecto válido
            categoria_limpia = Categoria.OTRO
        
        tipo_producto_raw = registro_raw.get("tipo_producto", "Otro")
        try:
            tipo_producto_limpio = DataValidator.validar_enum(
                value=tipo_producto_raw,
                enum_cls=TipoProducto,
                field_name="tipo_producto"
            )
        except (ValidationError, EnumValidationError, ValueError, TypeError):
            tipo_producto_limpio = TipoProducto.OTRO

        tipo_sensor_raw = registro_raw.get("tipo_sensor", "")
        try:
            tipo_sensor_limpio = DataValidator.validar_enum(
                value=tipo_sensor_raw,
                enum_cls=TipoSensor,
                field_name="tipo_sensor"
            )
        except (ValidationError, EnumValidationError, ValueError, TypeError):
            tipo_sensor_limpio = TipoSensor.SENSOR_DESCONOCIDO
        
        sensor_codigo_raw = str(registro_raw.get("codigo_producto", ""))
        coincidir_numero = re.search(r"\d+", sensor_codigo_raw)
    
        numero_serie = int(coincidir_numero.group()) if coincidir_numero else 1
        
        prefijo_sensor = tipo_sensor_limpio.value if tipo_sensor_limpio else "Sensor Desconocido"
        codigo_construido = f"{prefijo_sensor}-{numero_serie:03d}"
        try:
            sensor_codigo_limpio = DataValidator.validar_str(
                value=codigo_construido,
                field_name="codigo_producto",
                pattern=r"^[A-Za-záéíóúÁÉÍÓÚñÑ]+-\d+$",
                pattern_description="El código debe iniciar con un TipoSensor seguido de guion y número",
                allow_none=False
            )
        except (ValidationError, ValueError, TypeError):
            sensor_codigo_limpio = f"SensorDesconocido-{numero_serie:03d}"

        # Extrae y limpia temperatura numérica
        temperatura_raw = registro_raw.get("temperatura", 0.0)
        if isinstance(temperatura_raw, str):
            match_temp = re.search(r"[-+]?\d*\.?\d+", temperatura_raw)
            temperatura_extraida = float(match_temp.group()) if match_temp else 0.0
        else:
            temperatura_extraida = float(temperatura_raw)
        try:
            temperatura_limpia = DataValidator.validar_numero(
                value=temperatura_extraida,
                field_name="temperatura",
                min_value=None,
                max_value=None,
                allow_float=True
            )
        except (ValidationError, ValueError, TypeError):
            temperatura_limpia = 0.0

        # Limpia fecha de registro (con valor por defecto seguro si falta)
        dia_registro_raw = registro_raw.get("dia_registro")
        if not dia_registro_raw or str(dia_registro_raw).strip() == "":
            dia_registro_limpio = dt.now()
        else:
            try:
                dia_registro_limpio = DatetimeValidator.validar_datetime(
                    value=dia_registro_raw,
                    field_name="dia_registro",
                    allow_none=False
                )
            except (ValidationError, ValueError, TypeError):
                dia_registro_limpio = dt.now()

        # Limpia ubicación
        ubicacion_raw = registro_raw.get("ubicacion")
        if not ubicacion_raw or str(ubicacion_raw).strip() == "":
            ubicacion_limpia = Ubicacion.AREA_NO_ASIGNADA 
        else:
            try:
                ubicacion_limpia = DataValidator.validar_str(
                    value=ubicacion_raw,
                    field_name="ubicacion",
                    min_length=1,
                    transform="title"
                )
            except (ValidationError, ValueError, TypeError):
                ubicacion_limpia = Ubicacion.AREA_NO_ASIGNADA 

        # Retorna estrictamente el diccionario limpio
        registro_raw = {
            "categoria": categoria_limpia,
            "tipo_producto": tipo_producto_limpio,
            "tipo_sensor": tipo_sensor_limpio,
            "codigo_producto": sensor_codigo_limpio,
            "ubicacion": ubicacion_limpia,
            "dia_registro": dia_registro_limpio,
            "temperatura": temperatura_limpia,
        }
        return registro_raw

    def procesar_guardar_archivo(self, ruta_entrada: Path | str, ruta_salida: Path | str):
        """Lee el archivo crudo, lo procesa registro por registro y guarda un archivo nuevo"""

        try:
            registro_raw = FileValidator.validar_archivo_json(
                path=ruta_entrada,
                field_name="registro_raw",
                allow_empty=False
            )
        except (ValidationError, InfrastructureError) as e:
            print(f"Error crítico al validar el archivo de entrada: {e}")
            return

        lista_sensores_limpios = []

        for i, raw in enumerate(registro_raw, 1):
            try:
                # Llamamos a nuestra función de limpieza individual por cada elemento
                diccionario_limpio = self.limpiar_registro_sensor(raw)

                # Aseguramos serialización correcta de fechas para JSON
                if "dia_registro" in diccionario_limpio:
                    fecha = diccionario_limpio["dia_registro"]
                    if hasattr(fecha, "strftime"):
                        diccionario_limpio["dia_registro"] = fecha.strftime("%Y-%m-%d %H:%M:%S")

                lista_sensores_limpios.append(diccionario_limpio)
            except ValidationError as val_err:
                print(f"Advertencia en el registro #{i}: Dato inválido descartado -> {val_err}")

        self.lista_sensores_limpios = lista_sensores_limpios

        # Guardar en el NUEVO archivo JSON limpio (separado del impuro)
        try:
            with open(ruta_salida, "w", encoding="utf-8") as archivo_out:
                json.dump(lista_sensores_limpios, archivo_out, ensure_ascii=False, indent=4)
            print(f"¡Proceso exitoso! Se guardaron {len(lista_sensores_limpios)} registros limpios en '{ruta_salida}'.")
        except OSError as err:
            print(f"Error al escribir el archivo de salida: {err}")

    def generar_resumen_sensores(
        self,
        umbral_temperatura: dict[TipoSensor, tuple[float, float]] | None = None,
        lista_sensores_limpios: list[dict] | None = None
    ) -> tuple[list[str], float]:
        """ Genera el resumen tomando la lista limpia generada en el método
        procesar y guardar archivo"""

        # Si no se pasa una lista por argumento, usamos la que ya tiene guardada la instancia
        if lista_sensores_limpios is None:
            lista_sensores_limpios = self.lista_sensores_limpios

        # Validar que la lista no esté vacía
        if not lista_sensores_limpios or lista_sensores_limpios == [{}]:
            return [], 0.0

        # Validar el umbral de temperatura globalmente
        if umbral_temperatura is None or umbral_temperatura == "":
            umbral_temperatura = self.UMBRALES_SENSORES

        umbral_validado = DataValidator.validar_diccionario_anidado(
            value=umbral_temperatura,
            field_name="umbral_temperatura",
            allowed_value_types=(float, int),
            allow_empty=False,
        )

        temperaturas = []

        # Recorremos la lista limpia para filtrar alertas y acumular temperaturas
        for sensor in lista_sensores_limpios:
            temp = sensor.get("temperatura", 0.0)
            tipo_sensor_str = sensor.get("tipo_sensor")
            codigo = sensor.get("codigo_producto")

            temperaturas.append(temp)

            # Obtiene los límites correspondientes a este tipo de sensor
            # (Si no se encuentra, usa un rango global seguro por defecto)
            try:
                tipo_enum = TipoSensor(tipo_sensor_str)
                t_min, t_max = umbral_validado.get(tipo_enum, (-200.0, 3000.0))
            except (ValueError, TypeError):
                t_min, t_max = (-200.0, 3000.0)

            # Evalua si la temperatura viola el umbral mínimo o máximo de su categoría
            if (temp >= t_max or temp <= t_min) and codigo not in self.lista_sensores_alerta:
                self.lista_sensores_alerta.append(codigo)

        # Calcula el promedio térmico global de la planta usando NumPy de forma correcta
        prom_temperatura = float(np.average(
            temperaturas)) if temperaturas else 0.0
        
        promedio_temperatura = round(prom_temperatura)

        return self.lista_sensores_alerta, promedio_temperatura
