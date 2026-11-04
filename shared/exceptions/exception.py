# ==================
# EXCEPCIONES
# ==================

from __future__ import annotations

from _collections_abc import Iterable
from enum import StrEnum
from typing import Any


class EchoTechSolutionsError(Exception):
    """Excepción personalizada para las aplicaciones de Echo Tech Solutions"""
    pass


# ----------------------
# ERRORES DE VALIDACIÓN
# ----------------------


class ValidationError(EchoTechSolutionsError):
    """Validación de datos de entrada, formato y tipo de errores de validación"""

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        invalid_value: Any = None,
    ) -> None:

        self.field_name = field_name
        self.invalid_value = invalid_value
        self.message = message
        super().__init__(self.message)


class EnumValidationError(ValidationError):
    """Error arrojado cuando una cadena de texto o valores no es un StrEnum válido"""

    def __init__(
        self,
        field_name: str,
        invalid_value: Any,
        enum_valido: type[StrEnum] | Iterable[StrEnum],
    ) -> None:

        if isinstance(enum_valido, type) and issubclass(enum_valido, StrEnum):
            valores_validos = [member.value for member in enum_valido]
        elif isinstance(enum_valido, Iterable):
            valores_validos = [
                member.value if isinstance(member, StrEnum) else str(member)
                for member in enum_valido
            ]
        else:
            valores_validos = [str(enum_valido)]

        message = (
            f"Valor inválido '{invalid_value}' para campo '{field_name}'. "
            f"Debe ser: {valores_validos}"
        )
        super().__init__(
            message=message, field_name=field_name, invalid_value=invalid_value
        )


# -----------------------
# ERRORES DE LÓGICA
# -----------------------


class LogicError(EchoTechSolutionsError):
    """Error arrojado cuando el tipo de data es válido pero viola las reglas de negocio/operaciones"""

    pass


class StockInvalidoError(LogicError):
    """Error arrojado cuando el item tiene unidades insuficientes o 
    cero unidades de stock disponibles"""

    def __init__(self, producto_id: str, codigo_producto: str, stock: int) -> None:
        self.producto_id = producto_id
        self.codigo_producto = codigo_producto
        self.stock = stock
        self.message = f"""Producto ID'{producto_id}' Código {codigo_producto}
        tiene stock inválido: {stock}. Stock no puede ser negativo"""
        super().__init__(self.message)

# -----------------------
# ERROR DE INFRAESTRUCTURA
# -----------------------


class InfrastructureError(EchoTechSolutionsError):
    """ Errores externos con base de datos o conexiones API"""

    pass
