
from decimal import Decimal
from uuid import UUID, uuid4

from shared.enums.enums import Categoria, TipoCosto, TipoProducto
from shared.validators.data_validator import DataValidator


class PrecioProducto:
    """Calcula el costo de producción total y determina el precio de venta basado en márgenes"""

    def __init__(
        self,
        categoria: Categoria,
        tipo_producto: TipoProducto,
        codigo_producto: str,
        estructura_costos: dict[TipoCosto, Decimal],
        margen_ganancia: Decimal,
    ) -> None:

        self.precio_producto_id: UUID = DataValidator.validar_uuid(
            value=uuid4(), field_name="precio_producto_id", allow_none=False
        ) # ID tipo UUID

        self.categoria = DataValidator.validar_enum(
            value=categoria, enum_cls=Categoria, field_name="categoria",
            allowed_subset=None
        )
        self.tipo_producto = DataValidator.validar_enum(
            value=tipo_producto, enum_cls=TipoProducto, field_name="tipo_producto",
            allowed_subset=None
        )
        self.codigo_producto = DataValidator.validar_str(
            value=codigo_producto,
            field_name="codigo_producto",
            pattern=r"^(PANEL_SOLAR|BATERIA_RECARGABLE|SISTEMA_RECICLAJE|TERMOSTATO_INTELIGENTE)-\d+$",
            pattern_description="""El código debe iniciar con un TipoProducto válido
            seguido de guion y número (Ej: PANEL_SOLAR-001)"""
        )
        
        self.estructura_costos = DataValidator.validar_diccionario(
            value=estructura_costos,
            field_name="estructura_costos",
            key_enum_cls=TipoCosto,
            value_type=Decimal,
            allow_empty=True,
        )
        self.margen_ganancia = DataValidator.validar_decimal(
            margen_ganancia, field_name="margen_ganancia",
            min_value=Decimal("0.00"),
            max_value=Decimal("200.00"),
            max_decimal_places=2,
        )

    def calcular_costo_total(self) -> Decimal:
        """Suma todos los componentes de costos empresariales asociados al diccionario"""

        total = Decimal("0.0")
        for tipo, valor in self.estructura_costos.items():
            total += DataValidator.validar_decimal(valor, field_name=f"costo_{self.tipo_producto.value}_{tipo.value}",)
        return total

    def calcular_precio_venta(self) -> Decimal:
        """Determina el precio final para el cliente aplicando el margen
        de ganancia sobre el costo total"""

        costo_total = self.calcular_costo_total()
        factor_ganancia = Decimal("1.0") + (self.margen_ganancia / Decimal("100.0"))
        # Redondeamos a 2 decimales comerciales
        return (costo_total * factor_ganancia).quantize(Decimal("0.01"))