# ==================
# DATETIME VALIDATOR
# ==================

from datetime import date
from datetime import datetime as dt
from enum import StrEnum
from typing import Any, Literal, TypeVar, overload

from shared.exceptions.exception import ValidationError

T = TypeVar("T")  # Item
E = TypeVar("E", bound=StrEnum)  # Enum
K = TypeVar("K")  # Key
V = TypeVar("V")  # Value
C = TypeVar("C")  # Clase / Tipo de Instancia


class DatetimeValidator:
    """Validación de datos tipo DateTime para instanciación e inputs"""

    # --------------------------------
    # VALIDACIÓN TIPO DE DATO DATETIME
    # --------------------------------

    @overload
    @staticmethod
    def validar_datetime(
        value: Any,
        field_name: str,
        allow_none: Literal[False] = False,
    ) -> dt: ...

    @overload
    @staticmethod
    def validar_datetime(
        value: Any,
        field_name: str,
        allow_none: Literal[True] = True,
    ) -> dt | None: ...

    @staticmethod
    def validar_datetime(
        value: Any,
        field_name: str,
        allow_none: bool = False,
    ) -> dt | None:
        """Valida datos tipo datetime o cadenas de fecha formateadas"""

        if value is None or value == "":
            if allow_none:
                return None
            raise ValidationError(
                f"Campo '{field_name}' no puede ser nulo o estar vacío",
                field_name=field_name,
                invalid_value=value,
            )

        if isinstance(value, str):
            try:
                return dt.fromisoformat(value.strip())
            except ValueError:
                raise ValidationError(
                    f"""Campo '{field_name}' formato ISO inválido
                    format: '{value}'. Esperado 'YYYY-MM-DDTHH:MM:SS'.""",
                    field_name=field_name,
                    invalid_value=value,
                ) from None

        if not isinstance(value, dt):
            raise ValidationError(
                f"""Campo '{field_name}' debe ser una instancia datetime o cadena de fecha formateada, obtenido: '{type(value).__name__}'.""",
                field_name=field_name,
                invalid_value=value,
            )

        return value

    # ----------------------------
    # VALIDACIÓN TIPO DE DATO DATE
    # ----------------------------

    @overload
    @staticmethod
    def validar_date(
        value: Any,
        field_name: str,
        min_date: date | None = None,
        max_date: date | None = None,
        allow_none: Literal[False] = False,
    ) -> date: ...

    @overload
    @staticmethod
    def validar_date(
        value: Any,
        field_name: str,
        min_date: date | None = None,
        max_date: date | None = None,
        allow_none: Literal[True] = True,
    ) -> date | None: ...

    @staticmethod
    def validar_date(
        value: Any,
        field_name: str,
        min_date: date | None = None,
        max_date: date | None = None,
        allow_none: bool = False,
    ) -> date | None:
        """Valida datos tipo date o cadenas de fecha formateadas"""

        if value is None or value == "":
            if allow_none:
                return None
            raise ValidationError(
                f"Campo '{field_name}' no puede ser nulo o estar vacío",
                field_name=field_name,
                invalid_value=value,
            )

        validated_date: date

        if isinstance(value, str):
            try:
                validated_date = date.fromisoformat(value.strip())
            except ValueError:
                raise ValidationError(
                    f"""Campo '{field_name}' tiene un formato de fecha inválido: '{value}'.
                    Formato esperado 'YYYY-MM-DD'.""",
                    field_name=field_name,
                    invalid_value=value,
                ) from None
        elif isinstance(value, dt):
            validated_date = value.date()
        elif isinstance(value, date):
            validated_date = value
        else:
            raise ValidationError(
                f"""Campo '{field_name}' debe ser una instancia datetime.date
                o cadena de fecha formateada, obtenido: '{type(value).__name__}'.""",
                field_name=field_name,
                invalid_value=value,
            )

        if min_date and validated_date < min_date:
            raise ValidationError(
                f"""Campo '{field_name}' ({validated_date}) no puede ser anterior
                a {min_date}.""",
                field_name=field_name,
                invalid_value=value,
            )

        if max_date and validated_date > max_date:
            raise ValidationError(
                f"""Campo '{field_name}' ({validated_date}) no puede ser posterior
                a {max_date}.""",
                field_name=field_name,
                invalid_value=value,
            )
        return validated_date
