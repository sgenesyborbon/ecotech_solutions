
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from ejercicio_2_productos.dispositivos_ecologicos import DispositivoEcologico
from shared.enums.enums import Categoria, TipoProducto
from shared.validators.data_validator import DataValidator


class PanelSolar(DispositivoEcologico):
    """Define el producto Panel Solar heredado de Dispositivo Ecológico"""

    def __init__(
        self, 
        categoria: Categoria,
        tipo_producto: TipoProducto,
        codigo_producto: str, 
        nombre: str,
        descripcion: str,
        stock: int,
        fecha_produccion: date,
        fecha_garantia: date,
        degradacion_anual_max: float,
        precio_venta: Decimal, 
        potencia_max_salida: str, # reresentada como 450W
        tolerancia_positiva: str, # representada como 0/+5W
        eficiencia_max: float, # representada en porcentaje
        caracteristicas_generales: dict[str, list[str | int | float]], # Subtitulo y puntos descriptivos
        dimensiones_modulo: dict[str, tuple[str, str]], # modulo "2D": ancho x, altura x
        rendimiento_electrico: dict[str, tuple[float, float]], # debe representarse en gráfico de línea
        datos_electricos: dict[str, tuple[str, float]], #debe representarse en tabla
        datos_mecanicos: dict[str, str | int | float], # debe representarse en tabla
        datos_adicionales: dict[str, str | int | float], # debe representarse en tabla
    ):

        self.panel_solar_id: UUID = DataValidator.validar_uuid(
            value=uuid4(), field_name="panel_solar_id", allow_none=False
        )

        super().__init__(
            categoria, tipo_producto, codigo_producto, nombre, descripcion, fecha_produccion,
            fecha_garantia, degradacion_anual_max, precio_venta)

        self.potencia_max_salida = DataValidator.validar_str(
            value=potencia_max_salida, field_name="potencia_max_salida",
            min_length=2, max_length=10
        )
        self.tolerancia_positiva = DataValidator.validar_str(
            value=tolerancia_positiva, field_name="tolerancia_positiva",
            min_length=2, max_length=10
        )
        self.eficiencia_max = DataValidator.validar_numero(
            value=eficiencia_max, field_name="eficiencia_max",
            min_value=0.0, max_value=100.0, allow_float=True
        )
        self.caracteristicas_generales = DataValidator.validar_diccionario_anidado(
            value=caracteristicas_generales,
            field_name="caracteristicas_generales",
            allowed_value_types=(str, int, float)
        )
        self.dimensiones_modulo = DataValidator.validar_diccionario_anidado(
            value=dimensiones_modulo,
            field_name="dimensiones_modulo",
            allowed_value_types=(str, str)
        )
        self.rendimiento_electrico = DataValidator.validar_diccionario_anidado(
            value=rendimiento_electrico,
            field_name="rendimiento_electrico",
            allowed_value_types=(float, int)
        )
        self.datos_electricos = DataValidator.validar_diccionario_anidado(
            value=datos_electricos,
            field_name="datos_electricos",
            allowed_value_types=(str, float)
        )
        self.datos_mecanicos = DataValidator.validar_diccionario_anidado(
            value=datos_mecanicos,
            field_name="datos_mecanicos",
            allowed_value_types=(str, int, float)
        )
        self.datos_adicionales = DataValidator.validar_diccionario_anidado(
            value=datos_adicionales,
            field_name="datos_adicionales",
            allowed_value_types=(str, int, float)
        )

    def registrar_stock(self, cantidad: int):
        """Accede y modifica el stock validado usando self.stock"""

        # Sumamos al stock actual usando el getter y el setter automáticamente
        self.stock += cantidad 
        print(f"Stock actualizado. Nuevo stock: {self.stock}")

    def actualizar_registro_dispositivos(self, registro_dispositivos_raw: dict) -> dict:
        """Transforma un diccionario crudo individual en un diccionario estandarizado"""

        self.registro_dispositivos_raw = super().limpiar_registro_dispositivos({})
        self.registro_dispositivos_raw.update({
            "stock": self.stock,
            "potencia_max_salida": self.potencia_max_salida,
            "tolerancia_positiva": self.tolerancia_positiva,
            "eficiencia_max": self.eficiencia_max,
            "caracteristicas_generales": self.caracteristicas_generales,
            "dimensiones_modulo": self.dimensiones_modulo,
            "rendimiento_electrico": self.rendimiento_electrico,
            "datos_electricos": self.datos_electricos,
            "datos_mecanicos": self.datos_mecanicos,
            "datos_adicionales": self.datos_adicionales,
        })
        return self.registro_dispositivos_raw
        
    def obtener_ficha_tecnica(self) -> dict:
        """ Ficha técnica personalizada exclusiva de Panel Solar"""

        ficha_tecnica = super().obtener_ficha_tecnica()
        ficha_tecnica.update({
            "Potencia Máxima de Salida": self.potencia_max_salida,
            "Tolerancia Positiva": self.tolerancia_positiva,
            "Eficiencia Máxima": f"{self.eficiencia_max}%",
            "Características Generales": self.caracteristicas_generales,
            "Dimensiones del Módulo": self.dimensiones_modulo,
            "Rendimiento Eléctrico": self.rendimiento_electrico,
            "Datos Eléctricos": self.datos_electricos,
            "Datos Mecánicos": self.datos_mecanicos,
            "Datos Adicionales": self.datos_adicionales,
        })
        return ficha_tecnica
