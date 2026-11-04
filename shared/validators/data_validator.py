# ==================
# DATA VALIDATOR
# ==================

from _collections_abc import Callable, Iterable
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Literal, TypeVar, overload
from uuid import UUID

from shared.exceptions.exception import EnumValidationError, ValidationError

T = TypeVar("T")  # Item / Lists
E = TypeVar("E", bound=StrEnum)
K = TypeVar("K")  # Key
V = TypeVar("V")  # Value
C = TypeVar("C")  # Clase


class DataValidator:
    """Validación universal de datos de entrada para modelos e inputs"""

    # ---------------------
    # VALIDACIÓN DE UUID
    # ---------------------

    @overload
    @staticmethod
    def validar_uuid(
        value: Any,
        field_name: str,
        allow_none: Literal[False] = False,
    ) -> UUID: ...

    @overload
    @staticmethod
    def validar_uuid(
        value: Any,
        field_name: str,
        allow_none: Literal[True] = True,
    ) -> UUID | None: ...

    @staticmethod
    def validar_uuid(
        value: Any,
        field_name: str,
        allow_none: bool = False,
    ) -> UUID | None:
        if value is None:
            if allow_none:
                return None
            raise ValidationError(
                f"Campo '{field_name}' no puede estar vacío",
                field_name=field_name,
                invalid_value=value,
            )

        if isinstance(value, UUID):
            return value

        if isinstance(value, str):
            try:
                return UUID(value.strip())
            except ValueError as exc:
                raise ValidationError(
                    f"Campo '{field_name}' debe ser una cadena válida tipo UUID, obtenida '{value}'.",
                    field_name=field_name,
                    invalid_value=value,
                ) from exc

        raise ValidationError(
            f"""Campo '{field_name}' debe ser una cadena válida tipo UUID,
            obtenida '{type(value).__name__}'.""",
            field_name=field_name,
            invalid_value=value,
        )

    # -------------------------------
    # VALIDACIÓN DE CADENAS - STRING
    # -------------------------------

    @overload
    @staticmethod
    def validar_str(
        value: Any,
        field_name: str,
        min_length: int = 1,
        max_length: int | None = None,
        pattern: str | None = None,
        pattern_description: str | None = None,
        transform: Callable[[str], str]
        | Literal["lower", "upper", "capitalize", "title"]
        | None = None,
        allow_none: Literal[False] = False,
    ) -> str: ...

    @overload
    @staticmethod
    def validar_str(
        value: Any,
        field_name: str,
        min_length: int = 1,
        max_length: int | None = None,
        pattern: str | None = None,
        pattern_description: str | None = None,
        transform: Callable[[str], str]
        | Literal["lower", "upper", "capitalize", "title"]
        | None = None,
        allow_none: Literal[True] = True,
    ) -> str | None: ...

    @staticmethod
    def validar_str(
        value: Any,
        field_name: str,
        min_length: int = 1,
        max_length: int | None = None,
        pattern: str | None = None,
        pattern_description: str | None = None,
        transform: Callable[[str], str]
        | Literal["lower", "upper", "capitalize", "title"]
        | None = None,
        allow_none: bool = False,
    ) -> str | None:

        # 1. Clausula para valores None o vacíos
        if value is None or value == "":
            if allow_none:
                return None
            raise ValidationError(
                f"Campo '{field_name}' no puede ser None o estar vacío",
                field_name=field_name,
                invalid_value=value,
            )

        val_str = str(value).strip()

        # 2. Formateo de cadenas str
        if transform:
            if callable(transform):
                val_str = transform(val_str)
            elif transform == "lower":
                val_str = val_str.lower()
            elif transform == "upper":
                val_str = val_str.upper()
            elif transform == "capitalize":
                val_str = val_str.capitalize()
            elif transform == "title":
                val_str = val_str.title()

        # 3. Chequeo de validación de cadena str formateada
        if len(val_str) < min_length:
            raise ValidationError(
                f"Campo '{field_name}' debe contener {min_length} caracteres.",
                field_name=field_name,
                invalid_value=value,
            )

        if max_length and len(val_str) > max_length:
            raise ValidationError(
                f"Campo '{field_name}' excede la longitud máxima de {max_length} caracteres",
                field_name=field_name,
                invalid_value=value,
            )

        if pattern:
            import re

            if not re.match(pattern, val_str):
                desc = pattern_description or f"Formato {pattern}"
                raise ValidationError(
                    f"Campo '{field_name}' formato inválido: {desc}.",
                    field_name=field_name,
                    invalid_value=value,
                )

        return val_str

    # --------------------------------------
    # VALIDACIÓN NÚMEROS ENTEROS O FLOTANTES
    # --------------------------------------

    @overload
    @staticmethod
    def validar_numero(
        value: Any,
        field_name: str,
        min_value: int | None = None,
        max_value: int | None = None,
        allow_float: Literal[False] = False,
    ) -> int: ...

    @overload
    @staticmethod
    def validar_numero(
        value: Any,
        field_name: str,
        min_value: float | None = None,
        max_value: float | None = None,
        allow_float: Literal[True] = True,
    ) -> float: ...

    @staticmethod
    def validar_numero(
        value: Any,
        field_name: str,
        min_value: float | None = None,
        max_value: float | None = None,
        allow_float: bool = True,
    ) -> float | int:
        """Valida datos del tipo numérico (int/float) y rango de valores"""

        tipo_dato = (int, float) if allow_float else int
        if not isinstance(value, tipo_dato) or isinstance(value, bool):
            raise ValidationError(
                f"""Dato '{field_name}' debe ser un número (
                {"int/float" if allow_float else "int"}).""",
                field_name=field_name,
                invalid_value=value,
            )

        if min_value is not None and value < min_value:
            raise ValidationError(
                f"Dato '{field_name}' debe ser mayor o igual a {min_value}.",
                field_name=field_name,
                invalid_value=value,
            )
        if max_value is not None and value > max_value:
            raise ValidationError(
                f"Dato '{field_name}' no puede exceder {max_value}.",
                field_name=field_name,
                invalid_value=value,
            )
        return value

    # ---------------------
    # VALIDACIÓN DECIMAL
    # ---------------------
    
    @staticmethod
    def validar_decimal(
        value: Any,
        field_name: str,
        min_value: Decimal | float | None = None,
        max_value: Decimal | float | None = None,
        max_decimal_places: int | None = None,
    ) -> Decimal:
        """Valida precisión decimal en números"""
    
        # 1. Previene que valores booleanos sean pasados como números en input
        if isinstance(value, bool):
            raise ValidationError(
                f"""Campo '{field_name}' debe ser un número decimal válido,
                    obtenido tipo bool""",
                    field_name=field_name,
                    invalid_value=value,
                )

        # 2. Convierte a decimal de manera segura
        try:
            if isinstance(value, Decimal):
                decimal_val = value
            elif isinstance(value, (int, str)):
                decimal_val = Decimal(str(value).strip())
            elif isinstance(value, float):
                # Convierte variable float a str para evitar
                # problemas de representación binarios
                decimal_val = Decimal(str(value))
            else:
                raise TypeError
        except (InvalidOperation, TypeError, ValueError) as err:
            raise ValidationError(
                f"""Campo '{field_name}' debe ser un decimal válido
                o cadena numérica""",
                field_name=field_name,
                invalid_value=value,
            ) from err

        # 3. Chequea el valor mínimo
        if min_value is not None:
            min_dec = Decimal(str(min_value))
            if decimal_val < min_dec:
                raise ValidationError(
                    f"""Campo '{field_name}' debe ser igual o mayor a {min_dec}""",
                    field_name=field_name,
                    invalid_value=value,
                )

        # 4. Chequea el valor máximo
        if max_value is not None:
            max_dec = Decimal(str(max_value))
            if decimal_val > max_dec:
                raise ValidationError(
                    f"""Campo '{field_name}' no puede exceder el valor {max_dec}""",
                    field_name=field_name,
                    invalid_value=value,
                )

        # 5. Chequeo opcional para cantidad de decimales
        if max_decimal_places is not None:
            exponent = decimal_val.as_tuple().exponent
            if isinstance(exponent, int) and exponent < 0:
                actual_decimal_places = abs(exponent)
                if actual_decimal_places > max_decimal_places:
                    raise ValidationError(
                        f"""Campo '{field_name}' no puede tener
                        más de {max_decimal_places} decimales""",
                        field_name=field_name,
                        invalid_value=value,
                    )
        return decimal_val
    
    # ---------------------
    # VALIDACIÓN DE ENUMS
    # ---------------------

    @classmethod
    def validar_enum(
        cls,
        value: Any,
        enum_cls: type[E],
        field_name: str,
        allowed_subset: Iterable[E] | None = None,
    ) -> E:
        """Valida si un valor pertenence a una clase Enum"""

        parsed_enum: E | None = None

        # 1. Convierte str o valor crudo en una instancia Enum
        if isinstance(value, enum_cls):
            parsed_enum = value
        else:
            try:
                parsed_enum = enum_cls(value)
            except (ValueError, KeyError) as exc:
                raise EnumValidationError(
                    field_name=field_name,
                    invalid_value=value,
                    enum_valido=allowed_subset if allowed_subset else enum_cls,
                ) from exc

        # 2. Si un subset específico es requerido, chequea si el enum está dentro del mismo
        if allowed_subset is not None and parsed_enum not in allowed_subset:
            raise EnumValidationError(
                field_name=field_name,
                invalid_value=value,
                enum_valido=allowed_subset,
            )
        return parsed_enum

    # ---------------------
    # VALIDACIÓN DE LISTA
    # ---------------------

    @staticmethod
    def validar_lista(
        value: Any,
        field_name: str,
        item_validator: Callable[[Any, str], T] | None = None,
        min_length: int = 0,
        max_length: int | None = None,
        allow_empty: bool = True,
    ) -> list[T] | list[Any]:
        """Valida listas, limites de longitud y aplica validación para cada item"""

        if value is None:
            if allow_empty:
                return []
            raise ValidationError(
                f"Dato '{field_name}' no puede ser Nulo.",
                field_name=field_name,
                invalid_value=value,
            )

        if not isinstance(value, (list, tuple, set)):
            raise ValidationError(
                f"""Dato '{field_name}' debe ser una lista o un iterable,
                 devuelto '{type(value).__name__}'.""",
                field_name=field_name,
                invalid_value=value,
            )
        items_list = list(value)
        if not allow_empty and len(items_list) == 0:
            raise ValidationError(
                f"Dato '{field_name}' no puede estar vacío.",
                field_name=field_name,
                invalid_value=value,
            )

        if not allow_empty and len(value) == 0:
            raise ValidationError(
                f"Dato '{field_name}' no puede ser una lista vacía",
                field_name=field_name,
                invalid_value=value,
            )

        if len(value) < min_length:
            raise ValidationError(
                f"Data '{field_name}' debe contener como mínimo {min_length} items.",
                field_name=field_name,
                invalid_value=value,
            )

        if max_length is not None and len(value) > max_length:
            raise ValidationError(
                f"Dato '{field_name}' no puede conteneter más de {max_length} items.",
                field_name=field_name,
                invalid_value=value,
            )

        # Valida elementos individuales si una lista de elementos es provista
        if item_validator:
            validated_items: list[T] = []
            for idx, item in enumerate(items_list):
                validated_items.append(item_validator(item, f"{field_name}[{idx}]"))
            return validated_items
        return items_list

    # -------------------------
    # VALIDACIÓN DE DICCIONARIO
    # -------------------------

    @staticmethod
    def validar_diccionario(
        value: Any,
        field_name: str,
        key_enum_cls: type[Any],
        value_type: type[Any] = Decimal,
        allow_empty: bool = True,
    ) -> dict[Any, Any]:
        """Valida diccionarios y aplica validación opcional para llave/valor"""

        if not isinstance(value, dict):
            raise ValidationError(
                f"""Dato '{field_name}' debe ser un diccionario.
                Devuelto '{type(value).__name__}'.""",
                field_name=field_name,
                invalid_value=value,
            )

        if not allow_empty and len(value) == 0:
            raise ValidationError(
                f"Dato '{field_name}' no puede ser un diccionario vacío",
                field_name=field_name,
                invalid_value=value,
            )

        diccionario_valido = {}
        for k, v in value.items():
            entry_field_name = f"{field_name}[{k}]"

            # 1. Validar que la llave pertenezca al Enum esperado (ej: TipoCosto)
            if not isinstance(k, key_enum_cls) and k not in [e.value for e in key_enum_cls]:
                raise ValidationError(
                    f"La llave '{k}' en '{field_name}' no es un valor válido para {key_enum_cls.__name__}.",
                    field_name=entry_field_name,
                    invalid_value=k,
                )

            # Normalizar la clave al miembro del Enum si viene como string plano
            valid_k = k if isinstance(k, key_enum_cls) else key_enum_cls(k)

            # 2. Validar el valor (ej: Decimal o conversión segura)
            try:
                if value_type == Decimal and not isinstance(v, Decimal):
                    valid_v = Decimal(str(v))
                elif not isinstance(v, value_type):
                    raise ValueError(f"Tipo esperado {value_type.__name__}")
                else:
                    valid_v = v

            except (TypeError, ValueError) as err:
                raise ValidationError(
                    f"El valor para '{k}' en '{field_name}' debe ser de tipo {value_type.__name__}.",
                    field_name=entry_field_name,
                    invalid_value=v,
                ) from err

            diccionario_valido[valid_k] = valid_v

        return diccionario_valido
    
    @staticmethod
    def validar_diccionario_anidado(
        value: Any,
        field_name: str,
        allowed_value_types: tuple[type, ...],
        allow_empty: bool = False,
    ) -> dict[str, list[Any] | tuple[Any, ...] | Any]:
        """Valida diccionarios complejos donde los valores pueden ser primitivos 
        listas o tuplas de tipos permitidos (ej: str, int, float),
        ideales para JSONField en Django."""

        if not isinstance(value, dict):
            raise ValidationError(
                f"""El campo '{field_name}' debe ser un diccionario.
                Se recibió '{type(value).__name__}'.""",
                field_name=field_name,
                invalid_value=value,
            )

        if not allow_empty and len(value) == 0:
            raise ValidationError(
                f"El campo '{field_name}' no puede estar vacío.",
                field_name=field_name,
                invalid_value=value,
            )

        diccionario_validado = {}

        for k, v in value.items():
            entry_key_name = f"{field_name}.key({k})"
            
            # 1. Validar que la clave sea estrictamente un string (para JSON/Django)
            if not isinstance(k, str) or not k.strip():
                raise ValidationError(
                    f"La clave '{k}' en '{field_name}' debe ser un texto válido.",
                    field_name=entry_key_name,
                    invalid_value=k,
                )

            # 2. Validar si el valor es una lista o tupla
            if isinstance(v, (list, tuple)):
                elementos_validados = []
                for idx, item in enumerate(v):
                    entry_item_name = f"{field_name}[{k}][{idx}]"
                    if not isinstance(item, allowed_value_types):
                        raise ValidationError(
                            f"""El elemento '{item}' en la secuencia de '{k}'
                            no coincide con los tipos permitidos:
                            {[t.__name__ for t in allowed_value_types]}.""",
                            field_name=entry_item_name,
                            invalid_value=item,
                        )
                    elementos_validados.append(item)
                diccionario_validado[k] = tuple(elementos_validados) if isinstance(
                    v, tuple) else elementos_validados
            
            elif isinstance(v, allowed_value_types):
                diccionario_validado[k] = v
            else:
                raise ValidationError(
                    f"""El valor asociado a la clave '{k}' en
                    '{field_name}' tiene un tipo no permitido.""",
                    field_name=f"{field_name}[{k}]",
                    invalid_value=v,
                )

        return diccionario_validado

    # -----------------------
    # VALIDAR CLASE/INSTANCIA
    # -----------------------

    @staticmethod
    def validar_clase(
        value: Any,
        expected_class: type[C] | tuple[type, ...],
        field_name: str,
        allow_none: bool = False,
    ) -> C:
        """Valida que una variable está compuesta por una clase o instancia"""

        if value is None:
            if allow_none:
                return value
            raise ValidationError(
                f"Dato '{field_name}' no puede ser Nulo",
                field_name=field_name,
                invalid_value=None,
            )

        if not isinstance(value, expected_class):
            # Espera el nombre de la clase de lo contrario especifica que clase espera
            if isinstance(expected_class, tuple):
                class_names = " or ".join(cls.__name__ for cls in expected_class)
            else:
                class_names = expected_class.__name__

            raise ValidationError(
                f"""Dato '{field_name}' debe ser una instancia
                de {class_names}, devuelto '{type(value).__name__}'.""",
                field_name=field_name,
                invalid_value=value,
            )
        return value
